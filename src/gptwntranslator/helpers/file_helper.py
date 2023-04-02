"""This module contains helper functions for file operations"""

import os
import sys
import pypandoc


def write_file(file_path: str, contents: str, verbose: bool=False) -> None:
    """Write contents to file_path
    
    Parameters
    ----------
    file_path : str
        The path to the file to write to.
    contents : str
        The contents to write to the file.
    verbose : bool, optional
        Whether to print verbose messages, by default False
    
    Raises
    ------
    Exception
        If an error occurs while writing to the file.
    """	

    # Validate the parameters
    if not isinstance(file_path, str):
        raise TypeError("The file path must be a string")
    if not isinstance(contents, str):
        raise TypeError("The contents must be a string")
    if not isinstance(verbose, bool):
        raise TypeError("The verbose flag must be a boolean")

    try:
        print(f"Writing file {file_path}... ", end="") if verbose else None
        sys.stdout.flush()

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(contents)

        print("Done") if verbose else None
    except Exception as e:
        print("Failed") if verbose else None
        raise Exception(f"Error: {e}")

def read_file(file_path: str, verbose: bool=False) -> str:
    """Read contents from file_path	

    Parameters
    ----------
    file_path : str
        The path to the file to read from.
    verbose : bool, optional
        Whether to print verbose messages, by default False

    Raises
    ------
    Exception
        If an error occurs while reading from the file.

    Returns
    -------
    str
        The contents of the file.
    """

    # Validate the parameters
    if not isinstance(file_path, str):
        raise TypeError("The file path must be a string")
    if not isinstance(verbose, bool):
        raise TypeError("The verbose flag must be a boolean")

    try:
        print(f"Reading file {file_path}... ", end="") if verbose else None

        with open(file_path, 'r', encoding='utf-8') as f:
            contents = f.read()

        print("Done") if verbose else None
    except Exception as e:
        print("Failed") if verbose else None
        raise Exception(f"Error: {e}")

    return contents


def write_md_as_epub(input_md: str, output_path: str, verbose: bool=False) -> None:
    """Write the input markdown as an epub file.

    Parameters
    ----------
    input_md : str
        The markdown to write as an epub.
    output_path : str
        The path to the epub file to write to.
    verbose : bool, optional
        Whether to print verbose messages, by default False
    """
    
    # Validate the parameters
    if not isinstance(input_md, str):
        raise TypeError("The input markdown must be a string")
    if not isinstance(output_path, str):
        raise TypeError("The output path must be a string")
    if not isinstance(verbose, bool):
        raise TypeError("The verbose flag must be a boolean")

    pypandoc.convert_text('\n\n'.join(input_md), "epub3", format="md", outputfile=output_path)