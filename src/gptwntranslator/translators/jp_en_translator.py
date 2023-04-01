"""This module contains the Japanese to English translator functions"""

import re
import signal
import sys
from gptwntranslator.api.openai_api import OpenAI_APIException, call_api, get_line_token_count, validate_model
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.chunk import Chunk
from gptwntranslator.models.sub_chapter import SubChapter
from gptwntranslator.models.term_sheet import TermSheet

TERMS_MODELS = None
TRANSLATION_MODELS = None
SUMMARY_MODELS = None
AVAILABLE_MODELS = None
INITIALIZED = False

class JpToEnTranslatorException(Exception):
    """This class represents an exception raised by the Japanese to English translator."""
    pass

def initialize(available_models: dict, terms_models: list[str], translation_models: list[str], summary_models: list[str]) -> None:
    """Initialize the translator.

    Parameters
    ----------
    terms_models : list[str]
        The models to use for term extraction.
    translation_models : list[str]
        The models to use for translation.
    summary_models : list[str]
        The models to use for summarization.
    """

    # Validate the parameters
    if not isinstance(available_models, dict):
        raise TypeError("Available models must be a dictionary")
    if not all(validate_model(model) for model in available_models.values()):
        raise ValueError("Available models must be a dictionary of valid models")
    if not isinstance(terms_models, list):
        raise TypeError("Terms models must be a list")
    if not all(isinstance(terms_model, str) for terms_model in terms_models):
        raise TypeError("Terms models must be a list of strings")
    if not all(terms_model in available_models for terms_model in terms_models):
        raise ValueError("Terms models must be a list of valid models")
    if not isinstance(translation_models, list):
        raise TypeError("Translation models must be a list")
    if not all(isinstance(translation_model, str) for translation_model in translation_models):
        raise TypeError("Translation models must be a list of strings")
    if not all(translation_model in available_models for translation_model in translation_models):
        raise ValueError("Translation models must be a list of valid models")
    if not isinstance(summary_models, list):
        raise TypeError("Summary models must be a list")
    if not all(isinstance(summary_model, str) for summary_model in summary_models):
        raise TypeError("Summary models must be a list of strings")
    if not all(summary_model in available_models for summary_model in summary_models):
        raise ValueError("Summary models must be a list of valid models")
    
    # Initialize the global variables
    global TERMS_MODELS, TRANSLATION_MODELS, SUMMARY_MODELS, INITIALIZED, AVAILABLE_MODELS
    TERMS_MODELS = terms_models
    TRANSLATION_MODELS = translation_models
    SUMMARY_MODELS = summary_models
    AVAILABLE_MODELS = available_models
    INITIALIZED = True

def _get_translation_model(model: str) -> dict:
    """Get a translation model by name.
    
    Parameters
    ----------
    model : str
        The model to use for translation.
        
    Returns
    -------
    dict
        The translation model.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")
    
    # Validate the parameters
    if not isinstance(model, str):
        raise TypeError("Model must be a string")
    if model not in AVAILABLE_MODELS:
        raise ValueError("Model must be a valid model")
    
    # Get the translation model
    return AVAILABLE_MODELS[model]


def _split_text_into_chunks(text: str, division_size: int, line_token_counts: list[int]) -> list[str]:
    """Split a text into chunks of a given size.

    Parameters
    ----------
    text : str
        The text to split.
    division_size : int
        The maximum number of tokens in each chunk.
    line_token_counts : list[int]
        The token counts of each line in the text.

    Returns
    -------
    list[str]
        The chunks of the text.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate the parameters
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    if not isinstance(division_size, int):
        raise TypeError("Division size must be an integer")
    if division_size <= 0:
        raise ValueError("Division size must be greater than 0")
    if not isinstance(line_token_counts, list):
        raise TypeError("Line token counts must be a list")
    if not all(isinstance(line_token_count, int) for line_token_count in line_token_counts):
        raise TypeError("Line token counts must be a list of integers")
    if not all(line_token_count >= 0 for line_token_count in line_token_counts):
        raise ValueError("Line token counts must be a list of positive integers")
    
    # Initialize some variables
    chunks = []
    current_chunk = []
    current_tokens = 0

    # Split the text into chunks
    for line, token_count in zip(text.splitlines(), line_token_counts):
        if current_tokens + token_count <= division_size:
            current_chunk.append(line)
            current_tokens += token_count
        else:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_tokens = token_count

    # Add the last chunk
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

