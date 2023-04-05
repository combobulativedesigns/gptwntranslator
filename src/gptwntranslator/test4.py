import os
import locale
from types import NoneType
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent

import gptwntranslator.api.openai_api as openai_api
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.text_helper import parse_chapters
from gptwntranslator.scrapers.syosetu_scraper import process_novel, process_targets
from gptwntranslator.storage.json_storage import JsonStorage, JsonStorageException, JsonStorageFileException, JsonStorageFormatException
from gptwntranslator.translators.gpt_translator import GPTTranslatorJP2EN


def get_resources():
    # Initialize resource dictionary
    resources = {}

    # Title of the program
    title = "gptwntranslator"

    # Version of the program
    version = "v2.0.0"

    # Title string
    title_string = f"{title} {version}"

    # Title container
    title_container = [
        "┌─" + "─" * (len(title_string) + 2) + "─┐",
        "│  " + title_string + "  │",
        "└─" + "─" * (len(title_string) + 2) + "─┘",
    ]

    resources["title"] = title_container

    resources["chapter_regex_explanation"] = [
        "Chapter numbers are represented by one or more digits (e.g., \"3\" or \"12\").",
        "Sub-chapter numbers are also represented by one or more digits (e.g., \"4\" or \"23\").",
        "Chapter ranges are represented by two chapter numbers separated by a hyphen (e.g., \"2-5\").",
        "Sub-chapter ranges are represented by two sub-chapter numbers separated by a hyphen (e.g., \"6-9\").",
        "A chapter can be followed by a colon and a list of sub-chapters or sub-chapter ranges (e.g., \"3:2,5,7-9\").",
        "Individual chapters or chapter ranges can be separated by semicolons (e.g., \"3:2,5;5-7;8:1-3,5\").",
        "Here's an example input that would match this pattern: \"1:1,3,5-7;2-4;5:1-3,6;6-8\"."]

    # Main menu options
    resources["novel_selection_menu"] = {
        "message_lines": [
            "Please enter the URL code of the novel you want to scrape.",
            "For example, the URL code of https://ncode.syosetu.com/n5177as/",
            "is n5177as.",
        ],
        "menu_items": [
            (0, 0, None, "Novel URL code:", 1, "", True),
            (2, 0, 1, "1) Search novel", PageNovelLookup, "", False),
            (4, 0, 0, "0) Exit", PageExit, "", False)]
    }

    resources["novel_menu"] = {
        "message_lines": [
            "Actions menu for the novel:",
        ],
        "menu_items": [
            (0, 0, 1, "1) Update metadata", PageNovelIndexUpdate, "", False), 
            (1, 0, 2, "2) Download chapters", PageNovelScrapingTargets, "", False), 
            (2, 0, 3, "3) Translate metadata", PageNovelTranslateMetadata, "", False), 
            (3, 0, 4, "4) Translate chapters", PageNovelTranslationTargets, "", False), 
            (4, 0, 5, "5) Edit novel", PageNovelEditingTarget, "", False), 
            (5, 0, 6, "6) Export novel", PageNovelExportTargets, "", False), 
            (7, 0, 0, "0) Go back", PageReturn, PageNovelSelection, False)]
    }

    resources["novel_scraping_targets_menu"] = {
        "message_lines": [
            "Please select the target chapters and sub chapters",
            "you wish to scrape. Leave blank to scrape all chapters.",
        ],
        "menu_items": [
            (0, 0, None, "Chapter selection pattern:", 1, "", True),
            (2, 0, 1, "1) Start scraping", PageNovelScraping, "", False),
            (3, 0, 2, "2) Pattern explanation", PageMessage, resources["chapter_regex_explanation"], False),
            (5, 0, 0, "0) Go back", PageReturn, PageNovelMenu, False)]
    }

    resources["novel_translating_targets_menu"] = {
        "message_lines": [
            "Please select the target chapters and sub chapters",
            "you wish to translate. Leave blank to translate all chapters.",
        ],
        "menu_items": [
            (0, 0, None, "Chapter selection pattern:", 1, "", True),
            (2, 0, 1, "1) Start translating", PageNovelLookup, "", False),
            (3, 0, 2, "2) Pattern explanation", PageMessage, resources["chapter_regex_explanation"], False),
            (5, 0, 0, "0) Go back", PageReturn, PageNovelMenu, False)]
    }

    resources["novel_editing_targets_menu"] = {
        "message_lines": [
            "Please select the target chapter you whish to edit.",
        ],
        "menu_items": [
            (0, 0, None, "Chapter selection pattern:", 1, "", True),
            (2, 0, 1, "1) Start editing", PageNovelLookup, "", False),
            (4, 0, 0, "0) Go back", PageReturn, PageNovelMenu, False)]
    }

    resources["novel_export_targets_menu"] = {
        "message_lines": [
            "Please select the target chapters and sub chapters",
            "you wish to export. Leave blank to export all chapters.",
        ],
        "menu_items": [
            (0, 0, None, "Chapter selection pattern:", 1, "", True),
            (2, 0, 1, "1) Start exporting", PageNovelLookup, "", False),
            (3, 0, 2, "2) Pattern explanation", PageMessage, resources["chapter_regex_explanation"], False),
            (5, 0, 0, "0) Go back", PageReturn, PageNovelMenu, False)]
    }        
    
    return resources.copy()



