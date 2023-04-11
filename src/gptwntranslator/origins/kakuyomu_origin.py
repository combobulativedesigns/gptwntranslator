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

    # def _get_soup(self, url: str) -> BeautifulSoup:
    #     if not isinstance(url, str):
    #         raise ValueError(f"URL {url} should be a string")
    #     if not urlparse(url).scheme:
    #         raise ValueError(f"URL {url} should have a scheme")
    #     if not urlparse(url).netloc:
    #         raise ValueError(f"URL {url} should have a netloc")
        
    #     response = urlopen(url)
    #     html_bytes = response.read()

    #     while True:
    #         try:
    #             html = html_bytes.decode("utf-8", errors="replace")
    #             break
    #         except UnicodeDecodeError:
    #             pass

    #         # try:
    #         #     html = html_bytes.decode("GB18030", errors="replace")
    #         #     break
    #         # except UnicodeDecodeError:
    #         #     pass

    #         # try:
    #         #     html = gzip.decompress(html_bytes).decode("GB18030", errors="replace")
    #         #     break
    #         # except UnicodeDecodeError:
    #         #     pass

    #         # try:
    #         #     html = gzip.decompress(html_bytes).decode("utf-8", errors="replace")
    #         #     break
    #         # except UnicodeDecodeError:
    #         #     pass

    #         raise UnicodeDecodeError("Cannot decode the html")
        
    #     soup = BeautifulSoup(html, "html.parser")
    #     return soup
    
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
        
        description_items = soup.find("p", {"id": "introduction"}).find_all()
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
        
    # def process_targets(self, novel: Novel, targets: dict[str, list[str]]) -> None:
    #     if not isinstance(novel, Novel):
    #         raise ValueError(f"Novel {novel} should be a Novel object")
    #     if not isinstance(targets, dict):
    #         raise ValueError(f"Targets {targets} should be a dictionary")
    #     if not all(isinstance(key, str) for key in targets.keys()):
    #         raise ValueError(f"Targets keys {targets.keys()} should be strings")
    #     if not all(isinstance(value, list) for value in targets.values()):
    #         raise ValueError(f"Targets values {targets.values()} should be lists")
    #     if not all(isinstance(item, str) for value in targets.values() for item in value):
    #         raise ValueError(f"Targets items {targets.items()} should be strings")
        
    #     for chapter in novel.chapters:
    #         chapter.sub_chapters.sort()

    #         if targets is not None:
    #             if str(chapter.chapter_index) not in targets:
    #                 continue

    #             sub_chapter_targets = targets[str(chapter.chapter_index)]
    #             for sub_chapter in chapter.sub_chapters:
    #                 if len(sub_chapter_targets) > 0 and str(sub_chapter.sub_chapter_index) not in sub_chapter_targets:
    #                     continue

    #                 try:
    #                     # Get soup
    #                     soup = self._get_soup(sub_chapter.link)

    #                     # Get sub chapter contents
    #                     sub_chapter_contents = self._get_sub_chapter_contents(soup)

    #                     # Set sub chapter contents
    #                     sub_chapter.contents = sub_chapter_contents

    #                 except Exception as e:
    #                     raise Exception("Failed to scrape " + sub_chapter.link + ": " + str(e))
                    
    # def process_novel(self, novel_identifier: str) -> None:
    #     if not isinstance(novel_identifier, str):
    #         raise ValueError(f"Novel identifier {novel_identifier} should be a string")
        
    #     url = self.location + novel_identifier
        
    #     try:
    #         # Get soup
    #         soup = self._get_soup(url)

    #         # Get title
    #         title = self._get_title(soup)

    #         # Get author
    #         author, link = self._get_author(soup)

    #         # Get description
    #         description = self._get_description(soup)

    #         # Get index
    #         index = self._get_index(soup)

    #         # Process index
    #         chapters = self._process_index(index, novel_identifier)
    #     except Exception as e:
    #         raise Exception("Failed to scrape " + url + ": " + str(e))
        
    #     chapters.sort()

    #     return Novel(
    #         self.__class__.code,
    #         novel_identifier,
    #         title,
    #         author,
    #         description,
    #         "ja",
    #         author_link=link,
    #         chapters=chapters)