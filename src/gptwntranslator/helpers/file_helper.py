import os

import pypandoc


def write_file(file_path, contents, verbose=False):
    '''Write contents to file_path'''

    try:
        print(f"Writing file {file_path}... ", end="") if verbose else None

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(contents)

        print("Done") if verbose else None
    except Exception as e:
        print("Failed") if verbose else None
        raise Exception(f"Error: {e}")

def read_file(file_path, verbose=False):
    '''Read contents from file_path'''

    try:
        print(f"Reading file {file_path}... ", end="") if verbose else None

        with open(file_path, 'r', encoding='utf-8') as f:
            contents = f.read()

        print("Done") if verbose else None
    except Exception as e:
        print("Failed") if verbose else None
        raise Exception(f"Error: {e}")

    return contents


def write_md_as_epub(input_md, output_path, verbose=False):
    pypandoc.convert_text('\n\n'.join(input_md), "epub3", format="md", outputfile=output_path)