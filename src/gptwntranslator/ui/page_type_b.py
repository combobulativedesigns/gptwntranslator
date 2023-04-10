from gptwntranslator.helpers.ui_helper import UIMenuItem
from gptwntranslator.ui.page import Page
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.ui_resources import get_resources


class PageTypeB(Page):
    def __init__(self, menu: dict, pre_messages=None, post_messages=None) -> None:
        messages = menu["message_lines"]
        menu_items = menu["menu_items2"]
        self.pre_messages = pre_messages
        self.post_messages = post_messages
        super().__init__(messages, menu_items)
    
    def process_actions(self, item: UIMenuItem, content) -> tuple[PageBase, dict]:
        if item.page_target is PageMessage:
            return item.page_target, {**item.page_data, **{"return_page": self.__class__, "return_kwargs": self.args}}
        if item.page_target is PageReturn:
            return item.page_target, {**item.page_data, **{"return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}}
        return item.page_target, {**item.page_data, **{"novel_origin": self.args["novel_origin"], "novel_url_code": self.args["novel_url_code"], "return_page": self.__class__, "return_kwargs": self.args}}