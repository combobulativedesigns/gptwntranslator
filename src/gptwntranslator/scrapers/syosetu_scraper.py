"""This module contains functions aiding in scraping novels from syosetu.com."""

import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
from gptwntranslator.helpers.text_helper import make_printable

from gptwntranslator.models.chapter import Chapter
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.sub_chapter import SubChapter


def _get_soup(url: str) -> BeautifulSoup:
    """Get the BeautifulSoup object of the given URL.
    
    Parameters
    ----------
    url : str
        The URL to get the BeautifulSoup object of.

    Returns
    -------
    BeautifulSoup
        The soup of the given URL.
    """

    # Validate parameters
    if not isinstance(url, str):
        raise TypeError("URL must be a string")

    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def _get_title(soup: BeautifulSoup) -> str:
    """Get the title of the novel.

    Parameters
    ----------
    soup : BeautifulSoup
        The soup of the novel.

    Returns
    -------
    str
        The title of the novel.
    """

    # Validate parameters
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("Soup must be a BeautifulSoup object")

    # Find element that contains the title
    # It's found at div#novel_contents > div#novel_color > p.novel_title
    title = soup.find('div', id='novel_contents').find('div', id='novel_color').find('p', class_='novel_title').text
    return title.strip('\n\t ')

def _get_author(soup: BeautifulSoup) -> tuple[str, str]:
    """Get the author of the novel.

    Parameters
    ----------
    soup : BeautifulSoup
        The soup of the novel.

    Returns
    -------
    tuple[str, str]
        The author of the novel, and the link to their profile.
    """

    # Validate parameters
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("Soup must be a BeautifulSoup object")

    # Find element that contains the author
    # It's found at div#novel_contents > div#novel_color > div.novel_writername
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

def _get_description(soup: BeautifulSoup) -> str:
    """Get the description of the novel.

    Parameters
    ----------
    soup : BeautifulSoup
        The soup of the novel.

    Returns
    -------
    str
        The description of the novel.
    """

    # Validate parameters
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("Soup must be a BeautifulSoup object")

    # Find element that contains the description
    # It's found at div#novel_contents > div#novel_color > div#novel_ex
    description = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', id='novel_ex').text
    return description.strip('\n\t ')

def _get_index(soup: BeautifulSoup) -> BeautifulSoup:
    """Get the index of the novel.

    Parameters
    ----------
    soup : BeautifulSoup
        The soup of the novel.

    Returns
    -------
    BeautifulSoup
        The index of the novel.
    """

    # Validate parameters
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("Soup must be a BeautifulSoup object")

    # Find element that contains the chapters
    # It's found at div#novel_contents > div#novel_color > div#index_box
    index = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', class_='index_box')
    return index

