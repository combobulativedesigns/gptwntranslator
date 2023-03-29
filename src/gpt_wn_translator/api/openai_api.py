import openai
import tiktoken

def set_api_key(api_key):
    openai.api_key = api_key

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

def call_api(messages, model="gpt-3.5-turbo", encoding=None, **kwargs):
    if encoding is None:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
    
    response = None
    try_count = 0
    while response is None:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
            )
        except openai.error.APIConnectionError:
            try_count += 1
            if try_count > 5:
                raise openai.error.APIConnectionError
            
    return response
