from abc import abstractmethod
from gptwntranslator.helpers.ui_helper import UIMenuItem
from gptwntranslator.ui.page import Page
from gptwntranslator.ui.page_base import PageBase


class PageTypeA(Page):
    def __init__(self, menu: dict, pre_messages=None, post_messages=None) -> None:
        messages = menu["message_lines"]
        menu_items = menu["menu_items2"]
        super().__init__(messages, menu_items, pre_messages, post_messages)

    @abstractmethod
    def process_actions(self, item: UIMenuItem, content) -> tuple[PageBase, dict]:
        pass