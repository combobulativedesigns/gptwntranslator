class PageBase:
    def __init__(self) -> None:
        self.args = {}

    def show(self, screen, **kwargs) -> tuple[object, dict]:
        self.pre_render(screen, **kwargs)
        return self.render(screen, **kwargs)
    
    def pre_render(self, screen, **kwargs) -> None:
        self.args = kwargs
        screen.clear()

    def render(self, screen, **kwargs) -> tuple[object, dict]:
        pass

    def process_actions(self, page, content) -> tuple[object, dict]:
        pass