from gptwntranslator.ui.page_message import PageMessage
from gptwntranslator.ui.page_novel_translating import PageNovelTranslating
from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.page_type_b import PageTypeB
from gptwntranslator.ui.ui_resources import get_resources


class PageNovelTranslationTargets(PageTypeB):
    def __init__(self) -> None:
        resources = get_resources()

        menu = {
            "message_lines": [
                "Please select the target chapters and sub chapters",
                "you wish to translate. Leave blank to translate all chapters.",
            ],
            "menu_items": [
                (0, 0, None, "Chapter selection pattern:", 1, "", True),
                (2, 0, 1, "1) Start translating", PageNovelTranslating, "", False),
                (3, 0, 2, "2) Pattern explanation", PageMessage, resources["chapter_regex_explanation"], False),
                (5, 0, 0, "0) Go back", PageReturn, "", False)]
        }  

        super().__init__(menu)