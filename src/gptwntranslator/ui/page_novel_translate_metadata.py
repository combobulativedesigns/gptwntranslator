from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.translators.gpt_translator import GPTTranslatorJP2EN
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelTranslateMetadata(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        storage = JsonStorage()

        # Print title
        last_y = print_title(screen, resources["title"], 0)

        while True:
            last_y += 2
            try:
                screen.print_at("Loading novel from local storage...", 2, last_y)
                screen.refresh()
                novels = storage.get_data()
                novel = [novel for novel in novels if novel.novel_code == novel_code][0]
                screen.print_at("Novel loaded successfully.", 2, last_y + 1)
                screen.refresh()
                last_y += 2
            except Exception as e:
                screen.print_at("Error loading novel from local storage.", 2, last_y)
                messages = [
                    f"Error: Error loading local storage.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                screen.print_at("Initializing translator...", 2, last_y)
                screen.refresh()
                translator = GPTTranslatorJP2EN()
                screen.print_at("Translator initialized successfully.", 2, last_y + 1)
                screen.refresh()
                last_y += 2
            except Exception as e:
                screen.print_at("Error initializing translator.", 2, last_y)
                messages = [
                    f"Error: Error initializing translator.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break
            
            try:
                # Translate novel metadata
                screen.print_at("Translating novel metadata...", 2, last_y)
                screen.refresh()
                exceptions = translator.translate_novel_metadata(novel)
                if exceptions:
                    screen.print_at(f"There were {len(exceptions)} errors while translating novel metadata.", 2, last_y + 1)
                    screen.refresh()
                    last_y += 2
                    for exception in exceptions:
                        screen.print_at(f"Error: {exception}", 2, last_y)
                        last_y += 1
                    screen.refresh()
                    last_y += 2
                    raise Exception("There were errors while translating novel metadata.")
                else:
                    screen.print_at("Novel metadata translated successfully.", 2, last_y + 1)
                    screen.refresh()
                    last_y += 2
            except Exception as e:
                screen.print_at("Error translating novel metadata.", 2, last_y)
                messages = [
                    f"Error: Error translating novel metadata.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                screen.print_at("Saving novel to local storage...", 2, last_y)
                screen.refresh()
                storage.set_data(novels)
                screen.print_at("Novel saved to local storage.", 2, last_y + 1)
                target, params = self.args["return_page"], self.args["return_kwargs"]
                last_y += 1
            except Exception as e:
                screen.print_at("Novel saving failed.", 2, last_y)
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