# def _estimate_costs(line_token_counts):
#     # Estimate the costs for each action based on the line token counts
#     # You can customize these costs based on your API's pricing

#     term_cost_per_token = 0.03
#     translation_cost_per_token = 0.002
#     summary_cost_per_token = 0.002

#     return term_cost_per_token, translation_cost_per_token, summary_cost_per_token

# def _factors(number):
#     # Calculate the factors of a given number
#     result = set()
#     for i in range(1, int(number ** 0.5) + 1):
#         div, mod = divmod(number, i)
#         if mod == 0:
#             result |= {i, div}
#     return sorted(result)

def _estimate_chunks(total_lines: int, division_size: int, line_token_counts: list[int]) -> int:
    """
    Estimate the number of chunks that will be generated for a given text.

    Parameters
    ----------
    total_lines : int
        The total number of lines in the text.
    division_size : int
        The maximum number of tokens in each chunk.
    line_token_counts : list[int]
        The token counts of each line in the text.

    Returns
    -------
    int
        The number of chunks that will be generated for the given text.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate the input
    if not isinstance(total_lines, int):
        raise TypeError("total_lines must be an integer.")
    if total_lines <= 0:
        raise ValueError("total_lines must be a positive integer.")
    if not isinstance(division_size, int):
        raise TypeError("division_size must be an integer.")
    if division_size <= 0:
        raise ValueError("division_size must be a positive integer.")
    if not isinstance(line_token_counts, list):
        raise TypeError("line_token_counts must be a list.")
    if not all(isinstance(token_count, int) for token_count in line_token_counts):
        raise TypeError("line_token_counts must be a list of integers.")
    if not all(token_count >= 0 for token_count in line_token_counts):
        raise ValueError("line_token_counts must be a list of positive integers.")
    if len(line_token_counts) != total_lines:
        raise ValueError("line_token_counts must have the same length as total_lines.")
    
    # Estimate the number of chunks
    chunks = _split_text_into_chunks('\n'.join([''] * total_lines), division_size, line_token_counts)

    return len(chunks)

def _japanese_token_limit_worst_case(N: int, worst_case_ratio: float|int=1.125, safety_factor: float|int=0.8) -> int:
    """
    Calculate the token limit for a Japanese text so that the combined token count
    of the Japanese text and its English translation does not exceed N in the worst-case scenario.

    Parameters
    ----------
    N : int
        The maximum combined token count.
    worst_case_ratio : float or int, optional
        The worst-case ratio between Japanese token count and English translation token count. Defaults to 1.125.
    safety_factor : float or int, optional
        The safety factor to avoid exceeding the limit in worst-case scenarios. Defaults to 0.8.

    Returns
    -------
    int
        The token limit for the Japanese text.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate the input
    if not isinstance(N, int):
        raise TypeError("N must be an integer.")
    if N <= 0:
        raise ValueError("N must be a positive integer.")
    if not isinstance(worst_case_ratio, float) and not isinstance(worst_case_ratio, int):
        raise TypeError("worst_case_ratio must be a float or an integer.")
    if worst_case_ratio <= 0:
        raise ValueError("worst_case_ratio must be a positive float or integer.")
    if not isinstance(safety_factor, float) and not isinstance(safety_factor, int):
        raise TypeError("safety_factor must be a float or an integer.")
    if safety_factor <= 0:
        raise ValueError("safety_factor must be a positive float or integer.")
    
    # Calculate the token limit
    token_limit = N * safety_factor / (1 + worst_case_ratio)
    token_limit = int(token_limit)

    return token_limit

