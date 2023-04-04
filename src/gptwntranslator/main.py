import curses

def main(stdscr):
    # Clear screen
    stdscr.clear()

    # Title of the program
    title = "gptwntranslator"

    # Version of the program
    version = "v2.0.0"

    # Title string
    title_string = f"{title} {version}"

    # Title container
    container = [
        "┌─" + "─" * (len(title_string) + 2) + "─┐",
        "│  " + title_string + "  │",
        "└─" + "─" * (len(title_string) + 2) + "─┘",
    ]



    # Set up the menu items
    menu_items = ["Option 1", "Option 2", "Option 3", "Exit"]

    # Initialize the cursor position
    current_row = 0

    # Function to display the menu
    def display_menu():
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Print the title container at the top of the screen
        for idx, line in enumerate(container):
            x = 2
            y = 2 + idx
            stdscr.addstr(y, x, line)



        for idx, item in enumerate(menu_items):
            x = w // 2 - len(item) // 2
            y = h // 2 - len(menu_items) // 2 + idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

    # Initialize color pair
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Display the menu initially
    display_menu()

    while True:
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == ord('\n'):
            if current_row == len(menu_items) - 1:
                break
            else:
                stdscr.clear()
                stdscr.addstr(0, 0, f"You selected '{menu_items[current_row]}'")
                stdscr.refresh()
                stdscr.getch()

        # Redraw the menu
        display_menu()

if __name__ == "__main__":
    curses.wrapper(main)