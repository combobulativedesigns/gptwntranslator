import openai
import tiktoken

from gptwntranslator.helpers.config_helper import Config

class OpenAI_APIException(Exception):
    pass

def initialize(api_key):
    openai.api_key = api_key

def validate_model(model: dict) -> bool:
    """Validate a model dictionary and see if it has a correct structure.
    
    Parameters
    ----------
    model : dict
        The model dictionary to validate.

    Returns
    -------
    bool
        True if the model dictionary is valid, False otherwise.
    """

    # Verify that the model dictionary has the correct structure
    if model is None:
        return False
    if "name" not in model:
        return False
    if "cost_per_1k_tokens" not in model:
        return False
    if "max_tokens" not in model:
        return False
    if not isinstance(model["name"], str):
        return False
    if not isinstance(model["cost_per_1k_tokens"], float):
        return False
    if not isinstance(model["max_tokens"], int):
        return False

    return True

def get_model(model):
    cf = Config()
    available_models = cf.data.config.openai.models
    if available_models is None:
        raise OpenAI_APIException("OpenAI API not initialized")
    if model not in available_models:
        raise OpenAI_APIException(f"Model {model} not available")
    return available_models[model]

def get_line_token_count(line, model="gpt-3.5-turbo", encoding=None):
    if encoding is None:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(line))

def get_message_token_count(message, model="gpt-3.5-turbo", encoding=None):
    if encoding is None:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = 4
    for key, value in message.items():
        num_tokens += len(encoding.encode(value))
        if key == "name":
            num_tokens += -1
    return num_tokens

def get_text_token_count(text, model="gpt-3.5-turbo", encoding=None):
    if encoding is None:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = 0
    for line in text.splitlines():
        num_tokens += len(encoding.encode(line))
    return num_tokens

def get_messages_token_count(messages, model="gpt-3.5-turbo", encoding=None):
    if encoding is None:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = 0
    for message in messages:
        num_tokens += get_message_token_count(message, model, encoding)
    num_tokens += 2
    return num_tokens

def call_api(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
    )  
    return response
