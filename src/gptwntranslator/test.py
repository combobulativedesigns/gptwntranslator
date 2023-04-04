import curses
import os
import locale
from types import NoneType
import unicodedata
import unidecode

from wcwidth import wcswidth

from gptwntranslator.storage.json_storage import JsonStorage, JsonStorageException, JsonStorageFormatException, JsonStorageFileException
from gptwntranslator.models.novel import Novel
from gptwntranslator.scrapers.syosetu_scraper import process_novel


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
        "Sub-chapter numbers are also represented by one or more digits (e.g., \"4\" or \"23\")."]

    # Main menu options
    resources["novel_selection_menu"] = {
        "message_lines": [
            "Please enter the URL code of the novel you want to scrape.",
            "You can find the URL code in the URL of the novel's page.",
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
            "Tool for scraping and translating novels from the web.",
            "Please select an option from the menu below.",
        ],
        "menu_items": [
            (0, 0, 1, "1) Scrape new data", PageNovelScrapingTargets, "", False), 
            (1, 0, 2, "2) Translate novel", PageNovelTranslationTargets, "", False), 
            (2, 0, 3, "3) Edit novel", PageNovelEditingTarget, "", False), 
            (3, 0, 4, "4) Export novel", PageNovelExportTargets, "", False), 
            (5, 0, 0, "0) Go back", PageReturn, PageNovelSelection, False)]
    }

    resources["novel_scraping_targets_menu"] = {
        "message_lines": [
            "Please select the target chapters and sub chapters",
            "you wish to scrape. Leave blank to scrape all chapters.",
        ],
        "menu_items": [
            (0, 0, None, "Chapter selection pattern:", 1, "", True),
            (2, 0, 1, "1) Start scraping", PageNovelLookup, "", False),
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

def print_title(stdscr, title, y):
    for line in title:
        y += 1
        x = 2
        stdscr.addstr(y, x, line)

    return y

class PageBase:
    def __init__(self) -> None:
        pass

    def show(self, stdscr, **kwargs) -> tuple[object, dict]:
        self.pre_render(stdscr, **kwargs)
        return self.render(stdscr, **kwargs)
    
    def pre_render(self, stdscr, **kwargs) -> None:
        stdscr.clear()

    def render(self, stdscr, **kwargs) -> tuple[object, dict]:
        pass

    def process_actions(self, page, content) -> tuple[object, dict]:
        pass

class PageMessage(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, stdscr, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()

        last_y = print_title(stdscr, resources["title"], 0)

        last_y += 1
        for message in kwargs["messages"]:
            last_y += 1
            stdscr.addstr(last_y, 2, message)

        last_y += 2

        stdscr.addstr(last_y, 2, "Press any key to continue...")

        stdscr.refresh()

        stdscr.getch()

        return kwargs["return_page"], kwargs["return_kwargs"]
    
class PageExit(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, stdscr, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()

        while True:
            last_y = print_title(stdscr, resources["title"], 0)

            last_y += 1
            stdscr.addstr(last_y, 2, "Exiting program...")

            last_y += 2
            stdscr.addstr(last_y, 2, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()

            break

class PageReturn(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, stdscr, **kwargs) -> tuple[PageBase, dict]:
        return kwargs["return_page"], kwargs["return_kwargs"]

def fix_double_width_characters(text: str) -> str:
    for char in text:
        if unicodedata.east_asian_width(char) == "W":
            text = text.replace(char, char + " ")

    return text
    

class Page(PageBase):
    def __init__(self, item_code: str, messages: list[str], menu_items: list[tuple[int, int, int, str, PageBase, str, bool]], pre_messages: list[str]|NoneType = None, post_messages: list[str]|NoneType = None) -> None:
        self.item_code = item_code
        self.messages = messages
        self.menu_items = menu_items
        self.pre_messages = pre_messages
        self.post_messages = post_messages

        resources = get_resources()
        self.title = resources["title"]
        self.args = {}

    def pre_render(self, stdscr, **kwargs) -> None:
        self.args = kwargs
        super().pre_render(stdscr, **kwargs)

    def render(self, stdscr, **kwargs) -> tuple[PageBase, dict]:
        while True:
            stdscr.clear()

            # Print title
            last_y = print_title(stdscr, self.title, 0)

            if self.pre_messages is not None:
                last_y += 2
                for message in self.pre_messages:
                    stdscr.addstr(last_y, 2, message)
                    last_y += 1
            else:
                last_y += 1

            last_y += 1
            for message in self.messages:
                stdscr.addstr(last_y, 2, message)
                last_y += 1

            if self.post_messages is not None:
                last_y += 1
                for message in self.post_messages:
                    stdscr.addstr(last_y, 2, message)
                    last_y += 1
            else:
                last_y += 1

            stdscr.refresh()
            active_index = navigate_items(stdscr, last_y, 2, self.menu_items)
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

    def render(self, stdscr, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()
        novel_code = kwargs["novel_url_code"]
        storage = JsonStorage()

        # Print title
        last_y = print_title(stdscr, resources["title"], 0)

        last_y += 2
        stdscr.addstr(last_y, 2, "Novel Code: " + novel_code)
        stdscr.addstr(last_y + 1, 2, "Checking local storage...")
        stdscr.refresh()

        last_y += 2
        # Check if novel is already in local storage
        try:
            novels = storage.get_data()
        except Exception as e:
            stdscr.addstr(last_y, 2, "Error loading local storage.")
            last_y += 1
            stdscr.addstr(last_y, 2, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            messages = [
                f"Error: Error loading local storage.",
                f"Error: {e}"]
            target = PageMessage
            params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            return target, params
        
        if novel_code in [novel.novel_code for novel in novels]:
            stdscr.addstr(last_y, 2, "Novel already in local storage.")
            target, params = PageNovelMenu, {"novel_url_code": novel_code}
        else:
            stdscr.addstr(last_y, 2, "Novel not in local storage.")
            last_y += 1
            stdscr.addstr(last_y, 2, "Scraping Syosetu...")
            stdscr.refresh()

            try:
                # Scrape novel
                novel = process_novel(novel_code)
                last_y += 1
                stdscr.addstr(last_y, 2, "Novel scraped successfully.")
                last_y += 1
                stdscr.addstr(last_y, 2, "Saving novel to local storage...")
                stdscr.refresh()
                try:
                    # Save novel to local storage
                    novels.append(novel)
                    storage.set_data(novels)
                    last_y += 1
                    stdscr.addstr(last_y, 2, "Novel saved to local storage.")
                    target, params = PageNovelMenu, {"novel_url_code": novel_code}
                except Exception as e:
                    last_y += 1
                    stdscr.addstr(last_y, 2, "Novel saving failed.")
                    messages = [
                        f"Error: Novel saving failed.",
                        f"Error: {e}"]
                    target = PageMessage
                    params = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
            except Exception as e:
                last_y += 1
                stdscr.addstr(last_y, 2, "Novel scraping failed.")
                target, params = PageNovelSelection, {}
    
        last_y += 2
        stdscr.addstr(last_y, 2, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()
        return target, params

def str_to_unicode(s):
    return u''.join(r'\u{:04X}'.format(ord(chr)) for chr in s)

class PageNovelMenu(PageTypeA):
    def __init__(self) -> None:
        super().__init__("novel_menu")

    def pre_render(self, stdscr, **kwargs) -> None:
        super().pre_render(stdscr, **kwargs)
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


# Initialize the curses environment
def init_curses():
    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)
    stdscr.encoding = 'utf-8'
    locale.setlocale(locale.LC_ALL, '')
    return stdscr

# Clean up and close the curses environment
def close_curses(stdscr):
    stdscr.keypad(False)
    curses.echo()
    curses.nocbreak()
    curses.endwin()

def navigate_items(stdscr, pre_y, pre_x, items, active_index=0):
    while True:
        for index, item in enumerate(items):
            y, x, trigger, label, _, content, is_text_box = item
            stdscr.addstr(y + pre_y, x + pre_x, label)

            if index == active_index:
                if is_text_box:
                    stdscr.addstr(y + pre_y, x + pre_x, label, curses.A_REVERSE)
                    stdscr.addstr(y + pre_y, x + pre_x + len(label) + 1, content)
                else:
                    stdscr.addstr(y + pre_y, x + pre_x, label, curses.A_REVERSE)
            else:
                if is_text_box:
                    stdscr.addstr(y + pre_y, x + pre_x, label)
                    stdscr.addstr(y + pre_y, x + pre_x + len(label) + 1, content)
                else:
                    stdscr.addstr(y + pre_y, x + pre_x , label)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            active_index = (active_index - 1) % len(items)
        elif key == curses.KEY_DOWN:
            active_index = (active_index + 1) % len(items)
        # Check number keys
        elif key >= 48 and key <= 57:
            number = key - 48
            for index, item in enumerate(items):
                y, x, trigger, label, _, content, is_text_box = item
                if trigger == number:
                    active_index = index
                    break
            else:
                continue
            break

        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            y, x, trigger, label, target_index, content, is_text_box = items[active_index]
            if is_text_box:
                curses.echo()
                curses.curs_set(1)
                stdscr.addstr(y + pre_y, x + pre_x, label + " " * (len(content) + 1))
                stdscr.refresh()
                user_input = stdscr.getstr(y + pre_y, x + pre_x + len(label) + 1).decode("utf-8")
                trg_y, trg_x, trg_trigger, trg_label, trg_target, _, trg_is_text_box = items[target_index]
                items[target_index] = (trg_y, trg_x, trg_trigger, trg_label, trg_target, user_input, trg_is_text_box)
                curses.noecho()
                curses.curs_set(0)
            else:
                break

    return active_index

def main(stdscr):
    # Set verbose flag
    verbose = False

    # Set the configuration file path
    config_file_path = os.path.join(os.path.dirname(__file__), "config.json")

    # Set the persistent data file path
    persistent_data_file_path = os.path.join(os.getcwd(), "persistent_data.json")

    # Get storage
    storage = JsonStorage()
    storage.initialize(persistent_data_file_path)

    # Load the configuration file

    # Load the persistent data file
    try:
        storage.get_data()
        page = PageNovelSelection
        parameters = {"novel_objects": []}
    except JsonStorageFileException as e:
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
    except JsonStorageFormatException as e:
        messages = [
            f"Error: Failed to parse persistent data file.",
            f"Path: {persistent_data_file_path}",
            f"Error: {e}"]
        page = PageMessage
        parameters = {"messages": messages, "return_page": PageExit, "return_kwargs": {}}
    
    while True:
        try:
            page, parameters = page().show(stdscr, **parameters)
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
    stdscr = init_curses()
    try:
        curses.wrapper(main)
    finally:
        close_curses(stdscr)