def _greedy_find_max_optimal_configuration(line_token_counts: list[int]) -> tuple[int, int, str, str, str]:
    """Calculate the optimal configuration for the Japanese to English translator. Configuration is calculated by minimizing the total cost of the translation.

    Parameters
    ----------
    line_token_counts : list[int]
        The token counts of each line in the Japanese text.
    
    Returns
    -------
    tuple[int, int, str, str, str]
        The optimal configuration for the Japanese to English translator: token limit for the terms action, token limit for the translation action, terms model, translation model, summary model.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate the input
    if not isinstance(line_token_counts, list):
        raise TypeError("line_token_counts must be a list.")
    if not all(isinstance(token_count, int) for token_count in line_token_counts):
        raise TypeError("line_token_counts must be a list of integers.")
    if not all(token_count >= 0 for token_count in line_token_counts):
        raise ValueError("line_token_counts must be a list of positive integers.")

    # Initialize some values
    total_lines = len(line_token_counts)
    min_cost = float('inf')
    best_combination = None

    # Get the models to use
    terms_models = [_get_translation_model(model) for model in TERMS_MODELS]
    translation_models = [_get_translation_model(model) for model in TRANSLATION_MODELS]
    summary_models = [_get_translation_model(model) for model in SUMMARY_MODELS]

    # Iterate through all possible combinations of models and token limits
    for term_model in terms_models:
        term_model_limit = _japanese_token_limit_worst_case(term_model["max_tokens"])
        term_model_limit = term_model_limit - (term_model_limit % 4)

        for translation_model in translation_models:
            translation_model_limit = _japanese_token_limit_worst_case(translation_model["max_tokens"])
            translation_model_limit = translation_model_limit - (translation_model_limit % 4)

            for summary_model in summary_models:
                summary_model_limit = _japanese_token_limit_worst_case(summary_model["max_tokens"])
                summary_model_limit = summary_model_limit - (summary_model_limit % 4)

                for term_division in range(term_model_limit // 1, term_model_limit // 2, -4):
                    for translation_division in range(translation_model_limit // 1, translation_model_limit // 2, -4):

                        # Check if the current configuration is valid
                        if term_division % translation_division == 0:

                            # Calculate the cost of the current configuration
                            term_chunks = _estimate_chunks(total_lines, term_division, line_token_counts)
                            translation_chunks = _estimate_chunks(total_lines, translation_division, line_token_counts)
                            summary_chunks = _estimate_chunks(total_lines, summary_model_limit, line_token_counts)

                            term_cost = term_chunks * term_division * term_model["cost_per_1k_tokens"]
                            translation_cost = translation_chunks * translation_division * translation_model["cost_per_1k_tokens"]
                            summary_cost = summary_chunks * translation_division * summary_model["cost_per_1k_tokens"]

                            total_cost = term_cost + translation_cost + summary_cost

                            # Check if the current configuration is better than the best configuration so far, and update the best configuration if it is
                            if total_cost < min_cost:
                                min_cost = total_cost
                                best_combination = (term_division, translation_division, term_model['name'], translation_model['name'], summary_model['name'])

    return best_combination

def _calculate_line_token_counts(text: str) -> list[int]:
    """Calculate the number of tokens in each line of a text.

    Parameters
    ----------
    text : str
        The text to calculate the token counts for.

    Returns
    -------
    list[int]
        A list of integers representing the number of tokens in each line of the text.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate input
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    # Split the text into lines and calculate the token count for each line
    lines = text.splitlines()
    line_token_counts = [get_line_token_count(line) for line in lines]

    return line_token_counts

