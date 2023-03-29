
from src.gpt_wn_translator.api.openai_api import OpenAI_APIException, call_api, get_line_token_count
from src.gpt_wn_translator.models.chunk import Chunk
from src.gpt_wn_translator.models.term_sheet import TermSheet

class JpToEnTranslatorException(Exception):
    pass

def _split_text_into_chunks(text, division_size, line_token_counts):
    chunks = []
    current_chunk = []
    current_tokens = 0

    for line, token_count in zip(text.splitlines(), line_token_counts):
        if current_tokens + token_count <= division_size:
            current_chunk.append(line)
            current_tokens += token_count
        else:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_tokens = token_count

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

def _estimate_costs(line_token_counts):
    # Estimate the costs for each action based on the line token counts
    # You can customize these costs based on your API's pricing

    term_cost_per_token = 0.03
    translation_cost_per_token = 0.002
    summary_cost_per_token = 0.03

    return term_cost_per_token, translation_cost_per_token, summary_cost_per_token

def _factors(number):
    # Calculate the factors of a given number
    result = set()
    for i in range(1, int(number ** 0.5) + 1):
        div, mod = divmod(number, i)
        if mod == 0:
            result |= {i, div}
    return sorted(result)

def _estimate_chunks(total_lines, division_size, line_token_counts):
    chunks = _split_text_into_chunks('\n'.join([''] * total_lines), division_size, line_token_counts)
    return len(chunks)

