from gptwntranslator.ui.page import Page
from gptwntranslator.ui.ui_resources import get_resources


class PageTypeA(Page):
    def __init__(self, menu: dict, pre_messages=None, post_messages=None) -> None:
        messages = menu["message_lines"]
        menu_items = menu["menu_items"]
        super().__init__(messages, menu_items, pre_messages, post_messages)