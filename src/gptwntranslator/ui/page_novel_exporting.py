import os
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.data_helper import get_targeted_sub_chapters
from gptwntranslator.helpers.file_helper import write_md_as_epub
from gptwntranslator.helpers.text_helper import parse_chapters
from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.models.novel import Novel
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelExporting(PageBase):
    def __init__(self) -> None:
        pass

    def export_epub(self, novel: Novel, targets: dict[str, list[str]]) -> None:
        # Validate parameters
        if not isinstance(novel, Novel):
            raise TypeError("Novel must be a Novel object")
        if not isinstance(targets, dict):
            raise TypeError("Targets must be a dictionary")
        if not all(isinstance(key, str) for key in targets.keys()):
            raise TypeError("Chapter numbers must be strings")
        if not all(key.isdigit() for key in targets.keys()):
            raise TypeError("Chapter numbers must be digits as strings")
        if not all(isinstance(value, list) for value in targets.values()):
            raise TypeError("Sub chapter numbers must be lists")
        if not all(isinstance(item, str) for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be strings")
        if not all(item.isdigit() for value in targets.values() for item in value):
            raise TypeError("Sub chapter numbers must be digits as strings")
        
        config = Config()

        sub_chapters = get_targeted_sub_chapters(novel, targets)

        metadata = f"---\ntitle: \"{novel.title_translation}\"\nauthor: \"{novel.author_translation}\"\nlanguage: {config.data.config.translator.target_language}\n---\n\n"

        md_text = metadata
        # md_text += "# **{}**\n\n".format(novel.title_translation)
        md_text += "# **Contents**\n\n"
        md_text += "\n".join([f"- [{sub_chapter.translated_name if sub_chapter.translated_name is not None else sub_chapter.name}](#chapter-{sub_chapter.chapter_index}-{sub_chapter.sub_chapter_index})" for sub_chapter in sub_chapters])
        md_text += "\n\n"
        
        for sub_chapter in sub_chapters:
            name = sub_chapter.translated_name if sub_chapter.translated_name is not None else sub_chapter.name
            # md_text += f"# **Chapter {sub_chapter.chapter_index}-{sub_chapter.sub_chapter_index}**\n\n"
            md_text += f"<h1 id=\"chapter-{sub_chapter.chapter_index}-{sub_chapter.sub_chapter_index}\"><strong>{name}</strong></h1>"
            lines = sub_chapter.translation.splitlines()
            for line in lines:
                md_text += "{}\n\n".format(line.strip('\n\t '))

        output = os.path.join(config.vars["output_path"], f"{novel.novel_code}-{config.data.config.translator.target_language}.epub")
        write_md_as_epub(md_text, output)


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
                self.export_epub(novel, targets)
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