def _perform_relevant_terms_action(chunks: list[Chunk], model: str) -> TermSheet:
    """Call the relevant terms API and return a TermSheet object.

    Parameters
    ----------
    chunks : list[Chunk]
        A list of Chunk objects from which to extract relevant terms.
    model : str
        The model to use for the API call.

    Returns
    -------
    TermSheet
        A TermSheet object containing the relevant terms and their definitions.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate input
    available_models = [_get_translation_model(model)['name'] for model in TERMS_MODELS]
    if not isinstance(chunks, list):
        raise TypeError("Chunks must be a list")
    if not all(isinstance(chunk, Chunk) for chunk in chunks):
        raise TypeError("Chunks must be a list of Chunk objects")
    if not isinstance(model, str):
        raise TypeError("Model must be a string")
    if model not in available_models:
        raise ValueError(f"Model must be a valid model. Available models: {', '.join(available_models)}")

    # Initialize the terms list
    terms_list = None

    # Iterate over the chunks
    for chunk in chunks:
        # Build the messages list for the API call
        messages = [
                {"role": "system", "content": "You are a Japanese to English translator that creates list of proper nouns and other relevant terms in a given japanese text."},
                {"role": "system", "name": "example_user", "content": "Generate a term list for the text I'm about to provide. Mantain japanese web novel translation format convetions. Follow the format \"- japanese_term (rōmaji_for_japanese_term) - english_term\""},
                {"role": "system", "name": "example_assistant", "content": "Understood. Please provide the text."},
                {"role": "user", "content": chunk.contents}
        ]

        # Call the API
        try:
            response = call_api(messages, model)
            response = response['choices'][0]['message']['content']
        except OpenAI_APIException as e:
            raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
        except Exception as e:
            raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
        
        # Prepare the old terms list
        if isinstance(terms_list, TermSheet):
            old_terms = terms_list.__str__()
        else:
            old_terms = ''

        # Create the new terms list
        new_term_list = TermSheet(response, old_terms=old_terms, current_chunk=chunk.contents)
        terms_list = new_term_list

    return terms_list

def _perform_translation_action(chunk: Chunk, term_lists: TermSheet, summary: str, translation_model: str) -> str:
    """Call the API to perform the translation action on a chunk of text.

    Parameters
    ----------
    chunk : Chunk
        The chunk object with text to translate.
    term_lists : TermSheet
        The term sheet object with relevant terms and their translations.
    summary : str
        The summary of the text so far.
    translation_model : str
        The translation model to use.

    Returns
    -------
    str
        The translated text.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate inputs
    available_models = [_get_translation_model(model)['name'] for model in TRANSLATION_MODELS]
    if not isinstance(chunk, Chunk):
        raise TypeError("Chunk must be a Chunk object")
    if not isinstance(term_lists, TermSheet):
        raise TypeError("Term lists must be a TermSheet object")
    if not isinstance(summary, str):
        raise TypeError("Summary must be a string")
    if not isinstance(translation_model, str):
        raise TypeError("Translation model must be a string")
    if translation_model not in available_models:
        raise ValueError(f"Translation model must be a valid model. Available models: {', '.join(available_models)}")
    
    # Build the messages to send to the API
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

    # Call the API
    try:
        response = call_api(messages, model=translation_model)
        response = response['choices'][0]['message']['content']
    except OpenAI_APIException as e:
        raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
    except Exception as e:
        raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
        
    return response

