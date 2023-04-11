from abc import abstractmethod
import gzip
from typing import Callable
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4.element import Tag as SoupTag

from bs4 import BeautifulSoup
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.chapter import Chapter
from gptwntranslator.origins.base_origin import BaseOrigin


class BaseWebOrigin(BaseOrigin):
    @classmethod
    @property
    @abstractmethod
    def code(cls):
        pass

    @classmethod
    @property
    @abstractmethod
    def name(cls) -> str:
        pass
    
    def __init__(self, location: str, encoding: str) -> None:
        self.encoding = encoding
        super().__init__(location)

    def _conditional_decompression(self, html_bytes: bytes) -> str:
        if html_bytes.startswith(b"\x1f\x8b\x08"):
            return gzip.decompress(html_bytes)
        else:
            return html_bytes

    def _decode_html(self, html_bytes: bytes) -> str:
        methods: list[Callable[[bytes], str]] = [
            lambda x: x.decode(self.encoding),
            lambda x: gzip.decompress(x).decode(self.encoding),
            lambda x: self._conditional_decompression(x).decode(self.encoding, errors="ignore"),
        ]

        for method in methods:
            try:
                html = method(html_bytes)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise UnicodeDecodeError("Cannot decode the html")

        return html

    def _get_soup(self, url: str) -> BeautifulSoup:
        if not isinstance(url, str):
            raise ValueError(f"URL {url} should be a string")
        if not urlparse(url).scheme:
            raise ValueError(f"URL {url} should have a scheme")
        if not urlparse(url).netloc:
            raise ValueError(f"URL {url} should have a netloc")
        
        response = urlopen(url)
        html_bytes = response.read()
        html = self._decode_html(html_bytes)
        
        soup = BeautifulSoup(html, "html.parser")
        return soup
    
    @abstractmethod
    def _get_title(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def _get_author(self, soup: BeautifulSoup) -> str:
        pass
    
    @abstractmethod
    def _get_description(self, soup: BeautifulSoup) -> str:
        pass
    
    @abstractmethod
    def _get_index(self, soup: BeautifulSoup) -> BeautifulSoup:
        pass
    
    @abstractmethod
    def _process_index(self, index: SoupTag, novel_code: str) -> list[Chapter]:
        pass

    @abstractmethod
    def _get_sub_chapter_contents(self, soup: BeautifulSoup) -> str:
        pass
    
    def process_targets(self, novel: Novel, targets: dict[str, list[str]]) -> None:
        if not isinstance(novel, Novel):
            raise ValueError(f"Novel {novel} should be a Novel object")
        if not isinstance(targets, dict):
            raise ValueError(f"Targets {targets} should be a dictionary")
        if not all(isinstance(key, str) for key in targets.keys()):
            raise ValueError(f"Targets keys {targets.keys()} should be strings")
        if not all(isinstance(value, list) for value in targets.values()):
            raise ValueError(f"Targets values {targets.values()} should be lists")
        if not all(isinstance(item, str) for value in targets.values() for item in value):
            raise ValueError(f"Targets items {targets.items()} should be strings")

        for chapter in novel.chapters:
            chapter.sub_chapters.sort()

            if targets is not None:
                if str(chapter.chapter_index) not in targets:
                    continue

                sub_chapter_targets = targets[str(chapter.chapter_index)]
                for sub_chapter in chapter.sub_chapters:
                    if len(sub_chapter_targets) > 0 and str(sub_chapter.sub_chapter_index) not in sub_chapter_targets:
                        continue

                    try:
                        soup = self._get_soup(sub_chapter.link)
                        sub_chapter_contents = self._get_sub_chapter_contents(soup)
                        sub_chapter.contents = sub_chapter_contents

                    except Exception as e:
                        raise Exception("Failed to scrape " + sub_chapter.link + ": " + str(e))

    def process_novel(self, novel_identifier: str) -> None:
        if not isinstance(novel_identifier, str):
            raise ValueError(f"Novel identifier {novel_identifier} should be a string")
        
        url = self.location + novel_identifier
        
        try:
            soup = self._get_soup(url)
            title = self._get_title(soup)
            author, link = self._get_author(soup)
            description = self._get_description(soup)
            index = self._get_index(soup)
            chapters = self._process_index(index, novel_identifier)
        except Exception as e:
            raise Exception("Failed to scrape " + url + ": " + str(e))
        
        chapters.sort()

        return Novel(
            self.__class__.code,
            novel_identifier,
            title,
            author,
            description,
            "ja",
            author_link=link,
            chapters=chapters)

