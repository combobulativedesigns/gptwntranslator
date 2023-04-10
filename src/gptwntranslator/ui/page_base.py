from abc import ABC, abstractmethod
from gptwntranslator.helpers.logger_helper import CustomLogger


logger = CustomLogger(__name__)

class PageBase(ABC):
    def __init__(self) -> None:
        self.args = {}

    def show(self, screen, **kwargs) -> tuple['PageBase', dict]:
        logger.debug(f"Showing page: {self.__class__.__name__}, args: {kwargs}")
        self.pre_render(screen, **kwargs)
        return self.render(screen, **kwargs)

    def pre_render(self, screen, **kwargs) -> None:
        self.args = kwargs
        screen.clear()

    @abstractmethod
    def render(self, screen, **kwargs) -> tuple['PageBase', dict]:
        pass

    def process_actions(self, item: object, content) -> tuple['PageBase', dict]:
        pass