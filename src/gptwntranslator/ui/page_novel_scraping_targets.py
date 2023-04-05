from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.page_novel_scraping import PageNovelScraping
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.page_type_b import PageTypeB
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelScrapingTargets(PageTypeB):
    def __init__(self) -> None:
        resources = get_resources()

        menu = {
            "message_lines": [
                "Please select the target chapters and sub chapters",
                "you wish to scrape. Leave blank to scrape all chapters.",
            ],
            "menu_items": [
                (0, 0, None, "Chapter selection pattern:", 1, "", True),
                (2, 0, 1, "1) Start scraping", PageNovelScraping, "", False),
                (3, 0, 2, "2) Pattern explanation", PageMessage, resources["chapter_regex_explanation"], False),
                (5, 0, 0, "0) Go back", PageReturn, "", False)]
        }  

        super().__init__(menu)