def _perform_summary_action(translated_chunk: str, previous_summary: str, summarization_model: str) -> str:
    """Call the API to perform the summarization action on the translated chunk using the previous summary.	

    Parameters
    ----------
    translated_chunk : str
        The translated chunk of text to update the summary with.
    previous_summary : str
        The previous summary of the text.
    summarization_model : str
        The model to use for the summarization action.

    Returns
    -------
    str
        The updated summary.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate parameters
    available_models = [_get_translation_model(model)['name'] for model in SUMMARY_MODELS]
    if not isinstance(translated_chunk, str):
        raise TypeError("Translated chunk must be a string")
    if not isinstance(previous_summary, str):
        raise TypeError("Previous summary must be a string")
    if not isinstance(summarization_model, str):
        raise TypeError("Summarization model must be a string")
    if summarization_model not in available_models:
        raise ValueError(f"Summarization model must be a valid model. Available models: {', '.join(available_models)}")

    # Build the messages to send to the API
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

    # Call the API
    try:
        response = call_api(messages, model=summarization_model)
        response = response['choices'][0]['message']['content']
    except OpenAI_APIException as e:
        raise JpToEnTranslatorException("Error calling OpenAI API: " + str(e))
    except Exception as e:
        raise JpToEnTranslatorException("OpenAI API response is not valid: " + str(e))
    
    return response

def _perform_translation_and_summarization_action(chunks: list[Chunk], term_lists: TermSheet, summary: str, translation_model: str, summarization_model: str, verbose=False) -> tuple[list[str], str]:
    """Performs the translation and summarization actions on the provided chunks, using the provided term lists, summary, and models.

    Parameters
    ----------
    chunks : list[Chunk]
        The chunks to perform the translation and summarization actions on.
    term_lists : TermSheet
        The term lists to use for the translation action.
    summary : str
        The summary to use for the summarization action.
    translation_model : str
        The translation model to use for the translation action.
    summarization_model : str
        The summarization model to use for the summarization action.
    verbose : bool, optional
        Whether to print the progress of the translation and summarization actions, by default False

    Returns
    -------
    tuple[list[str], str]
        The translated chunks and updated summary.
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate the provided arguments
    available_translation_models = [_get_translation_model(model)['name'] for model in TRANSLATION_MODELS]
    available_summarization_models = [_get_translation_model(model)['name'] for model in SUMMARY_MODELS]
    if not isinstance(chunks, list):
        raise TypeError("Chunks must be a list of Chunk objects")
    if not all(isinstance(chunk, Chunk) for chunk in chunks):
        raise TypeError("Chunks must be a list of Chunk objects")
    if not isinstance(term_lists, TermSheet):
        raise TypeError("Term lists must be a TermSheet object")
    if not isinstance(summary, str):
        raise TypeError("Summary must be a string")
    if not isinstance(translation_model, str):
        raise TypeError("Translation model must be a string")
    if translation_model not in available_translation_models:
        raise ValueError(f"Translation model must be a valid model. Available models: {', '.join(available_translation_models)}. Value provided: {translation_model}")
    if not isinstance(summarization_model, str):
        raise TypeError("Summarization model must be a string")
    if summarization_model not in available_summarization_models:
        raise ValueError(f"Summarization model must be a valid model. Available models: {', '.join(available_summarization_models)}. Value provided: {summarization_model}")
    
    # Initialize the updated summary to the provided summary
    updated_summary = summary

    # Initialize the translated chunks list
    translated_chunks = []

    # Perform the translation and summarization actions on each chunk
    for chunk in chunks:
        try:
            translated_chunk = _perform_translation_action(chunk, term_lists, updated_summary, translation_model)
        except JpToEnTranslatorException as e:
            raise JpToEnTranslatorException(f"Error performing translation action for ({chunk}): {str(e)}")
        try:
            updated_summary = _perform_summary_action(translated_chunk, updated_summary, summarization_model)
        except JpToEnTranslatorException as e:
            raise JpToEnTranslatorException(f"Error performing summary action for ({chunk}): {str(e)}")
        translated_chunks.append(translated_chunk)
    
    return translated_chunks, updated_summary
    


