from chunk import Chunk
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

import gptwntranslator.api.openai_api as openai_api
from gptwntranslator.models.chapter import Chapter
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.sub_chapter import SubChapter

def _get_soup(url):
    html = urlopen(url)
    soup = bs(html, 'html.parser')
    return soup

def _get_title(soup):
    # Find element that contains the title
    # It's found at div#novel_contents > div#novel_color > p.novel_title
    title = soup.find('div', id='novel_contents').find('div', id='novel_color').find('p', class_='novel_title').text
    return title

def _get_author(soup):
    # Find element that contains the author
    # It's found at div#novel_contents > div#novel_color > div.novel_writername > a
    author = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', class_='novel_writername').find('a').text
    link = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', class_='novel_writername').find('a')['href']
    return author, link

def _get_description(soup):
    # Find element that contains the description
    # It's found at div#novel_contents > div#novel_color > div#novel_ex
    description = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', id='novel_ex').text
    return description

def _get_index(soup):
    # Find element that contains the chapters
    # It's found at div#novel_contents > div#novel_color > div#index_box
    index = soup.find('div', id='novel_contents').find('div', id='novel_color').find('div', class_='index_box')
    return index

def _process_index(index):
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
                sub_chapters.append(
                    SubChapter(
                    sub_chapter_number, 
                    chapter_number,
                    sub_chapter_name,
                    "",
                    sub_chapter_link,
                    sub_chapter_release_date,
                    "",
                    "",
                    ""))

                # Increment sub chapter number
                sub_chapter_number += 1
                
            # Set next element as current element
            chapter_name = next_element

        # Append chapter
        chapters.append(
            Chapter(
            chapter_number, 
            chapter_name_str, 
            "", 
            sub_chapters))

        # Increment chapter number
        chapter_number += 1
        
    return chapters

def _get_sub_chapter_contents(soup):
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
            sub_chapter_text_contents += sub_chapter_content.text.strip() + "\n\n"

    return sub_chapter_text_contents

def process_novel(novel_code, verbose=False):
    # Initialize
    base_url = 'https://ncode.syosetu.com'

    # Get url
    url = base_url + '/' + novel_code + '/'

    try:
        print("Scraping " + url + "... ", end="") if verbose else None
        
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
        chapters = _process_index(index)

        print("Done") if verbose else None
    except Exception as e:
        print("Failed") if verbose else None
        raise Exception("Failed to scrape " + url + ": " + str(e))
    
    chapters.sort()
    for chapter in chapters:
        chapter.sub_chapters.sort()
        for sub_chapter in chapter.sub_chapters:
            try:
                print("Scraping " + base_url + sub_chapter.link + "... ", end="") if verbose else None
                
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
            
    return Novel(
        novel_code,
        title,
        "",
        author,
        "",
        link,
        description,
        "",
        chapters)
















