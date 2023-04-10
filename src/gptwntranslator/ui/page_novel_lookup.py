from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.origins.origin_factory import OriginFactory
from gptwntranslator.origins.syosetu_scraper import process_novel
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.page_novel_menu import PageNovelMenu
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelLookup(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        novel_origin = kwargs["novel_origin"]
        storage = JsonStorage()
        origin = OriginFactory.get_origin(novel_origin)

        # Print title
        last_y = print_title(screen, resources["title"], 0)
        
        last_y += 2
        screen.print_at(f"Looking for novel: {novel_code}", 2, last_y)

        while True:
            last_y += 2
            try:
                message = "(1/2) Checking local storage... "
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
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
                break

            try:
                message = "(2/2) Checking if novel is already in local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novel = [novel for novel in novels if novel.novel_code == novel_code][0]
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
                target, params = PageNovelMenu, {"novel_origin": novel_origin, "novel_url_code": novel_code, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break
            except IndexError:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1

            try:
                message = "(3/4) Scraping Origin... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novel = origin.process_novel(novel_code)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error scraping novel.",
                    f"Error: {e}"]
                target, params = self.args["return_page"], self.args["return_kwargs"]
                break

            try:
                message = "(4/4) Saving novel to local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novels.append(novel)
                storage.set_data(novels)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
                target, params = PageNovelMenu, {"novel_origin": novel_origin, "novel_url_code": novel_code, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error saving novel to local storage.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        last_y += 1
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params