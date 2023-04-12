from abc import abstractmethod
from types import NoneType
from gptwntranslator.helpers.logger_helper import CustomLogger
from gptwntranslator.helpers.ui_helper import UIMenuItem, navigate_items, print_messages, print_title
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.ui_resources import get_resources


logger = CustomLogger(__name__)

class Page(PageBase):
    def __init__(self, messages: list[str], menu_items: list[UIMenuItem], pre_messages: list[str]|NoneType = None, post_messages: list[str]|NoneType = None) -> None:
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
                last_y = print_messages(screen, self.pre_messages, 2, last_y)
            else:
                last_y += 1

            last_y += 1
            last_y = print_messages(screen, self.messages, 2, last_y)

            if self.post_messages is not None:
                last_y += 1
                last_y = print_messages(screen, self.post_messages, 2, last_y)
            else:
                last_y += 1

            screen.refresh()
            active_index = navigate_items(screen, last_y, 2, self.menu_items)
            logger.debug(f"active_index: {active_index}")
            item = self.menu_items[active_index]

            if item.page_target is not None:
                page, content = self.process_actions(item, active_index)
                if page is not None:
                    return page, content
                else:
                    break
            else:
                break

        return None, {}

    @abstractmethod
    def process_actions(self, item: UIMenuItem, content) -> tuple[PageBase, dict]:
        pass