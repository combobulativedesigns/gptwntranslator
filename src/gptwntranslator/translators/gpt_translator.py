"""This module contains the Japanese to English translator functions"""

import openai
from yattag import Doc
import xml.etree.ElementTree as ET

from gptwntranslator.api.openai_api import call_api, get_line_token_count, validate_model
from gptwntranslator.helpers.api_helper import APICallQueue
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.data_helper import get_targeted_sub_chapters
from gptwntranslator.helpers.design_patterns_helper import singleton
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.chunk import Chunk
from gptwntranslator.models.sub_chapter import SubChapter
from gptwntranslator.models.term_sheet import TermSheet


class GPTTranslatorException(Exception):
    pass

class GPTTranslatorAPIException(GPTTranslatorException):
    pass

class GPTTranslatorAPIRetryableException(GPTTranslatorAPIException):
    pass

class GPTTranslatorAPINoRetriesException(GPTTranslatorAPIException):
    pass

class GPTTranslatorGPTFormatException(GPTTranslatorException):
    pass

class GPTTranslator:    
    def __init__(self) -> None:
        TypeError(f"'{self.__class__.__name__}' cannot be instantiated. Create a subclass instead.")
    
    def _initialize(self, available_models: dict, terms_models: list[str], translation_models: list[str], summary_models: list[str], metadata_models: list[str], original_language: str="Japanese", target_language: str="English") -> None:
        
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
        if not isinstance(metadata_models, list):
            raise TypeError("Metadata models must be a list")
        if not all(isinstance(metadata_model, str) for metadata_model in metadata_models):
            raise TypeError("Metadata models must be a list of strings")
        if not all(metadata_model in available_models for metadata_model in metadata_models):
            raise ValueError("Metadata models must be a list of valid models")
        if not isinstance(original_language, str):
            raise TypeError("Original language must be a string")
        if not isinstance(target_language, str):
            raise TypeError("Target language must be a string")
        
        self._available_models = available_models
        self._terms_models = terms_models
        self._translation_models = translation_models
        self._summary_models = summary_models
        self._metadata_models = metadata_models
        self._original_language = original_language
        self._target_language = target_language

    def set_original_language(self, original_language: str) -> None:
        # Validate the parameters
        if not isinstance(original_language, str):
            raise TypeError("Original language must be a string")
        
        cf = Config()
        if len(original_language) == 2:
            languages = [lang[1] for lang in [list(dct.items())[0] for dct in cf.data.config.languages] if lang[0] == original_language]
            if len(languages) == 1:
                original_language = languages[0]
            else:
                raise ValueError("Original language must be a valid language")
        else:
            languages = [lang[1] for lang in [list(dct.items())[0] for dct in cf.data.config.languages] if lang[1] == original_language]
            if not len(languages) == 1:
                raise ValueError("Original language must be a valid language")

        self._original_language = original_language

    def _get_api_model(self, model: str) -> dict:
        # Validate the parameters
        if not isinstance(model, str):
            raise TypeError("Model must be a string")
        if model not in self._available_models:
            raise ValueError("Model must be a valid model")
        
        # Get the translation model
        return self._available_models[model]
    
    def _split_text_into_chunks(self, text: str, division_size: int, line_token_counts: list[int]) -> list[str]:
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
    
    def _estimate_chunks(self, total_lines: int, division_size: int, line_token_counts: list[int]) -> int:
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
        chunks = self._split_text_into_chunks('\n'.join([''] * total_lines), division_size, line_token_counts)

        return len(chunks)
    
    def _original_language_token_limit_worst_case(self, N: int, worst_case_ratio: float|int=1.125, safety_factor: float|int=0.8) -> int:
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
    
    def _greedy_find_max_optimal_configuration(self, line_token_counts: list[int]) -> tuple[int, int, int, str, str, str]:
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
        terms_models = [self._get_api_model(model) for model in self._terms_models]
        translation_models = [self._get_api_model(model) for model in self._translation_models]
        summary_models = [self._get_api_model(model) for model in self._summary_models]

        # Iterate through all possible combinations of models and token limits
        for term_model in terms_models:
            term_model_limit = self._original_language_token_limit_worst_case(term_model["max_tokens"])
            term_model_limit = term_model_limit - (term_model_limit % 4)

            for translation_model in translation_models:
                translation_model_limit = self._original_language_token_limit_worst_case(translation_model["max_tokens"])
                translation_model_limit = translation_model_limit - (translation_model_limit % 4)

                for summary_model in summary_models:
                    summary_model_limit = self._original_language_token_limit_worst_case(summary_model["max_tokens"])
                    summary_model_limit = summary_model_limit - (summary_model_limit % 4)

                    for term_division in range(term_model_limit // 1, term_model_limit // 2, -4):
                        for translation_division in range(translation_model_limit // 1, translation_model_limit // 2, -4):
                            for summary_division in range(summary_model_limit // 1, summary_model_limit // 2, -4):

                                # Check if the current configuration is valid
                                if term_division % translation_division == 0:

                                    # Calculate the cost of the current configuration
                                    term_chunks = self._estimate_chunks(total_lines, term_division, line_token_counts)
                                    translation_chunks = self._estimate_chunks(total_lines, translation_division, line_token_counts)
                                    summary_chunks = self._estimate_chunks(total_lines, summary_division, line_token_counts)

                                    term_cost = term_chunks * term_division * term_model["cost_per_1k_tokens"]
                                    translation_cost = translation_chunks * translation_division * translation_model["cost_per_1k_tokens"]
                                    summary_cost = summary_chunks * summary_division * summary_model["cost_per_1k_tokens"]

                                    total_cost = term_cost + translation_cost + summary_cost

                                    # Check if the current configuration is better than the best configuration so far, and update the best configuration if it is
                                    if total_cost < min_cost:
                                        min_cost = total_cost
                                        best_combination = (term_division, translation_division, summary_division, term_model['name'], translation_model['name'], summary_model['name'])

        return best_combination
    
    def _calculate_line_token_counts(self, text: str) -> list[int]:
        # Validate input
        if not isinstance(text, str):
            raise TypeError("Text must be a string")
        
        # Split the text into lines and calculate the token count for each line
        lines = text.splitlines()
        line_token_counts = [get_line_token_count(line) for line in lines]

        return line_token_counts
    
    def _handle_api_exceptions(self, e: Exception) -> None:
        if isinstance(e, openai.error.APIError):
            raise GPTTranslatorAPIRetryableException(e)
        elif isinstance(e, openai.error.Timeout):
            raise GPTTranslatorAPIRetryableException(e)
        elif isinstance(e, openai.error.RateLimitError):
            raise GPTTranslatorAPIRetryableException(e)
        elif isinstance(e, openai.error.APIConnectionError):
            raise GPTTranslatorAPIRetryableException(e)
        elif isinstance(e, openai.error.InvalidRequestError):
            raise GPTTranslatorAPINoRetriesException(e)
        elif isinstance(e, openai.error.AuthenticationError):
            raise GPTTranslatorAPINoRetriesException(e)
        elif isinstance(e, openai.error.ServiceUnavailableError):
            raise GPTTranslatorAPIRetryableException(e)
        else:
            raise e
    
    def _perform_relevant_terms_action(self, **kwargs) -> str:
        available_models = [self._get_api_model(model)['name'] for model in self._terms_models]

        chunk = kwargs["chunk"]
        model = kwargs["model"]

        # Validate input
        if not isinstance(chunk, Chunk):
            raise TypeError("Chunk must be a Chunk object")
        if not isinstance(model, str):
            raise TypeError("Model must be a string")
        if model not in available_models:
            raise ValueError(f"Model must be a valid model. Available models: {', '.join(available_models)}")

        string_term_original_language = self._original_language.lower() + "_term"
        string_term_target_language = self._target_language.lower() + "_term"
        phonetic_term = "phonetic_for_" + string_term_original_language if self._original_language != "Japanese" else "rōmaji_for_" + string_term_original_language

        # Build the messages list for the API call
        messages = [
            {"role": "system", "content": f"You are a {self._original_language} to {self._target_language} translator."},
            {"role": "system", "name": "example_user", "content": 
                f"Generate a term list for the text I'm about to provide. Mantain {self._original_language} novel translation format convetions. Follow the format \"- {string_term_original_language} ({phonetic_term}) - {string_term_target_language}\""},
            {"role": "system", "name": "example_assistant", "content": "Understood. Please provide the text."},
            {"role": "user", "content": chunk.contents}
        ]

        # Call the API
        try:
            response = call_api(messages, model)
            response = response['choices'][0]['message']['content']
        except Exception as e:
            self._handle_api_exceptions(e)
        
        return response
    
    def _perform_translation_action(self, **kwargs) -> str:
        available_models = [self._get_api_model(model)['name'] for model in self._translation_models]

        chunk = kwargs["chunk"]
        term_lists = kwargs["term_lists"]
        summary = kwargs["summary"]
        translation_model = kwargs["translation_model"]
        
        # Validate inputs
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
            {"role": "system", "content": f"You are a {self._original_language} to {self._target_language} translator."},
            {"role": "system", "name": "example_user", "content": 
                f"Translate the chunk of text I'm about to provide. Mantain {self._original_language} novel translation format convetions. As context, I'll provide the immediate previous line of the text, the immediate next line of the text, the summary of the enclosing section, and a list of relevant terms and their translations to use. Do not repeat the {self._original_language} text before the translation, nor clarify your actions."},
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
        messages.append({"role": "system", "name": "example_user", "content": term_lists.for_api(chunk.contents)})
        messages.append({"role": "system", "name": "example_assistant", "content": "Understood. Please provide the text."})
        messages.append({"role": "user", "content": chunk.contents})

        # Call the API
        try:
            response = call_api(messages, model=translation_model)
            response = response['choices'][0]['message']['content']
        except Exception as e:
            self._handle_api_exceptions(e)
            
        return response
    
    def _perform_summary_action(self, **kwargs) -> str:
        available_models = [self._get_api_model(model)['name'] for model in self._summary_models]

        chunk = kwargs['chunk']
        previous_summary = kwargs['previous_summary']
        summarization_model = kwargs['summarization_model']

        # Validate parameters
        if not isinstance(chunk, str):
            raise TypeError("Chunk must be a string")
        if not isinstance(previous_summary, str):
            raise TypeError("Previous summary must be a string")
        if not isinstance(summarization_model, str):
            raise TypeError("Summarization model must be a string")
        if summarization_model not in available_models:
            raise ValueError(f"Summarization model must be a valid model. Available models: {', '.join(available_models)}")

        # Build the messages to send to the API
        messages = [
            {"role": "system", "content": f"You are an assistant that summarizes {self._original_language} text in {self._target_language}."},
            {"role": "system", "name": "example_user", "content": f"You are summarizing a text. Part of this text has already been summarized. I'll provide this previous summary and the proceeding chunk text. Please provide an updated summary of the text. Do not repeat the {self._original_language} text before the summary, nor clarify your actions."},
            {"role": "system", "name": "example_assistant", "content": "Understood. Please provide the previous summary."}
        ]
        if previous_summary:
            messages.append({"role": "system", "name": "example_user", "content": previous_summary})
            messages.append({"role": "system", "name": "example_assistant", "content": "Understood. Please provide the text."})
        else:
            messages.append({"role": "system", "name": "example_user", "content": ""})
            messages.append({"role": "system", "name": "example_assistant", "content": "No summary provided. The text is the first line of the text. Please provide the text."})
        messages.append({"role": "user", "content": chunk})

        # Call the API
        try:
            response = call_api(messages, model=summarization_model)
            response = response['choices'][0]['message']['content']
        except Exception as e:
            self._handle_api_exceptions(e)
        
        return response
    
    def _perform_novel_metadata_action(self, **kwargs) -> None:
        available_models = [self._get_api_model(model)['name'] for model in self._summary_models]

        novel = kwargs['novel']
        metadata_model = kwargs['metadata_model']

        # Validate parameters
        if not isinstance(novel, Novel):
            raise TypeError("Novel must be a Novel object")
        if not isinstance(metadata_model, str):
            raise TypeError("Metadata model must be a string")
        if metadata_model not in available_models:
            raise ValueError(f"Metadata model must be a valid model. Available models: {', '.join(available_models)}")

        doc, tag, text = Doc().tagtext()

        with tag('metadata'):
            with tag('title'):
                text(novel.title)
            with tag('author'):
                text(novel.author)
            with tag('description'):
                text(novel.description)

        metadata = doc.getvalue()

        # Build the messages to send to the API
        messages = [
            {"role": "system", "content": f"You are an assistant that translates {self._original_language} text in {self._target_language}."},
            {"role": "system", "name": "example_user", "content": 
                f"You are translating a novel's metadata. I'll provide the novel's metadata in {self._original_language}. Please provide the metadata in {self._target_language}. Do not repeat the {self._original_language} text before the translation, nor clarify your actions. Mantain the xml format."},
            {"role": "system", "name": "example_assistant", "content": f"Understood. Please provide the metadata in {self._original_language}."},
            {"role": "user", "content": f"{metadata}"}
        ]

        # Call the API
        try:
            response = call_api(messages, model=metadata_model)
            response = response['choices'][0]['message']['content']
        except Exception as e:
            self._handle_api_exceptions(e)

        try:
            root = ET.fromstring(response)
            novel.title_translation = root.find('title').text
            novel.author_translation = root.find('author').text
            novel.description_translation = root.find('description').text
        except Exception as e:
            raise GPTTranslatorGPTFormatException("Invalid metadata format {}".format(e))
    
    def _perform_chapters_metadata_action(self, **kwargs) -> str:
        available_models = [self._get_api_model(model)['name'] for model in self._summary_models]

        novel = kwargs['novel']
        sub_chapters = kwargs['sub_chapters']
        metadata_model = kwargs['metadata_model']

        # Validate parameters
        if not isinstance(novel, Novel):
            raise TypeError("Novel must be a Novel object")
        if not isinstance(metadata_model, str):
            raise TypeError("Metadata model must be a string")
        if metadata_model not in available_models:
            raise ValueError(f"Metadata model must be a valid model. Available models: {', '.join(available_models)}")
        if not isinstance(sub_chapters, list):
            raise TypeError("Sub chapters must be a list")
        if not all(isinstance(sub_chapter, SubChapter) for sub_chapter in sub_chapters):
            raise TypeError("Sub chapters must be SubChapter objects")
        # if not isinstance(targets, dict):
        #     raise TypeError("Targets must be a dictionary")
        # if not all(isinstance(key, str) for key in targets.keys()):
        #     raise TypeError("Chapter numbers must be strings")
        # if not all(key.isdigit() for key in targets.keys()):
        #     raise TypeError("Chapter numbers must be digits as strings")
        # if not all(isinstance(value, list) for value in targets.values()):
        #     raise TypeError("Sub chapter numbers must be lists")
        # if not all(isinstance(item, str) for value in targets.values() for item in value):
        #     raise TypeError("Sub chapter numbers must be strings")
        # if not all(item.isdigit() for value in targets.values() for item in value):
        #     raise TypeError("Sub chapter numbers must be digits as strings")

        # sub_chapters = get_targeted_sub_chapters(novel, targets)

        doc, tag, text = Doc().tagtext()

        with tag('metadata'):
            for chapter in novel.chapters:
                with tag('chapter', id=str(chapter.chapter_index)):
                    with tag('title'):
                        text(chapter.name)
                    for sub_chapter in chapter.sub_chapters:
                        if sub_chapter in sub_chapters:
                            with tag('sub_chapter', id=str(sub_chapter.sub_chapter_index)):
                                text(sub_chapter.name)

        metadata = doc.getvalue()

        # Build the messages to send to the API
        messages = [
            {"role": "system", "content": f"You are an assistant that summarizes {self._original_language} text in {self._target_language}."},
            {"role": "system", "name": "example_user", "content": 
                f"You are translating a novel's metadata. I'll provide the novel's metadata in {self._original_language}. Please provide the metadata in {self._target_language}. Do not repeat the {self._original_language} text before the translation, nor clarify your actions. Mantain the xml format."},
            {"role": "system", "name": "example_assistant", "content": f"Understood. Please provide the metadata in {self._original_language}."},
            {"role": "user", "content": f"{metadata}"}
        ]

        # Call the API
        try:
            response = call_api(messages, model=metadata_model)
            response = response['choices'][0]['message']['content']
        except Exception as e:
            self._handle_api_exceptions(e)

        try:
            root = ET.fromstring(response)
            chapters = root.findall('chapter')
            for chapter_data in chapters:
                chapter = novel.get_chapter(int(chapter_data.attrib['id']))
                chapter.translated_name = chapter_data.find('title').text
                sub_chapters = chapter_data.findall('sub_chapter')
                for sub_chapter_data in sub_chapters:
                    sub_chapter = chapter.get_sub_chapter(int(sub_chapter_data.attrib['id']))
                    sub_chapter.translated_name = sub_chapter_data.text
        except Exception as e:
            raise GPTTranslatorGPTFormatException("Invalid metadata format")

    def _summarize_sub_chapter(self,  **kwargs) -> str:
        available_models = [self._get_api_model(model)['name'] for model in self._summary_models]

        chunks = kwargs['chunks']
        model = kwargs['model']

        # Validate the provided arguments
        if not isinstance(chunks, list):
            raise TypeError("Chunks must be a list")
        if not all(isinstance(chunk, Chunk) for chunk in chunks):
            raise TypeError("Chunks must be a list of Chunk objects")
        if not isinstance(model, str):
            raise TypeError("Metadata model must be a string")
        if model not in available_models:
            raise ValueError(f"Metadata model must be a valid model. Available models: {', '.join(available_models)}")

        api_call_queue = APICallQueue()
        api_call_queue.start()
        
        previous_summary = ""
        for chunk in chunks:
            tries = 0
            while True:
                task_id = api_call_queue.add_call(self._perform_summary_action, retries=1, chunk=chunk.contents, summarization_model=model, previous_summary=previous_summary)
                api_call_queue.wait()
                result = api_call_queue.get_result(task_id)
                
                if not isinstance(result, Exception):
                    previous_summary = result
                    break
                else:
                    if isinstance(result, GPTTranslatorAPIRetryableException):
                        if tries < 3:
                            tries += 1
                            continue
                        else:
                            api_call_queue.stop()
                            raise result
                    else:
                        api_call_queue.stop()
                        raise result
            
            previous_summary = result

        api_call_queue.stop()

        return previous_summary
    
    def _gather_terms_for_sub_chapter(self,  **kwargs) -> str:
        available_models = [self._get_api_model(model)['name'] for model in self._terms_models]

        chunks = kwargs['chunks']
        model = kwargs['model']

        # Validate the provided arguments
        if not isinstance(chunks, list):
            raise TypeError("Chunks must be a list")
        if not all(isinstance(chunk, Chunk) for chunk in chunks):
            raise TypeError("Chunks must be a list of Chunk objects")
        if not isinstance(model, str):
            raise TypeError("Metadata model must be a string")
        if model not in available_models:
            raise ValueError(f"Metadata model must be a valid model. Available models: {', '.join(available_models)}")

        api_call_queue = APICallQueue()
        api_call_queue.start()

        previous_terms = ""
        for chunk in chunks:
            tries = 0
            while True:
                task_id = api_call_queue.add_call(self._perform_relevant_terms_action, retries=1, chunk=chunk, model=model)
                api_call_queue.wait()
                result = api_call_queue.get_result(task_id)

                if not isinstance(result, Exception):
                    previous_terms += result + "\n\n"
                    break
                else:
                    if isinstance(result, GPTTranslatorAPIRetryableException):
                        if tries < 3:
                            tries += 1
                            continue
                        else:
                            api_call_queue.stop()
                            raise result
                    else:
                        api_call_queue.stop()
                        raise result
                    
        api_call_queue.stop()

        return previous_terms
    
    def _translate_sub_chapter(self,  **kwargs) -> str:
        available_models = [self._get_api_model(model)['name'] for model in self._translation_models]

        chunks = kwargs['chunks']
        model = kwargs['model']
        summary = kwargs['summary']
        term_lists = kwargs['term_lists']

        # Validate the provided arguments
        if not isinstance(chunks, list):
            raise TypeError("Chunks must be a list")
        if not all(isinstance(chunk, Chunk) for chunk in chunks):
            raise TypeError("Chunks must be a list of Chunk objects")
        if not isinstance(model, str):
            raise TypeError("Metadata model must be a string")
        if model not in available_models:
            raise ValueError(f"Metadata model must be a valid model. Available models: {', '.join(available_models)}")
        if not isinstance(summary, str):
            raise TypeError("Summary must be a string")
        
        api_call_queue = APICallQueue()
        api_call_queue.start()

        translation = {}
        for chunk in chunks:
            tries = 0
            while True:
                task_id = api_call_queue.add_call(self._perform_translation_action, retries=1, chunk=chunk, translation_model=model, summary=summary, term_lists=term_lists)
                api_call_queue.wait()
                result = api_call_queue.get_result(task_id)

                if not isinstance(result, Exception):
                    translation[chunk.chunk_index] = result
                    break
                else:
                    if isinstance(result, GPTTranslatorAPIRetryableException):
                        if tries < 3:
                            tries += 1
                            continue
                        else:
                            api_call_queue.stop()
                            raise result
                    else:
                        api_call_queue.stop()
                        raise result

        api_call_queue.stop()

        return "\n\n".join([translation[key] for key in sorted(translation)])
    
    def _get_sub_chapter_context(self, novel: Novel, chapter_index: int, sub_chapter_index: int) -> tuple[SubChapter, SubChapter]:
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
            raise GPTTranslatorException("Invalid chapter or sub chapter index")

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
    
    def translate_novel_metadata(self, novel: Novel) -> list[Exception]:
        # Validate the provided arguments
        if not isinstance(novel, Novel):
            raise TypeError("Novel must be a Novel object")
        
        # Get the metadata model
        model = self._get_api_model(self._metadata_models[0])['name']

        api_call_queue = APICallQueue()
        api_call_queue.start()
        
        tries = 0
        while True:
            task_id = api_call_queue.add_call(self._perform_novel_metadata_action, retries=1, novel=novel, metadata_model=model)
            api_call_queue.wait()
            result = api_call_queue.get_result(task_id)

            if not isinstance(result, Exception):
                break
            else:
                if isinstance(result, GPTTranslatorAPIRetryableException):
                    if tries < 3:
                        tries += 1
                        continue
                    else:
                        api_call_queue.stop()
                        return [result]
                else:
                    api_call_queue.stop()
                    return [result]

        api_call_queue.stop()

        return []
    
    def translate_sub_chapters_metadata(self, novel: Novel, targets: dict[str, list[str]]) -> list[Exception]:
        # Validate parameters
        if not isinstance(novel, Novel):
            raise TypeError("Novel must be a Novel object")
        if not isinstance(targets, dict):
            raise TypeError("Targets must be a dictionary")
        if not all(isinstance(key, str) for key in targets.keys()):
            raise TypeError("Chapter numbers must be strings")
        if not all(key.isdigit() for key in targets.keys()):
            raise TypeError("Chapter numbers must be digits as strings")
        if not all(isinstance(value, list) for value in targets.values()):
            raise TypeError("Sub chapter numbers must be lists")
        if not all(isinstance(item, str) for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be strings")
        if not all(item.isdigit() for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be digits as strings")
        
        # Get the metadata model
        model = self._get_api_model(self._metadata_models[0])['name']
        
        sub_chapters = get_targeted_sub_chapters(novel, targets)

        api_call_queue = APICallQueue()
        api_call_queue.start()

        # Translate the metadata

        tries = 0
        while True:
            task_id = api_call_queue.add_call(self._perform_chapters_metadata_action, retries=1, novel=novel, sub_chapters=sub_chapters, metadata_model=model)
            api_call_queue.wait()
            result = api_call_queue.get_result(task_id)

            if not isinstance(result, Exception):
                break
            else:
                if isinstance(result, GPTTranslatorAPIRetryableException):
                    if tries < 3:
                        tries += 1
                        continue
                    else:
                        api_call_queue.stop()
                        return [result]
                else:
                    api_call_queue.stop()
                    return [result]
                
        api_call_queue.stop()

        return []

    def summarize_sub_chapters(self, novel: Novel, targets: dict[str, list[str]]) -> list[Exception]:
        # Validate parameters
        if not isinstance(novel, Novel):
            raise TypeError("Novel must be a Novel object")
        if not isinstance(targets, dict):
            raise TypeError("Targets must be a dictionary")
        if not all(isinstance(key, str) for key in targets.keys()):
            raise TypeError("Chapter numbers must be strings")
        if not all(key.isdigit() for key in targets.keys()):
            raise TypeError("Chapter numbers must be digits as strings")
        if not all(isinstance(value, list) for value in targets.values()):
            raise TypeError("Sub chapter numbers must be lists")
        if not all(isinstance(item, str) for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be strings")
        if not all(item.isdigit() for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be digits as strings")
        
        sub_chapters = get_targeted_sub_chapters(novel, targets)

        tasks = {}

        api_call_queue = APICallQueue()
        api_call_queue.start()

        # Summarize the sub chapters
        for sub_chapter in sub_chapters:
            if sub_chapter.summary:
                continue

            prev_sub_chapter, next_sub_chapter = self._get_sub_chapter_context(novel, sub_chapter.chapter_index, sub_chapter.sub_chapter_index)

            # Get the previous and next lines and summary
            prev_line = prev_sub_chapter.contents.splitlines()[-1] if prev_sub_chapter and prev_sub_chapter.contents else ""
            next_line = next_sub_chapter.contents.splitlines()[0] if next_sub_chapter and next_sub_chapter.contents else ""

            # Calculate the optimal configuration for the sub chapter
            line_token_counts = self._calculate_line_token_counts(sub_chapter.contents)
            _, _, summary_division, _, _, summary_model = self._greedy_find_max_optimal_configuration(line_token_counts)

            # Split the text into chunks for the terms sheet API
            terms_chunks = self._split_text_into_chunks(sub_chapter.contents, summary_division, line_token_counts)
            terms_chunks_objects = list()
            for i, chunk in enumerate(terms_chunks):
                chunk_prev_line = prev_line if i == 0 else terms_chunks[i - 1].splitlines()[-1]
                chunk_next_line = next_line if i == len(terms_chunks) - 1 else terms_chunks[i + 1].splitlines()[0]

                terms_chunks_objects.append(Chunk(
                    novel.novel_code,
                    sub_chapter.chapter_index,
                    sub_chapter.sub_chapter_index,
                    i,
                    chunk,
                    chunk_prev_line,
                    chunk_next_line))
            
            tasks[(sub_chapter.chapter_index, sub_chapter.sub_chapter_index)] = api_call_queue.add_call(self._summarize_sub_chapter, retries=1, chunks=terms_chunks_objects, model=summary_model)

        api_call_queue.wait()
        
        exceptions = []
        for key, value in tasks.items():
            result = api_call_queue.get_result(value)
            if not isinstance(result, Exception):
                active_chapter = novel.get_chapter(key[0])
                active_sub_chapter = active_chapter.get_sub_chapter(key[1])
                active_sub_chapter.summary = result
            else:
                exceptions.append(result)

        api_call_queue.stop()

        return exceptions
    
    def gather_terms_for_sub_chapters(self, novel: Novel, targets: dict[str, list[str]]) -> list[Exception]:
        # Validate parameters
        if not isinstance(novel, Novel):
            raise TypeError("Novel must be a Novel object")
        if not isinstance(targets, dict):
            raise TypeError("Targets must be a dictionary")
        if not all(isinstance(key, str) for key in targets.keys()):
            raise TypeError("Chapter numbers must be strings")
        if not all(key.isdigit() for key in targets.keys()):
            raise TypeError("Chapter numbers must be digits as strings")
        if not all(isinstance(value, list) for value in targets.values()):
            raise TypeError("Sub chapter numbers must be lists")
        if not all(isinstance(item, str) for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be strings")
        if not all(item.isdigit() for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be digits as strings")
        
        sub_chapters = get_targeted_sub_chapters(novel, targets)

        tasks = {}

        api_call_queue = APICallQueue()
        api_call_queue.start()

        # Summarize the sub chapters
        for sub_chapter in sub_chapters:
            prev_sub_chapter, next_sub_chapter = self._get_sub_chapter_context(novel, sub_chapter.chapter_index, sub_chapter.sub_chapter_index)

            # Get the previous and next lines and summary
            prev_line = prev_sub_chapter.contents.splitlines()[-1] if prev_sub_chapter and prev_sub_chapter.contents else ""
            next_line = next_sub_chapter.contents.splitlines()[0] if next_sub_chapter and next_sub_chapter.contents else ""

            # Calculate the optimal configuration for the sub chapter
            line_token_counts = self._calculate_line_token_counts(sub_chapter.contents)
            terms_division, _, _, terms_model, _, _ = self._greedy_find_max_optimal_configuration(line_token_counts)

            # Split the text into chunks for the terms sheet API
            terms_chunks = self._split_text_into_chunks(sub_chapter.contents, terms_division, line_token_counts)
            terms_chunks_objects = list()
            for i, chunk in enumerate(terms_chunks):
                chunk_prev_line = prev_line if i == 0 else terms_chunks[i - 1].splitlines()[-1]
                chunk_next_line = next_line if i == len(terms_chunks) - 1 else terms_chunks[i + 1].splitlines()[0]

                terms_chunks_objects.append(Chunk(
                    novel.novel_code,
                    sub_chapter.chapter_index,
                    sub_chapter.sub_chapter_index,
                    i,
                    chunk,
                    chunk_prev_line,
                    chunk_next_line))
                
            tasks[(sub_chapter.chapter_index, sub_chapter.sub_chapter_index)] = api_call_queue.add_call(self._gather_terms_for_sub_chapter, retries=1, chunks=terms_chunks_objects, model=terms_model)

        api_call_queue.wait()

        terms = ""
        exceptions = []
        for _, value in tasks.items():
            result = api_call_queue.get_result(value)
            if not isinstance(result, Exception):
                terms += result + "\n\n"
            else:
                exceptions.append(result)

        api_call_queue.stop()

        if not novel.terms_sheet:
            novel.terms_sheet = TermSheet(novel.novel_code)
        novel.terms_sheet.process_new_terms(terms)

        return exceptions
    
    def translate_sub_chapters(self, novel: Novel, targets: dict[str, list[str]]) -> list[Exception]:
        # Validate parameters
        if not isinstance(novel, Novel):
            raise TypeError("Novel must be a Novel object")
        if not isinstance(targets, dict):
            raise TypeError("Targets must be a dictionary")
        if not all(isinstance(key, str) for key in targets.keys()):
            raise TypeError("Chapter numbers must be strings")
        if not all(key.isdigit() for key in targets.keys()):
            raise TypeError("Chapter numbers must be digits as strings")
        if not all(isinstance(value, list) for value in targets.values()):
            raise TypeError("Sub chapter numbers must be lists")
        if not all(isinstance(item, str) for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be strings")
        if not all(item.isdigit() for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be digits as strings")
        
        sub_chapters = get_targeted_sub_chapters(novel, targets)

        tasks = {}

        api_call_queue = APICallQueue()
        api_call_queue.start()

        # Summarize the sub chapters
        for sub_chapter in sub_chapters:
            if sub_chapter.translation:
                continue

            prev_sub_chapter, next_sub_chapter = self._get_sub_chapter_context(novel, sub_chapter.chapter_index, sub_chapter.sub_chapter_index)

            # Get the previous and next lines and summary
            prev_line = prev_sub_chapter.contents.splitlines()[-1] if prev_sub_chapter and prev_sub_chapter.contents else ""
            next_line = next_sub_chapter.contents.splitlines()[0] if next_sub_chapter and next_sub_chapter.contents else ""

            # Calculate the optimal configuration for the sub chapter
            line_token_counts = self._calculate_line_token_counts(sub_chapter.contents)
            _, translate_division, _, _, translate_model, _ = self._greedy_find_max_optimal_configuration(line_token_counts)

            # Split the text into chunks for the terms sheet API
            terms_chunks = self._split_text_into_chunks(sub_chapter.contents, translate_division, line_token_counts)
            terms_chunks_objects = list()
            for i, chunk in enumerate(terms_chunks):
                chunk_prev_line = prev_line if i == 0 else terms_chunks[i - 1].splitlines()[-1]
                chunk_next_line = next_line if i == len(terms_chunks) - 1 else terms_chunks[i + 1].splitlines()[0]

                terms_chunks_objects.append(Chunk(
                    novel.novel_code,
                    sub_chapter.chapter_index,
                    sub_chapter.sub_chapter_index,
                    i,
                    chunk,
                    chunk_prev_line,
                    chunk_next_line))
                
            tasks[(sub_chapter.chapter_index, sub_chapter.sub_chapter_index)] = api_call_queue.add_call(self._translate_sub_chapter, retries=1, chunks=terms_chunks_objects, model=translate_model, summary=sub_chapter.summary, term_lists=novel.terms_sheet)

        api_call_queue.wait()

        translation = ""
        exceptions = []
        for key, value in tasks.items():
            result = api_call_queue.get_result(value)
            if not isinstance(result, Exception):
                active_chapter = novel.get_chapter(key[0])
                active_sub_chapter = active_chapter.get_sub_chapter(key[1])
                active_sub_chapter.translation = result

            else:
                exceptions.append(result)

        api_call_queue.stop()

        return exceptions

@singleton
class GPTTranslatorSingleton(GPTTranslator):
    def __init__(self) -> None:
        cf = Config()
        available_models = cf.data.config.openai.models
        terms_models = cf.data.config.translator.api.terms_list.models
        translation_models = cf.data.config.translator.api.translation.models
        summary_models = cf.data.config.translator.api.summary.models
        metadata_models = cf.data.config.translator.api.metadata.models
        original_language = ""
        target_language = cf.vars["target_language"]
        self._initialize(available_models, terms_models, translation_models, summary_models, metadata_models, original_language, target_language)
