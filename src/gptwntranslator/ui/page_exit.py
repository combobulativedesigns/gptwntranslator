import asyncio
import sys
from gptwntranslator.helpers.ui_helper import print_title, wait_for_user_input
from gptwntranslator.ui.page_base import PageBase
from gptwntranslator.ui.ui_resources import get_resources


class PageExit(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        resources = get_resources()

        while True:
            last_y = print_title(screen, resources["title"], 0)

            last_y += 2
            screen.print_at("Goodbye!", 2, last_y)
        
            # Stop shit

            last_y += 2
            screen.refresh()
            wait_for_user_input(screen, 2, last_y)

            break

        sys.exit(0)