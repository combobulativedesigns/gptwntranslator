"""Contains helper functions for text processing."""

import sys
import re


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

    chapter_title = lines[0].strip()
    output_txt = f"## **{chapter_title}**\n\n"

    for line in lines[1:]:
        line = line.strip()
        if line:
            output_txt += f"{line}\n\n"

    return output_txt