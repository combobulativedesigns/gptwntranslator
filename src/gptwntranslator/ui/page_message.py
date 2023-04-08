

from gptwntranslator.helpers.logger_helper import CustomLogger
from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.ui_resources import get_resources


logger = CustomLogger(__name__)

class PageMessage(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()

        last_y = print_title(screen, resources["title"], 0)

        last_y += 1
        for message in kwargs["messages"]:
            last_y += 1
            screen.print_at(message, 2, last_y)

        last_y += 2

        logger.debug(f"kwargs: {kwargs}")

        screen.refresh()
        wait_for_user_input(screen, 2, last_y)

        return kwargs["return_page"], kwargs["return_kwargs"]