def print_title(screen, title, y):
    for line in title:
        y += 1
        x = 2
        screen.print_at(line, x, y)

    return y

def read_user_input(screen, x, y):
    # screen.show_cursor(True)
    input_str = ""
    while True:
        screen.print_at(input_str, x, y)
        screen.move(x + len(input_str), y)
        screen.refresh()
        event = screen.get_event()
        if isinstance(event, KeyboardEvent):
            key = event.key_code
            if key == 10 or key == 13:
                break
            elif key == screen.KEY_BACK:
                input_str = input_str[:-1]
            else:
                input_str += chr(key)

    # screen.show_cursor(False)
    return input_str

def wait_for_user_input(screen, x, y):
    screen.print_at("Press enter to continue...", x, y)
    screen.refresh()

    while True:
        event = screen.get_event()
        if isinstance(event, KeyboardEvent):
            key = event.key_code
            if key == 10 or key == 13:
                break

class PageBase:
    def __init__(self) -> None:
        self.args = {}

    def show(self, screen, **kwargs) -> tuple[object, dict]:
        self.pre_render(screen, **kwargs)
        return self.render(screen, **kwargs)
    
    def pre_render(self, screen, **kwargs) -> None:
        self.args = kwargs
        screen.clear()

    def render(self, screen, **kwargs) -> tuple[object, dict]:
        pass

    def process_actions(self, page, content) -> tuple[object, dict]:
        pass

