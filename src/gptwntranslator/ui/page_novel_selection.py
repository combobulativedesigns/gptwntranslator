from gptwntranslator.ui.page_exit import PageExit
from gptwntranslator.ui.page_novel_lookup import PageNovelLookup
from gptwntranslator.ui.page_type_a import PageTypeA


class PageNovelSelection(PageTypeA):
    def __init__(self) -> None:
        menu = {
            "message_lines": [
                "Please enter the URL code of the novel you want to scrape.",
                "For example, the URL code of https://ncode.syosetu.com/n5177as/",
                "is n5177as.",
            ],
            "menu_items": [
                (0, 0, None, "Novel URL code:", 1, "", True),
                (2, 0, 1, "1) Search novel", PageNovelLookup, "", False),
                (4, 0, 0, "0) Exit", PageExit, "", False)]
        }

        super().__init__(menu)

    def process_actions(self, item, content):
        if item[4] == PageNovelLookup:
            return item[4], {"novel_url_code": item[5], "return_page": self.__class__, "return_kwargs": {}}
        return item[4], {}