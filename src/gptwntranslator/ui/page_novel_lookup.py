from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.scrapers.syosetu_scraper import process_novel
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
        storage = JsonStorage()

        # Print title
        last_y = print_title(screen, resources["title"], 0)

        last_y += 2
        screen.print_at("Checking local storage...", 2, last_y)
        screen.refresh()

        last_y += 1
        # Check if novel is already in local storage
        try:
            novels = storage.get_data()
        except Exception as e:
            screen.print_at("Error loading local storage.", 2, last_y)
            last_y += 1
            screen.refresh()
            wait_for_user_input(screen, 2, last_y)
            messages = [
                f"Error: Error loading local storage.",
                f"Error: {e}"]
            target = PageMessage
            params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            return target, params
        
        if novel_code in [novel.novel_code for novel in novels]:
            screen.print_at("Novel already in local storage.", 2, last_y)
            target, params = PageNovelMenu, {"novel_url_code": novel_code, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
        else:
            screen.print_at("Novel not in local storage.", 2, last_y)
            last_y += 1
            screen.print_at("Scraping Syosetu...", 2, last_y)
            screen.refresh()

            try:
                # Scrape novel
                novel = process_novel(novel_code)
                last_y += 1
                screen.print_at("Novel scraped successfully.", 2, last_y)
                last_y += 1
                screen.print_at("Saving novel to local storage...", 2, last_y)
                screen.refresh()
                try:
                    # Save novel to local storage
                    novels.append(novel)
                    storage.set_data(novels)
                    last_y += 1
                    screen.print_at("Novel saved to local storage.", 2, last_y)
                    target, params = PageNovelMenu, {"novel_url_code": novel_code, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                except Exception as e:
                    last_y += 1
                    screen.print_at("Novel saving failed.", 2, last_y)
                    messages = [
                        f"Error: Novel saving failed.",
                        f"Error: {e}"]
                    target = PageMessage
                    params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            except Exception as e:
                last_y += 1
                screen.print_at("Novel scraping failed.", 2, last_y)
                target, params = self.args["return_page"], self.args["return_kwargs"]
    
        last_y += 2
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params