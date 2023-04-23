def get_resources():
    # Initialize resource dictionary
    resources = {}

    # Title of the program
    title = "gptwntranslator"

    # Version of the program
    version = "v2.1.4"

    # Title string
    title_string = f"{title} {version}"

    # Title container
    title_container = [
        "┌─" + "─" * (len(title_string) + 2) + "─┐",
        "│  " + title_string + "  │",
        "└─" + "─" * (len(title_string) + 2) + "─┘",
    ]

    resources["title"] = title_container

    resources["chapter_regex_explanation"] = [
        "Chapter numbers are represented by one or more digits (e.g., \"3\" or \"12\").",
        "Sub-chapter numbers are also represented by one or more digits (e.g., \"4\" or \"23\").",
        "Chapter ranges are represented by two chapter numbers separated by a hyphen (e.g., \"2-5\").",
        "Sub-chapter ranges are represented by two sub-chapter numbers separated by a hyphen (e.g., \"6-9\").",
        "A chapter can be followed by a colon and a list of sub-chapters or sub-chapter ranges (e.g., \"3:2,5,7-9\").",
        "Individual chapters or chapter ranges can be separated by semicolons (e.g., \"3:2,5;5-7;8:1-3,5\").",
        "Here's an example input that would match this pattern: \"1:1,3,5-7;2-4;5:1-3,6;6-8\"."]
    
    return resources.copy()