def _process_index(index: BeautifulSoup, novel_code: str) -> list[Chapter]:
    """Process the index of the novel.

    Parameters
    ----------
    index : BeautifulSoup
        The index of the novel.
    novel_code : str
        The code of the novel.

    Returns
    -------
    list[Chapter]
        The chapters of the novel.
    """

    # Process the index to get the chapter links
    # The div elements that contain the chapter names are found at div.chapter_title elements
    # The sub chapters are found at dl.novel_sublist2 > dd.subtitle > a, with their release date found at dl.novel_sublist2 > dt.long_update
    # Chapters and sub chapters are both part of the index, with sub chapters between the chapter name and the next chapter name

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

            # Get sub chapter release date
            sub_chapter_release_date = sub_chapter.find('dt', class_='long_update').text

            # Append sub chapter
            sub_chapters.append(SubChapter(
                novel_code,
                chapter_number,
                sub_chapter_number,
                sub_chapter_link,
                sub_chapter_name,
                sub_chapter_release_date
            ))

            # Increment sub chapter number
            sub_chapter_number += 1

        # Append chapter
        chapters.append(Chapter(
            novel_code,
            chapter_number,
            chapter_name_str,
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

def _get_sub_chapter_contents(soup: BeautifulSoup) -> str:
    """Get the contents of the sub chapter.

    Parameters
    ----------
    soup : BeautifulSoup
        The soup of the sub chapter.

    Returns
    -------
    str
        The contents of the sub chapter.
    """

    # Find element that contains the sub chapter contents
    # It's found at div#novel_contents > div#novel_color > div#novel_honbun > p
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

def process_targets(novel: Novel, targets: dict[str, list[str]], verbose: bool=False) -> None:
    # Initialize
    base_url = 'https://ncode.syosetu.com'

    # Get url
    url = base_url + '/' + novel.novel_code + '/'

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
                    print("Scraping " + base_url + sub_chapter.link + "... ", end="") if verbose else None
                    sys.stdout.flush()
                    
                    # Get soup
                    soup = _get_soup(base_url + sub_chapter.link)

                    # Get sub chapter contents
                    sub_chapter_contents = _get_sub_chapter_contents(soup)

                    # Set sub chapter contents
                    sub_chapter.contents = sub_chapter_contents

                    print("Done") if verbose else None
                except Exception as e:
                    print("Failed") if verbose else None
                    raise Exception("Failed to scrape " + base_url + sub_chapter.link + ": " + str(e))



#def process_novel(novel_code: str, targets: dict[str, list[str]], verbose: bool=False) -> Novel:
def process_novel(novel_code: str, verbose: bool=False) -> Novel:
    """Process a novel.

    Parameters
    ----------
    novel_code : str
        The code of the novel.
    # targets : dict[str, list[str]]
    #     The targets to process.
    verbose : bool, optional
        Whether to print verbose output, by default False

    Returns
    -------
    Novel
        The processed novel.
    """

    # Validate parameters
    if not isinstance(novel_code, str):
        raise TypeError("novel_code must be a str")
    # if not isinstance(targets, dict):
    #     raise TypeError("targets must be a dict")
    # for key, value in targets.items():
    #     if not isinstance(key, str):
    #         raise TypeError("targets keys must be str")
    #     if not isinstance(value, list):
    #         raise TypeError("targets values must be list")
    #     if not all(isinstance(element, str) for element in value):
    #         raise TypeError("targets values must be list of str")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a bool")

    # Initialize
    base_url = 'https://ncode.syosetu.com'

    # Get url
    url = base_url + '/' + novel_code + '/'

    try:
        print("Scraping " + url + "... ", end="") if verbose else None
        sys.stdout.flush()
        
        # Get soup
        soup = _get_soup(url)

        # Get title
        title = _get_title(soup)

        # Get author
        author, link = _get_author(soup)

        # Get description
        description = _get_description(soup)

        # Get index
        index = _get_index(soup)

        # Process index
        chapters = _process_index(index, novel_code)

        print("Done") if verbose else None
    except Exception as e:
        print("Failed") if verbose else None
        raise Exception("Failed to scrape " + url + ": " + str(e))
    
    chapters.sort()
    # for chapter in chapters:
    #     chapter.sub_chapters.sort()

    #     if targets is not None:
    #         if str(chapter.chapter_index) not in targets:
    #             continue

    #         sub_chapter_targets = targets[str(chapter.chapter_index)]
    #         for sub_chapter in chapter.sub_chapters:
    #             if len(sub_chapter_targets) > 0 and str(sub_chapter.sub_chapter_index) not in sub_chapter_targets:
    #                 continue

    #             try:
    #                 print("Scraping " + base_url + sub_chapter.link + "... ", end="") if verbose else None
    #                 sys.stdout.flush()
                    
    #                 # Get soup
    #                 soup = _get_soup(base_url + sub_chapter.link)

    #                 # Get sub chapter contents
    #                 sub_chapter_contents = _get_sub_chapter_contents(soup)

    #                 # Set sub chapter contents
    #                 sub_chapter.contents = sub_chapter_contents

    #                 print("Done") if verbose else None
    #             except Exception as e:
    #                 print("Failed") if verbose else None
    #                 raise Exception("Failed to scrape " + base_url + sub_chapter.link + ": " + str(e))
                
    return Novel(
        novel_code,
        title,
        author,
        description,
        "ja",
        author_link=link,
        chapters=chapters)
