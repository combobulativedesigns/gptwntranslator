from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gptwntranslator.helpers.logger_helper import CustomLogger


logger = CustomLogger(__name__)

def print_title(screen, title, y):
    for line in title:
        y += 1
        x = 2
        screen.print_at(line, x, y)

    return y

def read_user_input(screen, old_input, x, y):
    # screen.show_cursor(True)
    input_str = ""
    if old_input is not None:
        screen.print_at(" " * len(old_input), x, y)
    while True:
        screen.print_at(input_str, x, y)
        screen.move(x + len(input_str), y)
        screen.print_at(" ", x + len(input_str), y, attr=Screen.A_REVERSE)
        screen.refresh()
        event = screen.get_event()
        if isinstance(event, KeyboardEvent):
            key = event.key_code
            if key == 10 or key == 13:
                screen.print_at(" ", x + len(input_str), y)
                break
            elif key == screen.KEY_BACK:
                if len(input_str) > 0:
                    screen.print_at(" ", x + len(input_str), y) # erase the deleted char from the screen
                    input_str = input_str[:-1]
                    screen.print_at(" ", x + len(input_str), y, attr=Screen.A_REVERSE)
            elif key < 256:
                try:
                    input_str += chr(key)
                except ValueError:
                    pass

    # screen.show_cursor(False)
    return input_str

def wait_for_user_input(screen, x, y):
    screen.print_at("Press enter to continue...", x, y)
    screen.refresh()

    while True:
        event = screen.get_event()
        if isinstance(event, KeyboardEvent):
            key = event.key_code
            if key == 10 or key == 13:
                break

def navigate_items(screen, pre_y, pre_x, items, active_index=0):
    while True:
        for index, item in enumerate(items):
            y, x, trigger, label, _, content, is_text_box = item
            screen.print_at(label, x + pre_x, y + pre_y)

            if index == active_index:
                if is_text_box:
                    screen.print_at(label, x + pre_x, y + pre_y, attr=Screen.A_REVERSE)
                    screen.print_at(content, x + pre_x + len(label) + 1, y + pre_y)
                else:
                    screen.print_at(label, x + pre_x, y + pre_y, attr=Screen.A_REVERSE)
            else:
                if is_text_box:
                    screen.print_at(label, x + pre_x, y + pre_y)
                    screen.print_at(content, x + pre_x + len(label) + 1, y + pre_y)
                else:
                    screen.print_at(label, x + pre_x, y + pre_y)

        screen.refresh()

        event = screen.get_event()
        if isinstance(event, KeyboardEvent):
            key = event.key_code
            if key == screen.KEY_UP:
                active_index = (active_index - 1) % len(items)
            elif key == screen.KEY_DOWN:
                active_index = (active_index + 1) % len(items)
            elif 48 <= key <= 57:
                number = key - 48
                for index, item in enumerate(items):
                    y, x, trigger, label, _, content, is_text_box = item
                    if trigger == number:
                        active_index = index
                        logger.debug(f"Triggered item: {index}")
                        break
                else:
                    continue
                break
            elif key == 10 or key == 13:
                y, x, trigger, label, target_index, _, is_text_box = items[active_index]
                logger.debug(f"Target index: {target_index}, type: {type(target_index)}")
                if is_text_box:
                    trg_y, trg_x, trg_trigger, trg_label, trg_target, old_input, trg_is_text_box = items[target_index]
                    screen.print_at(label + " ", x + pre_x, y + pre_y)
                    screen.refresh()
                    user_input = read_user_input(screen, old_input, x + pre_x + len(label) + 1, y + pre_y)
                    logger.debug(f"User input: {user_input}")
                    items[target_index] = (trg_y, trg_x, trg_trigger, trg_label, trg_target, user_input, trg_is_text_box)
                else:
                    break

    logger.debug(f"Active index: {active_index}")
    return active_index