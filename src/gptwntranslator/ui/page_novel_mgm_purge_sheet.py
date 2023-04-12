import copy

from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.ui_helper import print_messages, print_title, wait_for_user_input
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources
from gptwntranslator.ui.page_base import PageBase


class PageNovelPurgeSheet(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        novel_origin = kwargs["novel_origin"]
        storage = JsonStorage()
        config = Config()
        target_language = config.data.config.translator.target_language
        target_language_name = config.get_language_name_for_code(target_language)

        # Print title
        last_y = print_title(screen, resources["title"], 0)
        
        last_y += 2
        last_y = print_messages(screen, [f"Purging {target_language_name} summaries"], 2, last_y)

        while True:
            last_y += 1
            try:
                message = "(1/3) Loading local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novels = storage.get_data()
                novel_old = [novel for novel in novels if novel.novel_code == novel_code and novel.novel_origin == novel_origin][0]
                novel_new = copy.deepcopy(novel_old)
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
                message = "(2/3) Purging sheet... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                for _, term_item in novel_new.terms_sheet.terms.items():
                    if term_item.has_translation(target_language):
                        translations = copy.deepcopy(term_item.translations)
                        if target_language in translations:
                            _ = translations.pop(target_language)
                            term_item.translations = translations
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error purging sheet.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(3/3) Saving novel to local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novels.remove(novel_old)
                novels.append(novel_new)
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
