"""Contains helper functions for text processing."""

import sys


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