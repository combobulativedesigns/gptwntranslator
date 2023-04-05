from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.scrapers.syosetu_scraper import process_novel
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelIndexUpdate(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        storage = JsonStorage()

        # Print title
        last_y = print_title(screen, resources["title"], 0)

        last_y += 2
        screen.print_at("Updating metadata...", 2, last_y)
        screen.refresh()

        last_y += 1
        try:
            novels = storage.get_data()
        except Exception as e:
            screen.print_at("Error loading local storage.", 2, last_y)
            messages = [
                f"Error: Error loading local storage.",
                f"Error: {e}"]
            target = PageMessage
            params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
            return target, params

        try:
            # Scrape novel
            novel = process_novel(novel_code)
            screen.print_at("Metadata updated successfully.", 2, last_y)
            last_y += 1
            screen.print_at("Saving novel to local storage...", 2, last_y)
            screen.refresh()
            try:
                # Save novel to local storage
                novel_old = [novel for novel in novels if novel.novel_code == novel_code][0]
                novel_old.title = novel.title
                novel_old.author = novel.author
                novel_old.description = novel.description
                novel.author_link = novel.author_link if novel.author_link else novel_old.author_link
                for chapter in novel.chapters:
                    if chapter not in novel_old.chapters:
                        novel_old.chapters.append(chapter)
                storage.set_data(novels)
                last_y += 1
                screen.print_at("Novel saved to local storage.", 2, last_y)
                target, params = self.args["return_page"], self.args["return_kwargs"]
            except Exception as e:
                screen.print_at("Novel saving failed.", 2, last_y)
                messages = [
                    f"Error: Novel saving failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
        except Exception as e:
            screen.print_at("Metadata update failed.", 2, last_y)
            messages = [
                f"Error: Metadata update failed.",
                f"Error: {e}"]
            target = PageMessage
            params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}

        last_y += 2
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params