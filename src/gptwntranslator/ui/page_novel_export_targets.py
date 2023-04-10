from gptwntranslator.helpers.ui_helper import UIMenuItem, UIMenuItemType
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.page_novel_exporting import PageNovelExporting
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.page_type_b import PageTypeB
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelExportTargets(PageTypeB):
    def __init__(self) -> None:
        resources = get_resources()

        menu_item_2 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 2, 0, 1, "Start exporting", None, None, PageNovelExporting, {"target": ""}, None)
        menu_item_1 = UIMenuItem(UIMenuItemType.TEXT_INPUT, 0, 0, None, "Chapter selection pattern:", menu_item_2, "target", None, None, None)
        menu_item_3 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 3, 0, 2, "Pattern explanation", None, None, PageMessage, {"messages": resources["chapter_regex_explanation"]}, None)
        menu_item_4 = UIMenuItem(UIMenuItemType.PAGE_NAVIGATION, 5, 0, 0, "Go back", None, None, PageReturn, {}, None)


        menu = {
            "message_lines": [
                "Please select the target chapters and sub chapters",
                "you wish to export. Leave blank to export all chapters.",
            ],
            "menu_items": [
                (0, 0, None, "Chapter selection pattern:", 1, "", True),
                (2, 0, 1, "1) Start exporting", PageNovelExporting, "", False),
                (3, 0, 2, "2) Pattern explanation", PageMessage, resources["chapter_regex_explanation"], False),
                (5, 0, 0, "0) Go back", PageReturn, "", False)
            ],
            "menu_items2": [
                menu_item_1,
                menu_item_2,
                menu_item_3,
                menu_item_4
            ]

        }
        
        super().__init__(menu)