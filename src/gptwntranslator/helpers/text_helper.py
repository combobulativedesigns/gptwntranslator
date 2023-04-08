"""Contains helper functions for text processing."""

import os
import sys
import re
from gptwntranslator.helpers.config_helper import Config
from gptwntranslator.helpers.data_helper import get_targeted_sub_chapters

from gptwntranslator.models.novel import Novel


def parse_chapters(input_string: str) -> dict[str, list[str]]:
    """Parse a string of chapter numbers and ranges into a dictionary.

    Parameters
    ----------
    input_string : str
        The string to parse.

    Returns
    -------
    dict[str, list[str]]
        A dictionary of chapter numbers and subchapter numbers.
    """

    # Validate parameters
    if not isinstance(input_string, str):
        raise TypeError("Input string must be a string")

    # Check if the input string is empty
    if input_string == "":
        return {}

    # Matches a single sub chapter number
    pattern_core = "(\\d+)"
    # Matches a sub chapter range
    pattern_range = "(\\d+-\\d+)" 
    # Matches a single sub chapter number or range
    pattern_sub_chapter = f"({pattern_core}|{pattern_range})" 
    # Matches a list of sub chapter numbers or ranges
    pattern_sub_chapters = f"({pattern_sub_chapter}(,{pattern_sub_chapter})*)" 
    # Matches a single chapter number with optional sub chapters
    pattern_chapter_with_sub = f"(\\d+(:{pattern_sub_chapters})?)" 
    # Matches a single chapter number with optional sub chapters or a chapter range
    pattern_chapter = f"({pattern_chapter_with_sub}|{pattern_range})" 
    # Matches a list of chapter numbers with optional sub chapters or ranges
    pattern_chapters = f"({pattern_chapter}(;{pattern_chapter})*)" 

    # Compile the pattern
    pattern = re.compile(rf"^{pattern_chapters}$")

    # Check if the input string matches the pattern
    if not pattern.match(input_string):
        raise ValueError(f"Invalid chapter string: {input_string}")

    # Initialize the result dictionary
    result = {}

    # Split the input string into chapters
    chapters = input_string.split(';')
    
    # Parse each chapter
    for chapter in chapters:
        # Split the chapter into chapter number and sub chapters
        chapter_parts = chapter.split(':')

        # Parse the chapter number and sub chapters
        if len(chapter_parts) == 1:
            # Check if the chapter is a range
            if '-' in chapter_parts[0]:
                # Add each chapter in the range to the result
                for i in range(int(chapter_parts[0].split('-')[0]), int(chapter_parts[0].split('-')[1]) + 1):
                    result[str(i)] = []
            else:
                # Add the chapter to the result
                result[chapter_parts[0]] = []
        elif len(chapter_parts) == 2:
            # Initialize the sub chapters list
            result[chapter_parts[0]] = []

            splits = []
            
            # Check if there are multiple sub chapters
            if ',' in chapter_parts[1]:
                # Split the sub chapters
                splits = chapter_parts[1].split(',')
            else:
                # Add the sub chapter to the list
                splits.append(chapter_parts[1])

            # Parse each sub chapter
            for each in splits:
                # Check if the sub chapter is a range
                if '-' in each:
                    # Add each sub chapter in the range to the result
                    result[chapter_parts[0]].extend([str(i) for i in range(int(each.split('-')[0]), int(each.split('-')[1]) + 1)])
                else:
                    # Add the sub chapter to the result
                    result[chapter_parts[0]].append(each)
        elif len(chapter_parts) > 2:
            # Raise an error if the chapter string is invalid
            raise ValueError(f"Invalid chapter string: {chapter}")
    
    return result

def make_printable(s: str) -> str:
    """Return a string with all non-printable characters removed.

    Parameters
    ----------
    s : str
        The string to process.
    verbose : bool, optional
        If True, print the number of non-printable characters removed, by default False

    Returns
    -------
    str
        The string with all non-printable characters removed.
    """

    # Validate the parameter
    if not isinstance(s, str):
        raise TypeError("The string must be a string")

    LINE_BREAK_CHARACTERS = set(["\n", "\r"])
    NOPRINT_TRANS_TABLE = {
        i: None for i in range(0, sys.maxunicode + 1) if not chr(i).isprintable() and not chr(i) in LINE_BREAK_CHARACTERS
    }

    try:
        new_str = s.translate(NOPRINT_TRANS_TABLE)
        return new_str
    except Exception as e:
        raise Exception(f"Error: {e}")
    
def txt_to_md(input_txt: str) -> str:
    """Convert a text file to a markdown file.

    Parameters
    ----------
    input_txt : str
        The text file to convert.
    
    Returns
    -------
    str
        The markdown contents.
    """

    # Validate the parameter
    if not isinstance(input_txt, str):
        raise TypeError("The input text must be a string")
    
    lines = input_txt.splitlines()

    chapter_title = lines[0].strip('\n\t ')
    output_txt = f"## **{chapter_title}**\n\n"

    for line in lines[1:]:
        line = line.strip('\n\t ')
        if line:
            output_txt += f"{line}\n\n"

    return output_txt

def write_novel_md(novel: Novel, targets: dict[str, list[str]]) -> None:
    # Validate parameters
    if not isinstance(novel, Novel):
        raise TypeError("Novel must be a Novel object")
    if not isinstance(targets, dict):
        raise TypeError("Targets must be a dictionary")
    if not all(isinstance(key, str) for key in targets.keys()):
        raise TypeError("Chapter numbers must be strings")
    if not all(key.isdigit() for key in targets.keys()):
        raise TypeError("Chapter numbers must be digits as strings")
    if not all(isinstance(value, list) for value in targets.values()):
        raise TypeError("Sub chapter numbers must be lists")
    if not all(isinstance(item, str) for value in targets.values() for item in value):
        raise TypeError("Sub chapter numbers must be strings")
    if not all(item.isdigit() for value in targets.values() for item in value):
        raise TypeError("Sub chapter numbers must be digits as strings")
    
    config = Config()
    sub_chapters = get_targeted_sub_chapters(novel, targets)
    target_language = config.data.config.translator.target_language

    metadata = f"---\ntitle: \"{novel.title_translation[target_language]}\"\nauthor: \"{novel.author_translation[target_language]}\"\nlanguage: {target_language}\n---\n\n"

    md_text = metadata
    md_text += "# **Contents**\n\n"
    md_text += "\n".join([f"- [{sub_chapter.translated_name[target_language] if target_language in sub_chapter.translated_name is not None else sub_chapter.name}](#chapter-{sub_chapter.chapter_index}-{sub_chapter.sub_chapter_index})" for sub_chapter in sub_chapters])
    md_text += "\n\n"
    
    for sub_chapter in sub_chapters:
        name = sub_chapter.translated_name[target_language] if target_language in sub_chapter.translated_name is not None else sub_chapter.name
        md_text += f"# <strong id=\"chapter-{sub_chapter.chapter_index}-{sub_chapter.sub_chapter_index}\">{name}</strong>\n\n"
        lines = sub_chapter.translation[target_language].splitlines()
        for line in lines:
            md_text += "{}\n\n".format(line.strip('\n\t '))

    return md_text