class PageMessage(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()

        last_y = print_title(screen, resources["title"], 0)

        last_y += 1
        for message in kwargs["messages"]:
            last_y += 1
            screen.print_at(message, 2, last_y)

        last_y += 2

        screen.refresh()
        wait_for_user_input(screen, 2, last_y)

        return kwargs["return_page"], kwargs["return_kwargs"]
    
class PageExit(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()

        while True:
            last_y = print_title(screen, resources["title"], 0)

            last_y += 1
            screen.print_at("Exiting program...", 2, last_y)

            last_y += 2
            screen.refresh()
            wait_for_user_input(screen, 2, last_y)

            break

class PageReturn(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        return kwargs["return_page"], kwargs["return_kwargs"]

class Page(PageBase):
    def __init__(self, item_code: str, messages: list[str], menu_items: list[tuple[int, int, int, str, PageBase, str, bool]], pre_messages: list[str]|NoneType = None, post_messages: list[str]|NoneType = None) -> None:
        self.item_code = item_code
        self.messages = messages
        self.menu_items = menu_items
        self.pre_messages = pre_messages
        self.post_messages = post_messages

        resources = get_resources()
        self.title = resources["title"]

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        while True:
            screen.clear()

            # Print title
            last_y = print_title(screen, self.title, 0)

            if self.pre_messages is not None:
                last_y += 2
                for message in self.pre_messages:
                    screen.print_at(message, 2, last_y)
                    last_y += 1
            else:
                last_y += 1

            last_y += 1
            for message in self.messages:
                screen.print_at(message, 2, last_y)
                last_y += 1

            if self.post_messages is not None:
                last_y += 1
                for message in self.post_messages:
                    screen.print_at(message, 2, last_y)
                    last_y += 1
            else:
                last_y += 1

            screen.refresh()
            active_index = navigate_items(screen, last_y, 2, self.menu_items)
            item = self.menu_items[active_index]

            if item[4] is not None:
                page, content = self.process_actions(item, active_index)
                if page is not None:
                    return page, content
                else:
                    break
            else:
                break

        return None, {}

    def process_actions(self, item, content) -> tuple[PageBase, dict]:
        if item[4] == PageReturn:
            return item[4], {"return_page": item[5], "return_kwargs": {}}
        return item[4], item[5]

class PageTypeA(Page):
    def __init__(self, item_code: str, pre_messages=None, post_messages=None) -> None:
        self.resources = get_resources()
        messages = self.resources[item_code]["message_lines"]
        menu_items = self.resources[item_code]["menu_items"]
        super().__init__(item_code, messages, menu_items, pre_messages, post_messages)
    
class PageNovelSelection(PageTypeA):
    def __init__(self) -> None:
        super().__init__("novel_selection_menu")

    def process_actions(self, item, content):
        if item[4] == PageNovelLookup:
            return item[4], {"novel_url_code": item[5]}
        if item[4] is PageReturn:
            return item[4], {"return_page": item[5], "return_kwargs": {}}
        return item[4], {}

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
        screen.print_at("Novel Code: " + novel_code, 2, last_y)
        screen.print_at("Checking local storage...", 2, last_y + 1)
        screen.refresh()

        last_y += 2
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
            target, params = PageNovelMenu, {"novel_url_code": novel_code}
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
                    target, params = PageNovelMenu, {"novel_url_code": novel_code}
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
                target, params = PageNovelSelection, {}
    
        last_y += 2
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params

class PageNovelMenu(PageTypeA):
    def __init__(self) -> None:
        super().__init__("novel_menu")

    def pre_render(self, screen, **kwargs) -> None:
        super().pre_render(screen, **kwargs)
        storage = JsonStorage()
        novels = storage.get_data()
        novel = [novel for novel in novels if novel.novel_code == kwargs["novel_url_code"]][0]
        self.pre_messages = []
        if novel.title_translation:
            self.pre_messages.append(u"Novel: {}".format(novel.title_translation))
        else:
            self.pre_messages.append(u"Novel: {}".format(novel.title))
        if novel.author_translation:
            self.pre_messages.append(u"Author: {}".format(novel.author_translation))
        else:
            self.pre_messages.append(u"Author: {}".format(novel.author))
        self.pre_messages.append(f"Code: {novel.novel_code}")

    def process_actions(self, item, content):
        if item[4] is PageReturn:
            return item[4], {"return_page": item[5], "return_kwargs": {}}
        return item[4], self.args
    
class PageTypeB(Page):
    def __init__(self, item_code: str, pre_messages=None, post_messages=None) -> None:
        self.resources = get_resources()
        messages = self.resources[item_code]["message_lines"]
        menu_items = self.resources[item_code]["menu_items"]
        self.pre_messages = pre_messages
        self.post_messages = post_messages
        super().__init__(item_code, messages, menu_items)
    
    def process_actions(self, item, content) -> tuple[PageBase, dict]:
        if item[4] is PageMessage:
            return item[4], {"messages": item[5], "return_page": self.__class__, "return_kwargs": self.args}
        if item[4] is PageReturn:
            return item[4], {"return_page": item[5], "return_kwargs": self.args}
        return item[4], {"novel_url_code": self.args["novel_url_code"], "target": item[5]}
    
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
            params = {"messages": messages, "return_page": PageNovelMenu, "return_kwargs": self.args}
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
                target, params = PageNovelMenu, {"novel_url_code": novel_code}
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
            params = {"messages": messages, "return_page": PageNovelMenu, "return_kwargs": self.args}

        last_y += 2
        screen.refresh()
        wait_for_user_input(screen, 2, last_y)
        return target, params
    
class PageNovelTranslateMetadata(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        storage = JsonStorage()

        # Print title
        last_y = print_title(screen, resources["title"], 0)

        while True:
            last_y += 2
            try:
                screen.print_at("Loading novel from local storage...", 2, last_y)
                screen.refresh()
                novels = storage.get_data()
                novel = [novel for novel in novels if novel.novel_code == novel_code][0]
                screen.print_at("Novel loaded successfully.", 2, last_y + 1)
                screen.refresh()
                last_y += 2
            except Exception as e:
                screen.print_at("Error loading novel from local storage.", 2, last_y)
                messages = [
                    f"Error: Error loading local storage.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageNovelMenu, "return_kwargs": {"novel_url_code": novel_code}}
                break

            try:
                screen.print_at("Initializing translator...", 2, last_y)
                screen.refresh()
                translator = GPTTranslatorJP2EN()
                screen.print_at("Translator initialized successfully.", 2, last_y + 1)
                screen.refresh()
                last_y += 2
            except Exception as e:
                screen.print_at("Error initializing translator.", 2, last_y)
                messages = [
                    f"Error: Error initializing translator.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageNovelMenu, "return_kwargs": {"novel_url_code": novel_code}}
                break
            
            try:
                # Translate novel metadata
                screen.print_at("Translating novel metadata...", 2, last_y)
                screen.refresh()
                exceptions = translator.translate_novel_metadata(novel)
                if exceptions:
                    screen.print_at(f"There were {len(exceptions)} errors while translating novel metadata.", 2, last_y + 1)
                    screen.refresh()
                    last_y += 2
                    for exception in exceptions:
                        screen.print_at(f"Error: {exception}", 2, last_y)
                        last_y += 1
                    screen.refresh()
                    last_y += 2
                    raise Exception("There were errors while translating novel metadata.")
                else:
                    screen.print_at("Novel metadata translated successfully.", 2, last_y + 1)
                    screen.refresh()
                    last_y += 2
            except Exception as e:
                screen.print_at("Error translating novel metadata.", 2, last_y)
                messages = [
                    f"Error: Error translating novel metadata.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageNovelMenu, "return_kwargs": {"novel_url_code": novel_code}}
                break

            try:
                screen.print_at("Saving novel to local storage...", 2, last_y)
                screen.refresh()
                storage.set_data(novels)
                screen.print_at("Novel saved to local storage.", 2, last_y + 1)
                target, params = PageNovelMenu, {"novel_url_code": novel_code}
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
    
class PageNovelScrapingTargets(PageTypeB):
    def __init__(self) -> None:
        super().__init__("novel_scraping_targets_menu")
    
class PageNovelTranslationTargets(PageTypeB):
    def __init__(self) -> None:
        super().__init__("novel_translating_targets_menu")
    
class PageNovelEditingTarget(PageTypeB):
    def __init__(self) -> None:
        super().__init__("novel_editing_targets_menu")
    
class PageNovelExportTargets(PageTypeB):
    def __init__(self) -> None:
        super().__init__("novel_export_targets_menu")

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
                wait_for_user_input
                messages = [
                    f"Error: Chapter targets parsing failed.",
                    f"Error: {e}"]
                target = PageMessage
                params = {"messages": messages, "return_page": PageNovelMenu, "return_kwargs": {"novel_url_code": novel_code}}
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
                params = {"messages": messages, "return_page": PageNovelMenu, "return_kwargs": {"novel_url_code": novel_code}}
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
                params = {"messages": messages, "return_page": PageNovelMenu, "return_kwargs": {"novel_url_code": novel_code}}
                break

            try:
                screen.print_at("Saving novel to local storage...", 2, last_y)
                screen.refresh()
                storage.set_data(novels)
                screen.print_at("Novel saved to local storage.", 2, last_y + 1)
                target, params = PageNovelMenu, {"novel_url_code": novel_code}
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

def navigate_items(screen, pre_y, pre_x, items, active_index=0):
    while True:
        for index, item in enumerate(items):
            y, x, trigger, label, _, content, is_text_box = item
            screen.print_at(label, x + pre_x, y + pre_y)

            if index == active_index:
                if is_text_box:
                    screen.print_at(label, x + pre_x, y + pre_y, attr=Screen.A_REVERSE)
                    screen.print_at(content, x + pre_x + len(label) + 1, y + pre_y)
                else:
                    screen.print_at(label, x + pre_x, y + pre_y, attr=Screen.A_REVERSE)
            else:
                if is_text_box:
                    screen.print_at(label, x + pre_x, y + pre_y)
                    screen.print_at(content, x + pre_x + len(label) + 1, y + pre_y)
                else:
                    screen.print_at(label, x + pre_x, y + pre_y)

        screen.refresh()

        event = screen.get_event()
        if isinstance(event, KeyboardEvent):
            key = event.key_code
            if key == screen.KEY_UP:
                active_index = (active_index - 1) % len(items)
            elif key == screen.KEY_DOWN:
                active_index = (active_index + 1) % len(items)
            elif 48 <= key <= 57:
                number = key - 48
                for index, item in enumerate(items):
                    y, x, trigger, label, _, content, is_text_box = item
                    if trigger == number:
                        active_index = index
                        break
                else:
                    continue
                break
            elif key == 10 or key == 13:
                y, x, trigger, label, target_index, content, is_text_box = items[active_index]
                if is_text_box:
                    screen.print_at(label + " ", x + pre_x, y + pre_y)
                    screen.refresh()
                    user_input = read_user_input(screen, x + pre_x + len(label) + 1, y + pre_y)
                    trg_y, trg_x, trg_trigger, trg_label, trg_target, _, trg_is_text_box = items[target_index]
                    items[target_index] = (trg_y, trg_x, trg_trigger, trg_label, trg_target, user_input, trg_is_text_box)
                else:
                    break

    return active_index

def main(screen):
    verbose = False

    config_file_path = os.path.join(os.getcwd(), "config", "config.yaml")

    persistent_data_file_path = os.path.join(os.getcwd(), "persistent_data.json")

    storage = JsonStorage()
    storage.initialize(persistent_data_file_path)

    while True:
        try:
            config = Config()
            config.load(config_file_path)
            openai_api.initialize(config.data.config.openai.api_key)
        except Exception as e:
            messages = [
                f"Error: Failed to load config file.",
                f"Path: {config_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        try:
            storage.get_data()
            page = PageNovelSelection
            parameters = {"novel_objects": []}
            break
        except JsonStorageFormatException as e:
            messages = [
                f"Error: Failed to parse persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break
        except JsonStorageFileException as e:
            pass
        except Exception as e:
            messages = [
                f"Error: Failed to load persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            break

        try:
            storage.set_data([])
            messages = [
                f"Error: Failed to find persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"We'll create a new one for you."]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageNovelSelection, "return_kwargs": {"novel_objects": []}}
        except JsonStorageException as e:
            messages = [
                f"Error: Failed to create persistent data file.",
                f"Path: {persistent_data_file_path}",
                f"Error: {e}"]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}

        break

    while True:
        try:
            page, parameters = page().show(screen, **parameters)
        except Exception as e:
            messages = [
                f"Error: {e}",
                f"Page: {page}",
                f"Parameters: {parameters}",
                f"Please report this error to the developer."]
            page = PageMessage
            parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}

        if page == PageExit:
            break


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, '')
    Screen.wrapper(main)