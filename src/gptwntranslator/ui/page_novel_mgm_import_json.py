import json
import os
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.file_helper import read_file
from gptwntranslator.helpers.ui_helper import print_messages, print_title, wait_for_user_input
from gptwntranslator.hooks.object_hook import generic_object_hook
from gptwntranslator.models.novel import Novel
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelMgmImportJson(PageBase):
    def __init__(self) -> None:
        pass


    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        novel_origin = kwargs["novel_origin"]
        storage = JsonStorage()
        config = Config()
        target_language = config.data.config.translator.target_language
        input_file = os.path.join(config.vars["input_path"], f"{novel_origin}-{novel_code}-{target_language}.json")

        # Print title
        last_y = print_title(screen, resources["title"], 0)
        
        last_y += 2
        last_y = print_messages(screen, [f"Importing JSON: {input_file}"], 2, last_y)

        while True:
            last_y += 1
            try:
                message = "(1/3) Loading local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novels = storage.get_data()
                old_novel = [novel for novel in novels if novel.novel_code == novel_code and novel.novel_origin == novel_origin][0]
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error loading local storage.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(2/3) Importing novel from json... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                json_string = read_file(input_file)
                novel_new = json.loads(json_string, object_hook=generic_object_hook)
                if not isinstance(novel_new, Novel):
                    raise Exception("Novel is not of type Novel.")
                if novel_new.novel_code != novel_code or novel_new.novel_origin != novel_origin:
                    raise Exception("Novel code and origin do not match.")
                novels.remove(old_novel)
                novels.append(novel_new)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error importing novel from json.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(3/3) Saving novel to local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                storage.set_data(novels)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
                target, params = self.args["return_page"], self.args["return_kwargs"]
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Novel saving failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        last_y += 1
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params