def _greedy_find_optimal_configuration(line_token_counts):
    term_cost_per_token, translation_cost_per_token, summary_cost_per_token = _estimate_costs(line_token_counts)
    total_lines = len(line_token_counts)

    min_cost = float('inf')
    best_combination = None

    for term_division in range(8000 // 2, 4000 // 2, -4000 // 2):
        for summary_division in range(8000 // 2, 4000 // 2, -4000 // 2):
            for translation_division in _factors(min(term_division, summary_division)):
                if summary_division == translation_division:
                    term_chunks = _estimate_chunks(total_lines, term_division, line_token_counts)
                    translation_chunks = term_chunks * _estimate_chunks(term_division, translation_division, line_token_counts)
                    summary_chunks = _estimate_chunks(translation_chunks * translation_division, summary_division, line_token_counts)

                    term_cost = term_chunks * term_division * term_cost_per_token
                    translation_cost = translation_chunks * translation_division * translation_cost_per_token
                    summary_cost = summary_chunks * summary_division * summary_cost_per_token

                    total_cost = term_cost + translation_cost + summary_cost

                    if total_cost < min_cost:
                        min_cost = total_cost
                        best_combination = (term_division, translation_division, summary_division)

    return best_combination

def _calculate_line_token_counts(text):
    lines = text.splitlines()
    line_token_counts = [get_line_token_count(line) for line in lines]

    return line_token_counts

def _perform_relevant_terms_action(chunks):
    # Call the API to perform the relevant terms action on each chunk
    if not isinstance(chunks, list(Chunk)):
        raise JpToEnTranslatorException("Chunks must be a list of Chunk objects")

    terms_list = None
    for chunk in chunks:
        messages = [
                {"role": "system", "content": "You are a Japanese to English translator that creates list of proper nouns and other relevant terms in a given japanese text."},
                {"role": "system", "name": "example_user", "content": "Generate a term list for the text I'm about to provide. Mantain japanese web novel translation format convetions. Follow the format \"- japanese_term (rōmaji_for_japanese_term) - english_term\""},
                {"role": "system", "name": "example_assistant", "content": "Understood. Please provide the text."},
                {"role": "user", "content": chunk.content}
        ]

        try:
            response = call_api(messages)
            response = response['choices'][0]['message']['content']
        except OpenAI_APIException as e:
            raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
        except Exception as e:
            raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
        
        if isinstance(terms_list, TermSheet):
            old_terms = terms_list.__str__()
        else:
            old_terms = ''

        new_term_list = TermSheet(response, old_terms=old_terms, current_chunk=chunk.content)

        terms_list = new_term_list

    return terms_list

def _perform_translation_action(chunk, term_lists, summary):
    # Call the API to perform the translation action on each chunk using the term lists and summary
    if not isinstance(chunk, Chunk):
        raise JpToEnTranslatorException("Chunk must be a Chunk object")
    if not isinstance(term_lists, TermSheet):
        raise JpToEnTranslatorException("Term lists must be a TermSheet object")

    messages = [
        {"role": "system", "content": "You are a Japanese to English translator that translates a given japanese text."},
        {"role": "system", "name": "example_user", "content": "Translate the chunk of text I'm about to provide. Mantain japanese web novel translation format convetions. As context, I'll provide the immediate previous line of the text, the immediate next line of the text, the summary of the text so far, and a list of relevant terms and their translations to use."},
        {"role": "system", "name": "example_assistant", "content": "Understood. Please provide the previous line."}
    ]

    if chunk.prev_line:
        messages.append({"role": "system", "name": "example_user", "content": chunk.prev_line})
        messages.append({"role": "system", "name": "example_assistant", "content": "Understood. Please provide the next line."})
    else:
        messages.append({"role": "system", "name": "example_user", "content": ""})
        messages.append({"role": "system", "name": "example_assistant", "content": "No previous line provided. The text is the first line of the text. Please provide the next line."})

    if chunk.next_line:
        messages.append({"role": "system", "name": "example_user", "content": chunk.next_line})
        messages.append({"role": "system", "name": "example_assistant", "content": "Understood. Please provide the summary."})
    else:
        messages.append({"role": "system", "name": "example_user", "content": ""})
        messages.append({"role": "system", "name": "example_assistant", "content": "No next line provided. The text is the last line of the text. Please provide the summary."})

    if summary:
        messages.append({"role": "system", "name": "example_user", "content": summary})
        messages.append({"role": "system", "name": "example_assistant", "content": "Understood. Please provide the relevant terms."})
    else:
        messages.append({"role": "system", "name": "example_user", "content": ""})
        messages.append({"role": "system", "name": "example_assistant", "content": "No summary provided. The text is the first line of the text. Please provide the relevant terms."})

    messages.append({"role": "system", "name": "example_user", "content": term_lists.for_api()})
    messages.append({"role": "system", "name": "example_assistant", "content": "Understood. Please provide the text."})
    messages.append({"role": "user", "content": chunk})

    try:
        response = call_api(messages)
        response = response['choices'][0]['message']['content']
    except OpenAI_APIException as e:
        raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
    except Exception as e:
        raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
        
    return response

def _perform_summary_action(translated_chunk, previous_summary):
    # Call the API to perform the summary action on the translated_chunks and update the previous_summary
    if not isinstance(translated_chunk, str):
        raise JpToEnTranslatorException("Translated chunk must be a string")


    messages = [
        {"role": "system", "content": "You are an assistant that updates a concise summary, no longer that a few sentences, of an ongoing novel so it stays relevant for new releases, while removing content not relevant to the current story arc."},
        {"role": "system", "name": "example_user", "content": "I'll provide you with the current summary."},
        {"role": "system", "name": "example_assistant", "content": "Understood. Please provide the current summary."}
    ]

    if previous_summary:
        messages.append({"role": "system", "name": "example_user", "content": previous_summary})
        messages.append({"role": "system", "name": "example_assistant", "content": "Understood. Please provide the text."})
    else:
        messages.append({"role": "system", "name": "example_user", "content": ""})
        messages.append({"role": "system", "name": "example_assistant", "content": "No summary provided. The text is the first line of the text. Please provide the text."})

    messages.append({"role": "user", "content": translated_chunk})

    try:
        response = call_api(messages)
        response = response['choices'][0]['message']['content']
    except OpenAI_APIException as e:
        raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
    except Exception as e:
        raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
    
    return response

def _perform_translation_and_summarization_action(chunks, term_lists, summary):
    if not isinstance(chunks, list(Chunk)):
        raise JpToEnTranslatorException("Chunks must be a list of Chunk objects")
    if not isinstance(term_lists, TermSheet):
        raise JpToEnTranslatorException("Term lists must be a TermSheet object")
    
    updated_summary = summary
    translated_chunks = []
    for chunk in chunks:
        translated_chunk = _perform_translation_action(chunk, term_lists, updated_summary)
        updated_summary = _perform_summary_action(translated_chunk, updated_summary)
        translated_chunks.append(translated_chunk)
    
    return translated_chunks, updated_summary
    


def _get_sub_chapter_context(novel, chapter_index, sub_chapter_index):
    # Get the context of the sub chapter at the given index

    try:
        chapter = novel.chapters[chapter_index]
        sub_chapter = chapter.sub_chapters[sub_chapter_index]
    except IndexError:
        raise JpToEnTranslatorException("Invalid chapter or sub chapter index")


    if sub_chapter_index == 0:
        if chapter_index == 0:
            prev_sub_chapter = None
        else:
            prev_sub_chapter = novel.chapters[chapter_index - 1].sub_chapters[-1]
    else:
        prev_sub_chapter = chapter.sub_chapters[sub_chapter_index - 1]

    if sub_chapter_index == len(chapter.sub_chapters) - 1:
        if chapter_index == len(novel.chapters) - 1:
            next_sub_chapter = None
        else:
            next_sub_chapter = novel.chapters[chapter_index + 1].sub_chapters[0]
    else:
        next_sub_chapter = chapter.sub_chapters[sub_chapter_index + 1]

    return prev_sub_chapter, next_sub_chapter

def translate_sub_chapter(novel, chapter_index, sub_chapter_index):
    # Translate the sub chapter at the given index

    try:
        chapter = novel.chapters[chapter_index]
        sub_chapter = chapter.sub_chapters[sub_chapter_index]

        prev_sub_chapter, next_sub_chapter = _get_sub_chapter_context(novel, chapter_index, sub_chapter_index)
    except IndexError:
        raise JpToEnTranslatorException("Invalid chapter or sub chapter index")
    
    prev_line = prev_sub_chapter.contents if prev_sub_chapter else None
    next_line = next_sub_chapter.contents if next_sub_chapter else None
    prev_summary = prev_sub_chapter.summary if prev_sub_chapter else None

    line_token_counts = _calculate_line_token_counts(sub_chapter.contents)
    term_division, translation_division, summary_division = _greedy_find_optimal_configuration(line_token_counts)

    # Perform the relevant terms action
    terms_chunks = _split_text_into_chunks(sub_chapter.contents, term_division, line_token_counts)
    terms_chunks_objects = list(Chunk)
    for i, chunk in enumerate(terms_chunks):
        chunk_prev_line = prev_line if i == 0 else terms_chunks[i - 1].contents.splitlines()[-1]
        chunk_next_line = next_line if i == len(terms_chunks) - 1 else terms_chunks[i + 1].contents.splitlines()[0]

        terms_chunks_objects.append(Chunk(
            i,
            chapter_index,
            sub_chapter_index,
            chunk,
            "",
            chunk_prev_line,
            chunk_next_line))
    terms_list = _perform_relevant_terms_action(terms_chunks_objects)

    new_summary = None
    translation_chunks = []
    for i, term_chunk in enumerate(terms_chunks):
        sub_chunks = _split_text_into_chunks(term_chunk, translation_division, line_token_counts)
        sub_chunk_objects = list(Chunk)
        for j, chunk in enumerate(sub_chunks):
            chunk_prev_line = prev_line if j == 0 else sub_chunks[j - 1].contents.splitlines()[-1]
            chunk_next_line = next_line if j == len(sub_chunks) - 1 else sub_chunks[j + 1].contents.splitlines()[0]

            sub_chunk_objects.append(Chunk(
                j,
                chapter_index,
                sub_chapter_index,
                chunk,
                "",
                chunk_prev_line,
                chunk_next_line))
        translated_sub_chunks, new_summary = _perform_translation_and_summarization_action(sub_chunk_objects, terms_list[i], prev_summary)
        translation_chunks.extend(translated_sub_chunks)

    sub_chapter.translation = '\n'.join(translation_chunks)
    sub_chapter.summary = new_summary