def _get_sub_chapter_context(novel: Novel, chapter_index: int, sub_chapter_index: int) -> tuple[SubChapter, SubChapter]:
    """Returns the previous and next sub chapter objects for the given chapter and sub chapter indices
    
    Parameters
    ----------
    novel : Novel
        The novel object
    chapter_index : int
        The chapter index
    sub_chapter_index : int
        The sub chapter index

    Returns
    -------
    tuple[SubChapter, SubChapter]
        The previous and next sub chapter objects

    Raises
    ------
    JpToEnTranslatorException
        If the chapter or sub chapter index is invalid
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate the provided arguments
    if not isinstance(novel, Novel):
        raise TypeError("Novel must be a Novel object")
    if not isinstance(chapter_index, int):
        raise TypeError("Chapter index must be an integer")
    if not isinstance(sub_chapter_index, int):
        raise TypeError("Sub chapter index must be an integer")

    # Check if the chapter and sub chapter indices are valid
    try:
        chapter = novel.chapters[chapter_index]
        sub_chapter = chapter.sub_chapters[sub_chapter_index]
    except IndexError:
        raise JpToEnTranslatorException("Invalid chapter or sub chapter index")

    # Get the previous sub chapters
    if sub_chapter_index == 0:
        if chapter_index == 0:
            # If the sub chapter is the first sub chapter of the first chapter, there is no previous sub chapter
            prev_sub_chapter = None
        else:
            # If the sub chapter is the first sub chapter of a chapter, the previous sub chapter is the last sub chapter of the previous chapter
            prev_sub_chapter = novel.chapters[chapter_index - 1].sub_chapters[-1]
    else:
        # If the sub chapter is not the first sub chapter of a chapter, the previous sub chapter is the previous sub chapter of the same chapter
        prev_sub_chapter = chapter.sub_chapters[sub_chapter_index - 1]

    # Get the next sub chapters
    if sub_chapter_index == len(chapter.sub_chapters) - 1:
        if chapter_index == len(novel.chapters) - 1:
            # If the sub chapter is the last sub chapter of the last chapter, there is no next sub chapter
            next_sub_chapter = None
        else:
            # If the sub chapter is the last sub chapter of a chapter, the next sub chapter is the first sub chapter of the next chapter
            next_sub_chapter = novel.chapters[chapter_index + 1].sub_chapters[0]
    else:
        # If the sub chapter is not the last sub chapter of a chapter, the next sub chapter is the next sub chapter of the same chapter
        next_sub_chapter = chapter.sub_chapters[sub_chapter_index + 1]

    return prev_sub_chapter, next_sub_chapter

def translate_sub_chapter(novel: Novel, chapter_index: int, sub_chapter_index: int, verbose: bool=False) -> None:
    """Translate the sub chapter at the given indexes in the given novel

    Parameters
    ----------
    novel : Novel
        The novel to translate
    chapter_index : int
        The index of the chapter to translate
    sub_chapter_index : int
        The index of the sub chapter to translate
    verbose : bool, optional
        Whether to print the progress of the translation, by default False
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate the provided arguments
    if not isinstance(novel, Novel):
        raise TypeError("Novel must be a Novel object")
    if not isinstance(chapter_index, int):
        raise TypeError("Chapter index must be an integer")
    if not isinstance(sub_chapter_index, int):
        raise TypeError("Sub chapter index must be an integer")
    if not isinstance(verbose, bool):
        raise TypeError("Verbose must be a boolean")

    # Get the sub chapter to translate and its context
    try:
        chapter = novel.chapters[chapter_index]
        sub_chapter = chapter.sub_chapters[sub_chapter_index]

        prev_sub_chapter, next_sub_chapter = _get_sub_chapter_context(novel, chapter_index, sub_chapter_index)
    except IndexError:
        raise JpToEnTranslatorException("Invalid chapter or sub chapter index")
    
    # Get the previous and next lines and summary
    prev_line = prev_sub_chapter.contents.splitlines()[-1] if prev_sub_chapter and prev_sub_chapter.contents else ""
    next_line = next_sub_chapter.contents.splitlines()[0] if next_sub_chapter and next_sub_chapter.contents else ""
    prev_summary = prev_sub_chapter.summary if prev_sub_chapter and prev_sub_chapter.summary else ""

    # Calculate the optimal configuration for the sub chapter
    line_token_counts = _calculate_line_token_counts(sub_chapter.contents)
    term_division, translation_division, term_model, translation_model, summary_model = _greedy_find_max_optimal_configuration(line_token_counts)

    # --------------------- Terms Sheet --------------------- #

    # Split the text into chunks for the terms sheet API
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
    
    print("Terms... ", end="") if verbose else None
    sys.stdout.flush()

    try:
        # Perform the terms sheet API action
        terms_list = _perform_relevant_terms_action(terms_chunks_objects, term_model)
    except Exception as e:
        raise JpToEnTranslatorException("Error while performing terms sheet API action") from e

    # --------------------- Translation and Summary --------------------- #

    print("Translating... ", end="") if verbose else None
    sys.stdout.flush()

    # Initialize the summary and translated chunks
    new_summary = None
    translation_chunks = []

    # Split the text into chunks or sub chunks for the translation and summarization API
    for i, term_chunk in enumerate(terms_chunks):
        sub_chunks = _split_text_into_chunks(term_chunk, translation_division, line_token_counts)
        sub_chunk_objects = list()

        # Create the chunk objects for the translation and summarization API
        for j, chunk in enumerate(sub_chunks):
            chunk_prev_line = prev_line if j == 0 else sub_chunks[j - 1].splitlines()[-1]
            chunk_next_line = next_line if j == len(sub_chunks) - 1 else sub_chunks[j + 1].splitlines()[0]

            sub_chunk_objects.append(Chunk(
                j+1,
                chapter_index+1,
                sub_chapter_index+1,
                chunk,
                "",
                chunk_prev_line,
                chunk_next_line))

        try:    
            # Perform the translation and summarization API action
            translated_sub_chunks, new_summary = _perform_translation_and_summarization_action(sub_chunk_objects, terms_list, prev_summary, translation_model, summary_model, verbose)

            # Add the translated sub chunks to the translation chunks
            translation_chunks.extend(translated_sub_chunks)
        except Exception as e:
            raise JpToEnTranslatorException("Error while performing translation and summarization API action") from e

    # Save the translation and summary to the novel object
    sub_chapter.translation = '\n'.join(translation_chunks)
    sub_chapter.summary = new_summary

