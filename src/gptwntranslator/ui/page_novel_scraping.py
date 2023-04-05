from gptwntranslator.helpers.text_helper import parse_chapters
from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.scrapers.syosetu_scraper import process_targets
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelScraping(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        targets = kwargs["target"]
        storage = JsonStorage()

        # Print title
        last_y = print_title(screen, resources["title"], 0)

        while True:
            last_y += 2
            try:
                screen.print_at("Parsing chapter targets...", 2, last_y)
                screen.refresh()
                targets = parse_chapters(targets)
                screen.print_at("Chapter targets parsed successfully.", 2, last_y + 1)
                screen.refresh()
                last_y += 2
            except Exception as e:
                screen.print_at("Chapter targets parsing failed.", 2, last_y)
                messages = [
                    f"Error: Chapter targets parsing failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break
            
            try:
                screen.print_at("Loading local storage...", 2, last_y)
                screen.refresh()
                novels = storage.get_data()
                screen.print_at("Local storage loaded successfully.", 2, last_y + 1)
                screen.refresh()
                last_y += 2
            except Exception as e:
                screen.print_at("Error loading local storage.", 2, last_y)
                messages = [
                    f"Error: Error loading local storage.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break
            
            try:
                screen.print_at("Downloading chapters targets...", 2, last_y)
                screen.refresh()
                novel = [novel for novel in novels if novel.novel_code == novel_code][0]
                process_targets(novel, targets)
                screen.print_at("Chapters downloaded successfully.", 2, last_y + 1)
                screen.refresh()
                last_y += 2
            except Exception as e:
                screen.print_at("Chapters downloading failed.", 2, last_y)
                messages = [
                    f"Error: Chapters downloading failed.",
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
                last_y += 2
            except Exception as e:
                screen.print_at("Novel saving failed.", 2, last_y)
                messages = [
                    f"Error: Novel saving failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        last_y += 2
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params