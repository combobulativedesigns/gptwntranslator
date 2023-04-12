import gzip
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4.element import Tag as SoupTag
from gptwntranslator.models.chapter import Chapter
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.sub_chapter import SubChapter
from gptwntranslator.origins.base_origin import BaseOrigin
from gptwntranslator.origins.base_web_origin import BaseWebOrigin


class KakuyomuOrigin(BaseWebOrigin):
    @classmethod
    @property
    def code(cls):
        return "kakuyomu"
    
    @classmethod
    @property
    def name(cls):
        return "Kakuyomu"
    
    def __init__(self) -> None:
        location = "https://kakuyomu.jp"
        novel_path = "/works/"
        sub_chapter_path = "../episodes/"
        encoding = "utf-8"
        language = "ja"
        super().__init__(location, novel_path, sub_chapter_path, language, encoding)
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        title = soup.find("h1", {"id": "workTitle"}).find("a").text
        return title.strip('\r\n\t ')
    
    def _get_author(self, soup: BeautifulSoup) -> str:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        author_soup = soup.find("span", {"id": "workAuthor-activityName"}).find("a")
        author = author_soup.text.strip('\r\n\t ')
        link = author_soup["href"]
        return author, link
    
    def _get_description(self, soup: BeautifulSoup) -> str:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        description_items = soup.find("p", {"id": "introduction"}).contents
        description = ""

        for item in description_items:
            if isinstance(item, SoupTag):
                if item.name == "br":
                    description += "\n"
                else:
                    description += item.text.strip('\r\n\t ')
            else:
                description += item.strip('\r\n\t ')

        return description
    
    def _get_index(self, soup: BeautifulSoup) -> SoupTag:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        index = soup.find("div", {"id": "table-of-contents"}).find("section", {"class": "widget-toc"}).find("div", {"class": "widget-toc-main"}).find("ol", {"class": "widget-toc-items"})
        return index
    
    def _process_index(self, index: SoupTag, novel_code: str) -> list[Chapter]:
        if not isinstance(index, SoupTag):
            raise ValueError(f"Index {index} should be a bs4.element.Tag object")
        if not isinstance(novel_code, str):
            raise ValueError(f"Novel code {novel_code} should be a string")
        
        chapters = []
        chapter_names = index.find_all("li", {"class": "widget-toc-chapter"})

        chapter_number = 1
        if len(chapter_names) == 0:
            chapter_name = 'Chapters'
            sub_chapters = list()
            sub_chapter_number = 1

            for sub_chapter in index.find_all("li", {"class": "widget-toc-episode"}):
                sub_chapter_name = sub_chapter.find("span", {"class": "widget-toc-episode-titleLabel"}).text.strip('\r\n\t ')
                sub_chapter_link = sub_chapter.find("a", {"class": "widget-toc-episode-episodeTitle"})["href"].rstrip("/").split("/")[-1]
                sub_chapter_release_date = sub_chapter.find("time", {"class": "widget-toc-episode-datePublished"})["datetime"]

                sub_chapters.append(SubChapter(
                    novel_code,
                    chapter_number,
                    sub_chapter_number,
                    sub_chapter_link,
                    sub_chapter_name,
                    "",
                    sub_chapter_release_date))
                
                sub_chapter_number += 1

            chapters.append(Chapter(
                novel_code,
                chapter_number,
                chapter_name,
                sub_chapters=sub_chapters))
            
        else:
            for chapter_name in chapter_names:
                chapter_name_str = chapter_name.find("span").text.strip('\r\n\t ')
                sub_chapters = list()
                sub_chapter_number = 1

                while True:
                    next_element = chapter_name.next_sibling

                    if next_element is None:
                        break

                    if isinstance(next_element, SoupTag) and "class" in next_element.attrs and "widget-toc-chapter" in next_element.attrs["class"]:
                        break

                    if isinstance(next_element, SoupTag) and "class" in next_element.attrs and "widget-toc-episode" in next_element.attrs["class"]:
                        sub_chapter_name = next_element.find("span", {"class": "widget-toc-episode-titleLabel"}).text.strip('\r\n\t ')
                        sub_chapter_link = next_element.find("a", {"class": "widget-toc-episode-episodeTitle"})["href"].rstrip("/").split("/")[-1]
                        sub_chapter_release_date = next_element.find("time", {"class": "widget-toc-episode-datePublished"})["datetime"]

                        sub_chapters.append(SubChapter(
                            novel_code,
                            chapter_number,
                            sub_chapter_number,
                            sub_chapter_link,
                            sub_chapter_name,
                            "",
                            sub_chapter_release_date))
                        
                        sub_chapter_number += 1

                    chapter_name = next_element

                chapters.append(Chapter(
                    novel_code,
                    chapter_number,
                    chapter_name_str,
                    sub_chapters=sub_chapters))
                
                chapter_number += 1

        return chapters
    
    def _get_sub_chapter_contents(self, soup: BeautifulSoup) -> str:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        sub_chapter_contents = soup.find("div", {"id": "contentMain-inner"}).find("div", {"class": "widget-episodeBody"}).find_all("p")
        sub_chapter_text_contents = ""

        for sub_chapter_content in sub_chapter_contents:
            if "class" in sub_chapter_content.attrs and "blank" in sub_chapter_content.attrs["class"]:
                sub_chapter_text_contents += "\n\n"
            else:
                sub_chapter_text_contents += sub_chapter_content.text.strip('\r\n\t ') + "\n\n"

        return sub_chapter_text_contents.strip('\r\n\t ')