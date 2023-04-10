import json
import os
from gptwntranslator.encoders.json_encoder import JsonEncoder
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.file_helper import write_file
from gptwntranslator.helpers.text_helper import make_printable
from gptwntranslator.helpers.ui_helper import print_messages, print_title, wait_for_user_input
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources

class PageNovelMgmExportSheet(PageBase):
    def __init__(self) -> None:
        pass


    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        novel_origin = kwargs["novel_origin"]
        storage = JsonStorage()
        config = Config()
        target_language = config.data.config.translator.target_language
        output = os.path.join(config.vars["output_path"], f"{novel_origin}-{novel_code}-{target_language}-sheet.json")

        # Print title
        last_y = print_title(screen, resources["title"], 0)
        
        last_y += 2
        last_y = print_messages(screen, [f"Exporting term sheet: {output}"], 2, last_y)

        while True:
            last_y += 1
            try:
                message = "(1/2) Loading local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novels = storage.get_data()
                novel = [novel for novel in novels if novel.novel_code == novel_code and novel.novel_origin == novel_origin][0]
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
                message = "(1/2) Exporting term sheet to json... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                sheet = novel.terms_sheet
                json_string = make_printable(json.dumps(sheet, ensure_ascii=False, cls=JsonEncoder))
                write_file(output, json_string)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
                target, params = self.args["return_page"], self.args["return_kwargs"]
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error exporting term sheet to json.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
            break

        last_y += 1
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params


    