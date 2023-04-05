from gptwntranslator.ui.page_return import PageReturn
from gptwntranslator.ui.page_type_b import PageTypeB


class PageNovelEditingTarget(PageTypeB):
    def __init__(self) -> None:
        menu = {
            "message_lines": [
                "Please select the target chapter you whish to edit.",
            ],
            "menu_items": [
                (0, 0, None, "Chapter selection pattern:", 1, "", True),
                (2, 0, 1, "1) Start editing", PageReturn, "", False),
                (4, 0, 0, "0) Go back", PageReturn, "", False)]
        }

        super().__init__(menu)