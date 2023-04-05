from gptwntranslator.ui.page_base import PageBase


class PageReturn(PageBase):
    def __init__(self) -> None:
        pass

    def render(self, screen, **kwargs) -> tuple[PageBase, dict]:
        return kwargs["return_page"], kwargs["return_kwargs"]