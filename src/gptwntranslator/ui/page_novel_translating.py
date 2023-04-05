from gptwntranslator.helpers.text_helper import parse_chapters
from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.translators.gpt_translator import GPTTranslatorSingleton
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelTranslating(PageBase):
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
                message = "(1/12) Parsing chapter targets... "
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
                message = "(2/12) Loading local storage... "
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
                message = "(3/12) Initializing translator... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                translator = GPTTranslatorSingleton()
                translator.set_original_language(novel.original_language)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error initializing translator.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(4/12) Generating summary for targets... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novel = [novel for novel in novels if novel.novel_code == novel_code][0]
                exceptions = translator.summarize_sub_chapters(novel, targets)
                if exceptions:
                    raise Exception("Summary generation failed for some sub chapters. {}".format(exceptions[0]))
                else:
                    screen.print_at("success.", 2 + len(message), last_y)
                    screen.refresh()
                    last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error generating summary.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(5/12) Saving novel to local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                storage.set_data(novels)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Novel saving failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(6/12) Updating novel terms sheet with targets... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                exceptions = translator.gather_terms_for_sub_chapters(novel, targets)
                if exceptions:
                    raise Exception("Terms sheet update failed for some chapters. {}".format(exceptions[0]))
                else:
                    screen.print_at("success.", 2 + len(message), last_y)
                    screen.refresh()
                    last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error updating terms sheet.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(7/12) Saving novel to local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                storage.set_data(novels)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Novel saving failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(8/12) Updating terms sheet weights... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                novel.terms_sheet.update_dimensions(novel.original_body(), novel.original_language)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error updating terms sheet weights.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(9/12) Translating targets... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                exceptions = translator.translate_sub_chapters(novel, targets)
                if exceptions:
                    raise Exception("Translation failed for some sub chapters. {}".format(exceptions[0]))
                else:
                    screen.print_at("success.", 2 + len(message), last_y)
                    screen.refresh()
                    last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error translating.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
                break

            try:
                message = "(10/12) Saving novel to local storage... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                storage.set_data(novels)
                screen.print_at("success.", 2 + len(message), last_y)
                screen.refresh()
                last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Novel saving failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
                break

            try:
                message = "(11/12) Translating targets' metadata... "
                screen.print_at(message, 2, last_y)
                screen.refresh()
                exceptions = translator.translate_sub_chapters_metadata(novel, targets)
                if exceptions:
                    raise Exception("Translation of metadata failed for some sub chapters. {}".format(exceptions[0]))
                else:
                    screen.print_at("success.", 2 + len(message), last_y)
                    screen.refresh()
                    last_y += 1
            except Exception as e:
                screen.print_at("failed.", 2 + len(message), last_y)
                last_y += 1
                messages = [
                    f"Error: Error translating metadata.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
                break

            try:
                message = "(12/12) Saving novel to local storage... "
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


