from gptwntranslator.ui.page import Page
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.ui_resources import get_resources


class PageTypeB(Page):
    def __init__(self, menu: dict, pre_messages=None, post_messages=None) -> None:
        messages = menu["message_lines"]
        menu_items = menu["menu_items"]
        self.pre_messages = pre_messages
        self.post_messages = post_messages
        super().__init__(messages, menu_items)
    
    def process_actions(self, item, content) -> tuple[PageBase, dict]:
        if item[4] is PageMessage:
            return item[4], {"messages": item[5], "return_page": self.__class__, "return_kwargs": self.args}
        if item[4] is PageReturn:
            return item[4], {"return_page": self.args["return_page"], "return_kwargs": self.args["return_kwargs"]}
        return item[4], {"novel_url_code": self.args["novel_url_code"], "target": item[5], "return_page": self.__class__, "return_kwargs": self.args}