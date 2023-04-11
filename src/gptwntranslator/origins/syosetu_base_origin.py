from abc import abstractmethod
from bs4 import BeautifulSoup
from bs4.element import Tag as SoupTag

from gptwntranslator.models.chapter import Chapter
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.sub_chapter import SubChapter
from gptwntranslator.origins.base_origin import BaseOrigin
from gptwntranslator.origins.base_web_origin import BaseWebOrigin


class SyosetuBaseOrigin(BaseWebOrigin):
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
    
    def __init__(self, location: str) -> None:
        novel_path = "/"
        sub_chapter_path = "../"
        encoding = "utf-8"
        language = "ja"
        super().__init__(location, novel_path, sub_chapter_path, language, encoding)

    # @abstractmethod
    # def _get_soup(self, url: str) -> BeautifulSoup:
    #     pass

    def _get_title(self, soup: BeautifulSoup) -> str:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        title = soup.find('div', id='novel_contents').find('div', id='novel_color').find('p', class_='novel_title').text
        return title.strip('\n\t ')
    
    def _get_author(self, soup: BeautifulSoup) -> str:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        author_soup = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', class_='novel_writername')

        # Check if the author is a link
        if author_soup.find('a') is None:
            # The author is not a link
            author = author_soup.text.strip('\n\t ')
            if author.startswith('作者：'):
                author = author[3:]
            link = ""
        else:
            # The author is a link
            author = author_soup.find('a').text.strip('\n\t ')
            link = author_soup.find('a').get('href').strip('\n\t ')

        return author, link
    
    def _get_description(self, soup: BeautifulSoup) -> str:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        description = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', id='novel_ex').text
        return description.strip('\n\t ')
    
    def _get_index(self, soup: BeautifulSoup) -> BeautifulSoup:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        index = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', class_='index_box')
        return index
    
    def _process_index(self, index: SoupTag, novel_code: str) -> list[Chapter]:
        if not isinstance(index, SoupTag):
            raise ValueError(f"Index {index} should be a bs4.element.Tag object. its type is {type(index)}")
        if not isinstance(novel_code, str):
            raise ValueError(f"Novel code {novel_code} should be a string")

        # Initialize chapter list
        chapters = list()

        # Find chapter names
        chapter_names = index.find_all('div', class_='chapter_title')

        # Initialize chapter number
        chapter_number = 1

        if len(chapter_names) == 0:
            # The novel doesn't group sub chapters into chapters, so it's just one big chapter

            # Make chapter name
            chapter_name = "Chapters"

            # Get sub chapters
            sub_chapters = list()

            # Initialize sub chapter number
            sub_chapter_number = 1

            # Find sub chapters
            for sub_chapter in index.find_all('dl', class_='novel_sublist2'):
                # Get sub chapter name
                sub_chapter_name = sub_chapter.find('dd', class_='subtitle').find('a').text

                # Get sub chapter link
                sub_chapter_link = sub_chapter.find('dd', class_='subtitle').find('a')['href']
                sub_chapter_link = sub_chapter_link.split('/')[-1]

                # Get sub chapter release date
                sub_chapter_release_date = sub_chapter_link.rstrip('/').split('/')[-1]

                # Append sub chapter
                sub_chapters.append(SubChapter(
                    novel_code,
                    chapter_number,
                    sub_chapter_number,
                    sub_chapter_link,
                    sub_chapter_name,
                    "",
                    sub_chapter_release_date
                ))

                # Increment sub chapter number
                sub_chapter_number += 1

            # Append chapter
            chapters.append(Chapter(
                novel_code,
                chapter_number,
                chapter_name,
                sub_chapters=sub_chapters))

        else:
            # Find sub chapters relevant to each chapter
            for chapter_name in chapter_names:
                # Get chapter name
                chapter_name_str = chapter_name.text

                # Get sub chapters
                sub_chapters = list()

                # Initialize sub chapter number
                sub_chapter_number = 1

                # Find sub chapters
                while True:
                    # Get next element
                    next_element = chapter_name.next_sibling

                    # If it's None, it's the end of the index, so break
                    if next_element is None:
                        break

                    # If it's a div element, it's a chapter name, so break
                    if next_element.name == 'div':
                        break

                    # If it's a dl element, it's a sub chapter
                    if next_element.name == 'dl':
                        # Get sub chapter name
                        sub_chapter_name = next_element.find('dd', class_='subtitle').find('a').text

                        # Get sub chapter link
                        sub_chapter_link = next_element.find('dd', class_='subtitle').find('a')['href']
                        sub_chapter_link = sub_chapter_link.rstrip('/').split('/')[-1]

                        # Get sub chapter release date
                        sub_chapter_release_date = next_element.find('dt', class_='long_update').text

                        # Append sub chapter
                        sub_chapters.append(SubChapter(
                            novel_code,
                            chapter_number,
                            sub_chapter_number,
                            sub_chapter_link,
                            sub_chapter_name,
                            "",
                            sub_chapter_release_date
                        ))

                        # Increment sub chapter number
                        sub_chapter_number += 1
                        
                    # Set next element as current element
                    chapter_name = next_element

                # Append chapter
                chapters.append(Chapter(
                    novel_code,
                    chapter_number,
                    chapter_name_str,
                    sub_chapters=sub_chapters))

                # Increment chapter number
                chapter_number += 1
            
        return chapters

    def _get_sub_chapter_contents(self, soup: BeautifulSoup) -> str:
        if not isinstance(soup, BeautifulSoup):
            raise ValueError(f"Soup {soup} should be a BeautifulSoup object")
        
        sub_chapter_contents = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', id='novel_honbun').find_all('p')

        # Initialize sub chapter contents
        sub_chapter_text_contents = ""

        # Process sub chapter contents
        for sub_chapter_content in sub_chapter_contents:
            # If it's empty, it's a break, so skip it
            if sub_chapter_content.text == '':
                continue
            
            # If it contains a br element, it's a line skip, so add a line break
            if sub_chapter_content.find('br') is not None:
                sub_chapter_text_contents += "\n"
            # If it contains text, it's a paragraph, so add a paragraph
            elif sub_chapter_content.text != '':
                sub_chapter_text_contents += sub_chapter_content.text.strip('\n\t ') + "\n\n"

        return sub_chapter_text_contents
    
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
    #                     soup = self._get_soup(self.location + sub_chapter.link)

    #                     # Get sub chapter contents
    #                     sub_chapter_contents = self._get_sub_chapter_contents(soup)

    #                     # Set sub chapter contents
    #                     sub_chapter.contents = sub_chapter_contents

    #                 except Exception as e:
    #                     raise Exception("Failed to scrape " + self.location + sub_chapter.link + ": " + str(e))

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