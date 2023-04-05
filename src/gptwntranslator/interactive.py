import locale
import os
from asciimatics.screen import Screen
from gptwntranslator.api import openai_api
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.storage.json_storage import JsonStorage, JsonStorageException, JsonStorageFileException, JsonStorageFormatException
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.page_novel_selection import PageNovelSelection


def _ui(screen):
    config_file_path = os.path.join(os.getcwd(), "config", "config.yaml")

    persistent_data_file_path = os.path.join(os.getcwd(), "persistent_data.json")

    output_file_path = os.path.join(os.getcwd(), "output")

    storage = JsonStorage()
    storage.initialize(persistent_data_file_path)

    while True:
        try:
            config = Config()
            config.load(config_file_path)
            config.vars["output_path"] = output_file_path
            target_language = config.data.config.translator.target_language
            languages = [lang[1] for lang in [list(dct.items())[0] for dct in config.data.config.languages] if lang[0] == target_language]
            config.vars["target_language"] = languages[0]
            openai_api.initialize(config.data.config.openai.api_key)
        except Exception as e:
            messages = [
                f"Error: Failed to load config file.",
                f"Path: {config_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        try:
            storage.get_data()
            page = PageNovelSelection
            parameters = {}
            break
        except JsonStorageFormatException as e:
            messages = [
                f"Error: Failed to parse persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break
        except JsonStorageFileException as e:
            pass
        except Exception as e:
            messages = [
                f"Error: Failed to load persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        try:
            storage.set_data([])
            messages = [
                f"Error: Failed to find persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"We'll create a new one for you."]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageNovelSelection, "return_kwargs": {"novel_objects": []}}
        except JsonStorageException as e:
            messages = [
                f"Error: Failed to create persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}

        break
    while True:
        try:
            page, parameters = page().show(screen, **parameters)
        except KeyboardInterrupt:
            messages = [
                f"Detected Ctrl+C.",
                f"Shutting down..."]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
        except Exception as e:
            messages = [
                f"Error: {e}",
                f"Page: {page}",
                f"Parameters: {parameters}",
                f"Please report this error to the developer."]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}

def run_interactive():
    locale.setlocale(locale.LC_ALL, '')
    Screen.wrapper(_ui)