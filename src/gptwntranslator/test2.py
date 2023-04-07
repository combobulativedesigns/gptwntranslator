import argparse
import sys

def show_in_depth_help():
    message = '''
gptwntranslator - A web novel translator powered by OpenAI's GPT models
-----------------------------------------------------------------------

This tool supports two main modes: interactive and command. You can also access this in-depth help by using the 'help' command.

1. Interactive Mode:

    Run the tool in interactive mode by using the 'interactive' or 'i' command:

        python -m gptwntranslator i
            or
        python src/gptwntranslator/__main__.py i
            or
        gptwntranslator i

2. Command Mode:

    Run the tool in command mode by using the 'command' or 'c' command:

        python -m gptwntranslator c ACTION NOVEL_IDENTIFIER [CHAPTERS]
            or
        python src/gptwntranslator/__main__.py c ACTION NOVEL_IDENTIFIER [CHAPTERS]
            or
        gptwntranslator c ACTION NOVEL_IDENTIFIER [CHAPTERS]


    Command mode requires an action, a novel identifier, and optionally chapters depending on the action. Available actions:

        - scrape-metadata (sm): Scrape novel metadata
        - scrape-chapters (sc): Scrape novel chapters
        - translate-metadata (tm): Translate novel metadata
        - translate-chapters (tc): Translate novel chapters
        - export-chapters (ec): Export novel chapters

    Provide the novel identifier (e.g., URL code). If the action is 'sc', 'tc', or 'ec', specify the chapters to process (e.g., 1:1, 1-2, 10:2-5;11).
    All actions but 'sm' require previously scraped metadata. If the metadata is not found, the tool will terminate.
    Translate actions require a previous scrape action. If the chapters are not found, the tool will terminate.
    Export actions require a previous translate action. If the chapters are not found, the tool will terminate. 

    Example:

        Novel URL: https://ncode.syosetu.com/n5177as/ >>> Novel code: n5177as

    Scrape novel metadata:

        gptwntranslator c sm n5177as

    Enable verbose output using the -v or --verbose flag:

        gptwntranslator c -v sm n5177as

Both modes support the following optional arguments:

    -cf, --config-file PATH     Specify the path to a custom configuration file
    -pf, --persistent-file PATH     Specify the path to a custom persistent file for tracking progress
    -od, --output-directory PATH    Specify the output directory for generated files

Chapters can be specified in the following formats:

    - Chapter numbers are represented by one or more digits (e.g., \"3\" or \"12\").
    - Sub-chapter numbers are also represented by one or more digits (e.g., \"4\" or \"23\").
    - Chapter ranges are represented by two chapter numbers separated by a hyphen (e.g., \"2-5\").
    - Sub-chapter ranges are represented by two sub-chapter numbers separated by a hyphen (e.g., \"6-9\").
    - A chapter can be followed by a colon and a list of sub-chapters or sub-chapter ranges (e.g., \"3:2,5,7-9\").
    - Individual chapters or chapter ranges can be separated by semicolons (e.g., \"3:2,5;5-7;8:1-3,5\").

    Here's an example input that would match this pattern: \"1:1,3,5-7;2-4;5:1-3,6;6-8\".

    '''

    print(message)

def main():
    # Check if no arguments are provided, and display the in-depth help if necessary.
    if len(sys.argv) == 1:
        show_in_depth_help()
        sys.exit()

    parser = argparse.ArgumentParser(description="A web novel translator powered by OpenAI's GPT models.", add_help=False)

    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Help mode
    help_parser = subparsers.add_parser("help", help="Show in-depth help section", aliases=["h"])

    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Run the tool in interactive mode, prompting for actions and options", aliases=["i"])
    interactive_parser.add_argument("-cf", "--config-file", type=str, help="Specify the path to a custom configuration file")
    interactive_parser.add_argument("-pf", "--persistent-file", type=str, help="Specify the path to a custom persistent file for tracking progress")
    interactive_parser.add_argument("-od", "--output-directory", type=str, help="Specify the output directory for generated files")

    # Command mode
    command_parser = subparsers.add_parser("command", help="Run the tool in command mode, providing actions and options as arguments", aliases=["c"])
    actions_parser = command_parser.add_subparsers(dest="action", required=True)

    # Define subparsers for each action
    sm_parser = actions_parser.add_parser("sm", help="Scrape metadata", aliases=["scrape-metadata"])
    sm_parser.add_argument("novel", type=str, help="Provide the novel identifier (e.g.,n5177as)")

    sc_parser = actions_parser.add_parser("sc", help="Scrape chapters", aliases=["scrape-chapters"])
    sc_parser.add_argument("novel", type=str, help="Provide the novel identifier (e.g., n5177as)")
    sc_parser.add_argument("chapters", type=str, help="Specify chapters to process (e.g., '1:1,3,5-7;2-4;5:1-3,6;6-8')")

    tm_parser = actions_parser.add_parser("tm", help="Translate metadata", aliases=["translate-metadata"])
    tm_parser.add_argument("novel", type=str, help="Provide the novel identifier (e.g., n5177as)")

    tc_parser = actions_parser.add_parser("tc", help="Translate chapters", aliases=["translate-chapters"])
    tc_parser.add_argument("novel", type=str, help="Provide the novel identifier (e.g., n5177as)")
    tc_parser.add_argument("chapters", type=str, help="Specify chapters to process (e.g., '1:1,3,5-7;2-4;5:1-3,6;6-8')")

    ec_parser = actions_parser.add_parser("ec", help="Export chapters", aliases=["export-chapters"])
    ec_parser.add_argument("novel", type=str, help="Provide the novel identifier (e.g., n5177as)")
    ec_parser.add_argument("chapters", type=str, help="Specify chapters to process (e.g., '1:1,3,5-7;2-4;5:1-3,6;6-8')")

    # Add common arguments for all actions
    for subparser in [sm_parser, sc_parser, tm_parser, tc_parser, ec_parser]:
        subparser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for detailed information during execution")
        subparser.add_argument("-cf", "--config-file", type=str, help="Specify the path to a custom configuration file")
        subparser.add_argument("-pf", "--persistent-file", type=str, help="Specify the path to a custom persistent file for tracking progress")
        subparser.add_argument("-od", "--output-directory", type=str, help="Specify the output directory for generated files")

    args = parser.parse_args()

    if args.mode in ["help", "h"]:
        show_in_depth_help()
        sys.exit()

    if args.mode == "command" and (args.action in ["sm", "tm"] and args.chapters is not None):
        parser.error("Chapters argument is not allowed for the selected action")

    if args.mode == "command" and (args.action in ["sc", "tc", "ec"] and args.chapters is None):
        parser.error("Chapters argument is required for the selected action")

    print(args)

if __name__ == "__main__":
    main()