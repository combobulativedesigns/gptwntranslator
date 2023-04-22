

from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.ui_helper import UIMenuItem, UIMenuItemType
from gptwntranslator.storage.json_storage import JsonStorage
from gptwntranslator.ui.page import Page
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_novel_menu import PageNovelMenu
from gptwntranslator.ui.page_novel_selection import PageNovelSelection


class PageNovelList(Page):
    def __init__(self) -> None:
        messages = [
            "Welcome to gptwntranslator!",
            "Please select a novel to translate or download a new one."
        ]
        menu_items = [
            UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 0, 0, 1, "Download a new novel", None, None, PageNovelSelection, {}, None),
            UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 12, 0, 0, "Exit", None, None, PageExit, {}, None)
        ]
        super().__init__(messages, menu_items)

    def pre_render(self, screen, **kwargs) -> None:
        super().pre_render(screen, **kwargs)
        cf = Config()
        target_language = cf.data.config.translator.target_language
        storage = JsonStorage()
        current_page_index = kwargs["page_index"]

        novel_title_length = 60
        novels_per_page_count = 6
        novels = storage.get_data()
        novels_count = len(novels)

        novels_page_count = novels_count // novels_per_page_count
        if novels_page_count == 0:
            novels_page_count = 1
        elif novels_count % novels_per_page_count != 0:
            novels_page_count += 1
        current_page_index = current_page_index % novels_page_count
        novels_start_index = current_page_index * novels_per_page_count
        novels_end_index = novels_start_index + novels_per_page_count
        novels_end_index = novels_end_index if novels_end_index < novels_count else novels_count
        current_novels = novels[novels_start_index:novels_end_index]
        for index, novel in enumerate(current_novels):
            if target_language not in novel.title_translation:
                title = novel.title
            else:
                title = novel.title_translation[target_language]
            if len(title) > novel_title_length:
                title = title[:int(novel_title_length-3)] + "..."
            menu_item = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, int(index + 2), 0, None, f"- {title}", None, None, PageNovelMenu, {"novel_origin": novel.novel_origin, "novel_url_code": novel.novel_code}, None)
            self.menu_items.append(menu_item)
        for index in range(len(self.menu_items), novels_per_page_count + 2):
            menu_item = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, int(index), 0, None, "(Empty)", None, None, PageNovelList, {"page_index": current_page_index}, None)
            self.menu_items.append(menu_item)


        menu_item = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 9, 0, 2, "Previous page", None, None, PageNovelList, {"page_index": current_page_index - 1}, None)
        self.menu_items.append(menu_item)
        menu_item = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 10, 0, 3, "Next page", None, None, PageNovelList, {"page_index": current_page_index + 1}, None)
        self.menu_items.append(menu_item)
        self.menu_items.sort(key=lambda x: x.y_offset)

    def process_actions(self, item: UIMenuItem, content) -> tuple[PageBase, dict]:
        if item.page_target == PageExit:
            return item.page_target, {}
        return item.page_target, {**item.page_data, **{"return_page": self.__class__, "return_kwargs": self.args}}