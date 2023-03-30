import sys

def make_printable(s, verbose=False):
    LINE_BREAK_CHARACTERS = set(["\n", "\r"])
    NOPRINT_TRANS_TABLE = {
        i: None for i in range(0, sys.maxunicode + 1) if not chr(i).isprintable() and not chr(i) in LINE_BREAK_CHARACTERS
    }

    try:
        print(f"Removing non-printable characters... ", end="") if verbose else None
        new_str = s.translate(NOPRINT_TRANS_TABLE)
        print("Done") if verbose else None
        return new_str
    except Exception as e:
        print("Failed") if verbose else None
        raise Exception(f"Error: {e}")
    
def txt_to_md(input_txt):
    lines = input_txt.splitlines()

    chapter_title = lines[0].strip()
    output_txt = f"## **{chapter_title}**\n\n"

    for line in lines[1:]:
        line = line.strip()
        if line:
            output_txt += f"{line}\n\n"

    return output_txt