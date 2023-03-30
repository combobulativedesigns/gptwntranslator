
import re
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
    summary_cost_per_token = 0.002

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

def japanese_token_limit_worst_case(N, worst_case_ratio=1.125, safety_factor=0.8):
    """
    Calculate the token limit for a Japanese text so that the combined token count
    of the Japanese text and its English translation does not exceed N in the worst-case scenario.

    Args:
        N (int): The maximum combined token count.
        worst_case_ratio (float, optional): The worst-case ratio between Japanese token count and English translation token count. Defaults to 3.
        safety_factor (float, optional): The safety factor to avoid exceeding the limit in worst-case scenarios. Defaults to 0.8.

    Returns:
        int: The token limit for the Japanese text.
    """
    token_limit = N * safety_factor / (1 + worst_case_ratio)
    return int(token_limit)

def _greedy_find_max_optimal_configuration(line_token_counts):
    total_lines = len(line_token_counts)

    models = dict()
    # models["gpt-4"] = {
    #     "name" : "gpt-4",
    #     "cost_per_token" : 0.03,
    #     "max_tokens" : 8000,
    # }
    models["gpt-3.5-turbo"] = {
        "name" : "gpt-3.5-turbo",
        "cost_per_token" : 0.002,
        "max_tokens" : 4000,
    }

    min_cost = float('inf')
    best_combination = None

    try:
        term_model = models['gpt-4']
    except KeyError:
        term_model = models['gpt-3.5-turbo']
    term_model_limit = japanese_token_limit_worst_case(term_model["max_tokens"])
    # reduce limit to nearest multiple of 4
    term_model_limit = term_model_limit - (term_model_limit % 4)

    for translation_model in models.values():
        translation_model_limit = japanese_token_limit_worst_case(translation_model
        ["max_tokens"])
        translation_model_limit = translation_model_limit - (translation_model_limit % 4)
        for summary_model in models.values():
            summary_model_limit = japanese_token_limit_worst_case(summary_model["max_tokens"])
            summary_model_limit = summary_model_limit - (summary_model_limit % 4)
            for term_division in range(term_model_limit // 1, term_model_limit // 2, -4):
                for translation_division in range(translation_model_limit // 1, translation_model_limit // 2, -4):
                    if term_division % translation_division == 0:
                        term_chunks = _estimate_chunks(total_lines, term_division, line_token_counts)
                        translation_chunks = term_chunks * _estimate_chunks(term_division, translation_division, line_token_counts)
                        summary_chunks = _estimate_chunks(translation_chunks * translation_division, translation_division, line_token_counts)

                        term_cost = term_chunks * term_division * term_model["cost_per_token"]
                        translation_cost = translation_chunks * translation_division * translation_model["cost_per_token"]
                        summary_cost = summary_chunks * translation_division * summary_model["cost_per_token"]

                        total_cost = term_cost + translation_cost + summary_cost

                        if total_cost < min_cost:
                            min_cost = total_cost
                            best_combination = (term_division, translation_division, term_model['name'], translation_model['name'], summary_model['name'])
    return best_combination

# def _greedy_find_max_optimal_configuration(line_token_counts):
#     total_lines = len(line_token_counts)

#     models = dict()
#     models["gpt-4"] = {
#         "name" : "gpt-4",
#         "cost_per_token" : 0.03,
#         "max_tokens" : 8000,
#     }
#     models["gpt-3.5-turbo"] = {
#         "name" : "gpt-3.5-turbo",
#         "cost_per_token" : 0.002,
#         "max_tokens" : 4000,
#     }

#     min_cost = float('inf')
#     best_combination = None

#     try:
#         term_model = models['gpt-4']
#     except KeyError:
#         term_model = models['gpt-3.5-turbo']
#     term_model_limit = japanese_token_limit_worst_case(term_model["max_tokens"])
#     # reduce limit to nearest multiple of 4
#     term_model_limit = term_model_limit - (term_model_limit % 4)

#     for translation_model in models.values():
#         translation_model_limit = japanese_token_limit_worst_case(translation_model
#         ["max_tokens"])
#         translation_model_limit = translation_model_limit - (translation_model_limit % 4)
#         for summary_model in models.values():
#             summary_model_limit = japanese_token_limit_worst_case(summary_model["max_tokens"])
#             summary_model_limit = summary_model_limit - (summary_model_limit % 4)
#             for term_division in range(term_model_limit // 2, term_model_limit // 4, -4):
#                 for summary_division in range(summary_model_limit // 2, summary_model_limit // 4, -4):
#                     for translation_division in range(translation_model_limit // 2, translation_model_limit // 4, -4):
#                         factors = _factors(min(term_division, summary_division))
#                         if summary_division == translation_division and translation_division in factors:
#                             term_chunks = _estimate_chunks(total_lines, term_division, line_token_counts)
#                             translation_chunks = term_chunks * _estimate_chunks(term_division, translation_division, line_token_counts)
#                             summary_chunks = _estimate_chunks(translation_chunks * translation_division, summary_division, line_token_counts)

#                             term_cost = term_chunks * term_division * term_model["cost_per_token"]
#                             translation_cost = translation_chunks * translation_division * translation_model["cost_per_token"]
#                             summary_cost = summary_chunks * summary_division * summary_model["cost_per_token"]

#                             total_cost = term_cost + translation_cost + summary_cost

#                             if total_cost < min_cost:
#                                 min_cost = total_cost
#                                 best_combination = (term_division, translation_division, summary_division, term_model['name'], translation_model['name'], summary_model['name'])
#     print(best_combination)
#     text = input()
#     return best_combination

def _calculate_line_token_counts(text):
    lines = text.splitlines()
    line_token_counts = [get_line_token_count(line) for line in lines]

    return line_token_counts

def _perform_relevant_terms_action(chunks, model):
    # Call the API to perform the relevant terms action on each chunk
    if not isinstance(chunks, list):
        raise JpToEnTranslatorException("Chunks must be a list of Chunk objects")

    terms_list = None
    for chunk in chunks:
        messages = [
                {"role": "system", "content": "You are a Japanese to English translator that creates list of proper nouns and other relevant terms in a given japanese text."},
                {"role": "system", "name": "example_user", "content": "Generate a term list for the text I'm about to provide. Mantain japanese web novel translation format convetions. Follow the format \"- japanese_term (rōmaji_for_japanese_term) - english_term\""},
                {"role": "system", "name": "example_assistant", "content": "Understood. Please provide the text."},
                {"role": "user", "content": chunk.contents}
        ]

        try:
            print()
            print(messages)
            response = call_api(messages, model)
            response = response['choices'][0]['message']['content']
            print(response)
        except OpenAI_APIException as e:
            raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
        except Exception as e:
            raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
        
        if isinstance(terms_list, TermSheet):
            old_terms = terms_list.__str__()
        else:
            old_terms = ''

        new_term_list = TermSheet(response, old_terms=old_terms, current_chunk=chunk.contents)

        terms_list = new_term_list

    return terms_list

def _perform_translation_action(chunk, term_lists, summary, translation_model):
    # Call the API to perform the translation action on each chunk using the term lists and summary
    if not isinstance(chunk, Chunk):
        raise JpToEnTranslatorException("Chunk must be a Chunk object")
    if not isinstance(term_lists, TermSheet):
        raise JpToEnTranslatorException("Term lists must be a TermSheet object")

    messages = [
        {"role": "system", "content": "You are a Japanese to English translator that translates a given japanese text."},
        {"role": "system", "name": "example_user", "content": "Translate the chunk of text I'm about to provide. Mantain japanese web novel translation format convetions. As context, I'll provide the immediate previous line of the text, the immediate next line of the text, the summary of the text so far, and a list of relevant terms and their translations to use. Do not repeat the japanese text before the translation, nor clarify your actions."},
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
    messages.append({"role": "user", "content": chunk.contents})

    try:
        print()
        print(messages)
        response = call_api(messages, model=translation_model)
        response = response['choices'][0]['message']['content']
        print(response)
    except OpenAI_APIException as e:
        raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
    except Exception as e:
        raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
        
    return response

def _perform_summary_action(translated_chunk, previous_summary, summarization_model):
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
        print()
        print(messages)
        response = call_api(messages, model=summarization_model)
        response = response['choices'][0]['message']['content']
        print(response)
    except OpenAI_APIException as e:
        raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
    except Exception as e:
        raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
    
    return response

def _perform_translation_and_summarization_action(chunks, term_lists, summary, translation_model, summarization_model):
    if not isinstance(chunks, list):
        raise JpToEnTranslatorException("Chunks must be a list of Chunk objects")
    if not isinstance(term_lists, TermSheet):
        raise JpToEnTranslatorException("Term lists must be a TermSheet object")
    
    updated_summary = summary
    translated_chunks = []
    for chunk in chunks:
        translated_chunk = _perform_translation_action(chunk, term_lists, updated_summary, translation_model)
        updated_summary = _perform_summary_action(translated_chunk, updated_summary, summarization_model)
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
    
    prev_line = prev_sub_chapter.contents.splitlines()[-1] if prev_sub_chapter else ""
    next_line = next_sub_chapter.contents.splitlines()[0] if next_sub_chapter else ""
    prev_summary = prev_sub_chapter.summary if prev_sub_chapter else ""

    line_token_counts = _calculate_line_token_counts(sub_chapter.contents)
    term_division, translation_division, term_model, translation_model, summary_model = _greedy_find_max_optimal_configuration(line_token_counts)

    # Perform the relevant terms action
    terms_chunks = _split_text_into_chunks(sub_chapter.contents, term_division, line_token_counts)
    terms_chunks_objects = list()
    for i, chunk in enumerate(terms_chunks):
        chunk_prev_line = prev_line if i == 0 else terms_chunks[i - 1].splitlines()[-1]
        chunk_next_line = next_line if i == len(terms_chunks) - 1 else terms_chunks[i + 1].splitlines()[0]

        terms_chunks_objects.append(Chunk(
            i,
            chapter_index,
            sub_chapter_index,
            chunk,
            "",
            chunk_prev_line,
            chunk_next_line))
    terms_list = _perform_relevant_terms_action(terms_chunks_objects, term_model)

    new_summary = None
    translation_chunks = []
    for i, term_chunk in enumerate(terms_chunks):
        sub_chunks = _split_text_into_chunks(term_chunk, translation_division, line_token_counts)
        sub_chunk_objects = list()
        for j, chunk in enumerate(sub_chunks):
            chunk_prev_line = prev_line if j == 0 else sub_chunks[j - 1].splitlines()[-1]
            chunk_next_line = next_line if j == len(sub_chunks) - 1 else sub_chunks[j + 1].splitlines()[0]

            sub_chunk_objects.append(Chunk(
                j,
                chapter_index,
                sub_chapter_index,
                chunk,
                "",
                chunk_prev_line,
                chunk_next_line))
        translated_sub_chunks, new_summary = _perform_translation_and_summarization_action(sub_chunk_objects, terms_list, prev_summary, translation_model, summary_model)
        translation_chunks.extend(translated_sub_chunks)

    sub_chapter.translation = '\n'.join(translation_chunks)
    sub_chapter.summary = new_summary

def fix_linebreaks(translated_text, original_text):
    def count_sentences(text):
        return len(re.findall(r'[。！？]', text))

    original_lines = original_text.split("\n")
    original_lines = [line.strip() for line in original_lines if line.strip()]
    translated_sentences = re.split(r'(?<=[.!?])\s+', translated_text)
    translated_sentences = [sentence.strip() for sentence in translated_sentences if sentence.strip()]

    fixed_translation = []
    
    for original_line in original_lines:
        num_sentences = count_sentences(original_line)
        current_line = []

        for _ in range(num_sentences):
            if translated_sentences:
                current_line.append(translated_sentences.pop(0))
            else:
                break

        fixed_translation.append(" ".join(current_line))

    # Add any remaining sentences, just in case
    if translated_sentences:
        fixed_translation.append(" ".join(translated_sentences))

    fixed_translation = "\n".join([line.strip() for line in fixed_translation if line.strip()])

    return fixed_translation





