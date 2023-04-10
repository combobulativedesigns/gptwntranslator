from gptwntranslator.helpers.ui_helper import UIMenuItem, UIMenuItemType
from gptwntranslator.origins.origin_factory import OriginFactory
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_novel_lookup import PageNovelLookup
from gptwntranslator.ui.page_type_a import PageTypeA


class PageNovelSelection(PageTypeA):
    def __init__(self) -> None:

        menu_item_1_items = OriginFactory.origin_names()

        menu_item_3 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 3, 0, 1, "Search novel", None, None, PageNovelLookup, {"novel_origin": "", "novel_url_code": ""}, None)
        menu_item_1 = UIMenuItem(UIMenuItemType.COMBO_BOX, 0, 0, None, "Novel origin:", menu_item_3, "novel_origin", None, None, menu_item_1_items)
        menu_item_2 = UIMenuItem(UIMenuItemType.TEXT_INPUT, 1, 0, None, "Novel URL code:", menu_item_3, "novel_url_code", None, None, None)
        menu_item_4 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 5, 0, 0, "Exit", None, None, PageExit, {}, None)

        menu = {
            "message_lines": [
                "Please enter the URL code of the novel you want to scrape. For example, the URL code of https://ncode.syosetu.com/n5177as/ is n5177as.",
            ],
            "menu_items": [
                (0, 0, None, "Novel URL code:", 1, "", True),
                (2, 0, 1, "1) Search novel", PageNovelLookup, "", False),
                (4, 0, 0, "0) Exit", PageExit, "", False)
            ],
            "menu_items2": [
                menu_item_1,
                menu_item_2,
                menu_item_3,
                menu_item_4
            ]
        }

        super().__init__(menu)

    def process_actions(self, item: UIMenuItem, content) -> tuple[PageBase, dict]:
        if item.page_target == PageExit:
            return item.page_target, {}
        return item.page_target, {**item.page_data, **{"return_page": self.__class__, "return_kwargs": {}}}