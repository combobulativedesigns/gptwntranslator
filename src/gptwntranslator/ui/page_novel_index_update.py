from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.origins.origin_factory import OriginFactory
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
        novel_origin = kwargs["novel_origin"]
        storage = JsonStorage()
        origin = OriginFactory.get_origin(novel_origin)

        # Print title
        last_y = print_title(screen, resources["title"], 0)
        
        last_y += 2
        screen.print_at(f"Updating novel metadata: {novel_code}", 2, last_y)

        while True:
            last_y += 2
            try:
                message = "(1/3) Loading local storage... "
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
                message = "(2/3) Downloading novel metadata... "
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
                    f"Error: Error downloading novel metadata.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
                break

            try:
                message = "(3/3) Updating local data... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novel_old = [novel for novel in novels if novel.novel_code == novel_code and novel.novel_origin == novel_origin][0]
                novel_old.title = novel.title
                novel_old.author = novel.author
                novel_old.description = novel.description
                novel.author_link = novel.author_link if novel.author_link else novel_old.author_link
                for chapter in novel.chapters:
                    if chapter not in novel_old.chapters:
                        novel_old.chapters.append(chapter)
                storage.set_data(novels)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
                target, params = self.args["return_page"], self.args["return_kwargs"]
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error updating local data.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        last_y += 1
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params