def fix_linebreaks(translated_text: str, original_text: str) -> str:
    """Fixes linebreaks in the translated text to match the original text.	

    Parameters
    ----------
    translated_text : str
        The translated text
    original_text : str
        The original text

    Returns
    -------
    str
        The fixed translation
    """

    # Validate the translator has been initialized  
    if not INITIALIZED:
        raise JpToEnTranslatorException("Translator has not been initialized")

    # Validate the provided arguments
    if not isinstance(translated_text, str):
        raise TypeError("Translated text must be a string")
    if not isinstance(original_text, str):
        raise TypeError("Original text must be a string")

    def count_sentences(text: str) -> int:
        """Counts the number of sentences in the given text.

        Parameters
        ----------
        text : str
            The text to count the number of sentences in. Has to be in Japanese.
        
        Returns
        -------
        int
            The number of sentences in the given text.
        """

        return len(re.findall(r'[。！？]', text))

    # Split the Japanese text into lines
    original_lines = original_text.split("\n")
    # Remove empty lines
    original_lines = [line.strip() for line in original_lines if line.strip()]

    # Split the translated text into sentences
    translated_sentences = re.split(r'(?<=[.!?])\s+', translated_text)
    # Remove empty sentences
    translated_sentences = [sentence.strip() for sentence in translated_sentences if sentence.strip()]

    # Initialize the fixed translation
    fixed_translation = []
    
    # Iterate over the lines in the original text
    for original_line in original_lines:
        # Count the number of sentences in the current line
        num_sentences = count_sentences(original_line)

        # Initialize the current line
        current_line = []

        # Add the same number of sentences to the current line from the translated text to match the original text
        for _ in range(num_sentences):
            # If there are no more sentences to add, break
            if translated_sentences:
                current_line.append(translated_sentences.pop(0))
            else:
                break
        
        # Add the current line to the fixed translation
        fixed_translation.append(" ".join(current_line))

    # Add any remaining sentences, just in case
    if translated_sentences:
        fixed_translation.append(" ".join(translated_sentences))

    # Remove empty lines and join the fixed translation
    fixed_translation = "\n".join([line.strip() for line in fixed_translation if line.strip()])

    return fixed_translation





