from gptwntranslator.helpers.text_helper import parse_chapters
from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.origins.origin_factory import OriginFactory
from gptwntranslator.origins.syosetu_scraper import process_targets
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
        novel_origin = kwargs["novel_origin"]
        storage = JsonStorage()
        origin = OriginFactory.get_origin(novel_origin)

        # Print title
        last_y = print_title(screen, resources["title"], 0)
        
        last_y += 2
        screen.print_at(f"Downloading targets: {targets}", 2, last_y)

        while True:
            last_y += 2
            try:
                message = "(1/4) Parsing chapter targets... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                targets = parse_chapters(targets)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Chapter targets parsing failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break
            
            try:
                message = "(2/4) Loading local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novels = storage.get_data()
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
                message = "(3/4) Downloading chapters targets... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novel = [novel for novel in novels if novel.novel_code == novel_code][0]
                origin.process_targets(novel, targets)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Chapters downloading failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(4/4) Saving novel to local storage... "
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