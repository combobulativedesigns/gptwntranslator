from types import NoneType
from gptwntranslator.helpers.logger_helper import CustomLogger
from gptwntranslator.helpers.ui_helper import navigate_items, print_title
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.ui_resources import get_resources


logger = CustomLogger(__name__)

class Page(PageBase):
    def __init__(self, messages: list[str], menu_items: list[tuple[int, int, int, str, PageBase, str, bool]], pre_messages: list[str]|NoneType = None, post_messages: list[str]|NoneType = None) -> None:
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
            logger.debug(f"active_index: {active_index}")
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