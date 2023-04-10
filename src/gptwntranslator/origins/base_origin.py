from abc import ABC, abstractmethod


class BaseOrigin(ABC):
    @classmethod
    @property
    @abstractmethod
    def code(cls) -> str:
        pass

    @classmethod
    @property
    @abstractmethod
    def name(cls) -> str:
        pass

    def __init__(self, location: str) -> None:
        self.location = location

    @abstractmethod
    def process_novel(self, novel_identifier: str) -> None:
        pass

    @abstractmethod
    def process_targets(self, chapter_targets: str) -> None:
        pass