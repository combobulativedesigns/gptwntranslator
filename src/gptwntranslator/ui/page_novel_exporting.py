import os
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.data_helper import get_targeted_sub_chapters
from gptwntranslator.helpers.file_helper import write_md_as_epub
from gptwntranslator.helpers.text_helper import write_novel_md, parse_chapters
from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.models.novel import Novel
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelExporting(PageBase):
    def __init__(self) -> None:
        pass


    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        targets = kwargs["target"]
        storage = JsonStorage()
        config = Config()
        target_language = config.data.config.translator.target_language

        # Print title
        last_y = print_title(screen, resources["title"], 0)
        
        last_y += 2
        screen.print_at(f"Exporting targets: {targets}", 2, last_y)

        while True:
            last_y += 2
            try:
                message = "(1/3) Parsing chapter targets... "
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
                message = "(2/3) Loading local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novels = storage.get_data()
                novel = [novel for novel in novels if novel.novel_code == novel_code][0]
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
                message = "(3/3) Exporting novel to epub... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                md_text = write_novel_md(novel, targets)
                output = os.path.join(config.vars["output_path"], f"{novel.novel_code}-{target_language}.epub")
                write_md_as_epub(md_text, output)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
                target, params = self.args["return_page"], self.args["return_kwargs"]
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error exporting novel to epub.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
            break

        last_y += 1
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params