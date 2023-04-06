import asyncio
import locale
import os
from asciimatics.screen import Screen
from gptwntranslator.api import openai_api
from gptwntranslator.helpers.api_helper import MultiAPICallQueue
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.logger_helper import CustomLogger
from gptwntranslator.storage.json_storage import JsonStorage, JsonStorageException, JsonStorageFileException, JsonStorageFormatException
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.page_novel_selection import PageNovelSelection

logger = CustomLogger(__name__)

def _ui(screen):
    config_file_path = os.path.join(os.getcwd(), "config", "config.yaml")
    persistent_data_file_path = os.path.join(os.getcwd(), "persistent_data.json")
    output_file_path = os.path.join(os.getcwd(), "output")

    logger.info("Config file path: " + config_file_path)
    logger.info("Persistent data file path: " + persistent_data_file_path)
    logger.info("Output folder path: " + output_file_path)

    storage = JsonStorage()
    storage.initialize(persistent_data_file_path)

    while True:
        try:
            config = Config()
            config.load(config_file_path)
            config.vars["output_path"] = output_file_path
            language = config.get_language_name_for_code(config.data.config.translator.target_language)
            config.vars["target_language"] = language
            openai_api.initialize(config.data.config.openai.api_key)
            logger.info("Config file loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load config file. {e}")
            messages = [
                f"Error: Failed to load config file.",
                f"Path: {config_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        try:
            storage.get_data()
            logger.info("Persistent data file loaded successfully.")
            page = PageNovelSelection
            parameters = {}
            break
        except JsonStorageFormatException as e:
            logger.error(f"Failed to parse persistent data file. {e}")
            messages = [
                f"Error: Failed to parse persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break
        except JsonStorageFileException as e:
            logger.warning("Failed to load persistent data file. Switching to creating a new one.")
            pass
        except Exception as e:
            logger.error(f"Failed to load persistent data file. {e}")
            messages = [
                f"Error: Failed to load persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        try:
            storage.set_data([])
            logger.info("Persistent data file created successfully.")
            messages = [
                f"Error: Failed to find persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"We'll create a new one for you."]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageNovelSelection, "return_kwargs": {"novel_objects": []}}
        except JsonStorageException as e:
            logger.error(f"Failed to create persistent data file. {e}")
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
            MultiAPICallQueue().stop_all()
            logger.info("Detected Ctrl+C.")
            messages = [
                f"Detected Ctrl+C.",
                f"Shutting down..."]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
        except Exception as e:
            MultiAPICallQueue().stop_all()
            logger.error(f"An error occurred. {e}")
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