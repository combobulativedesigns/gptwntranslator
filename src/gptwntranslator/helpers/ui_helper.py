import enum
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen

from gptwntranslator.helpers.logger_helper import CustomLogger
from gptwntranslator.origins.origin_factory import OriginFactory
from gptwntranslator.ui.page_base import PageBase


logger = CustomLogger(__name__)

class UIMenuItemType(enum.Enum):
    PAGE_NAVIGATION = "page_navigation"
    TEXT_INPUT = "text_input"
    COMBO_BOX = "combo_box"

class UIMenuItem:
    def __init__(self, item_type: UIMenuItemType, y_offset: int, x_offset: int, key_shortcut: int, text: str, data_target: 'UIMenuItem'=None, data_target_item: str=None, page_target: PageBase=None, page_data: dict=None, combo_items: dict=None):
        if item_type == UIMenuItemType.PAGE_NAVIGATION and page_target is None:
            raise ValueError("Page navigation menu items must have a page target")
        if item_type == UIMenuItemType.TEXT_INPUT and data_target is None:
            raise ValueError("Text input menu items must have a data target")
        if item_type == UIMenuItemType.COMBO_BOX and data_target is None:
            raise ValueError("Combo box menu items must have a data target")
        if item_type == UIMenuItemType.COMBO_BOX and page_target is not None:
            raise ValueError("Combo box menu items cannot have a page target")
        if item_type == UIMenuItemType.TEXT_INPUT and page_target is not None:
            raise ValueError("Text input menu items cannot have a page target")
        if item_type == UIMenuItemType.PAGE_NAVIGATION and page_data is None:
            raise ValueError("Page navigation menu items must have page kwargs")
        if item_type == UIMenuItemType.TEXT_INPUT and page_data is not None:
            raise ValueError("Text input menu items cannot have page kwargs")
        if item_type == UIMenuItemType.COMBO_BOX and page_data is not None:
            raise ValueError("Combo box menu items cannot have page kwargs")
        if item_type == UIMenuItemType.PAGE_NAVIGATION and data_target is not None:
            raise ValueError("Page navigation menu items cannot have a data target")
        if item_type == UIMenuItemType.TEXT_INPUT and combo_items is not None:
            raise ValueError("Text input menu items cannot have combo items")
        if item_type == UIMenuItemType.COMBO_BOX and combo_items is None:
            raise ValueError("Combo box menu items must have combo items")
        if item_type == UIMenuItemType.PAGE_NAVIGATION and combo_items is not None:
            raise ValueError("Page navigation menu items cannot have combo items")
        if data_target is not None and data_target_item is None:
            raise ValueError("Data target menu items must have a data target item")
        if data_target is None and data_target_item is not None:
            raise ValueError("Data target menu items cannot have a data target item")


        self.item_type = item_type
        self.y_offset = y_offset
        self.x_offset = x_offset
        self.key_shortcut = key_shortcut
        self.text = text
        self.data_target = data_target
        self.data_target_item = data_target_item
        self.page_target = page_target
        self.page_data = page_data
        self.combo_items = combo_items

    @property
    def label(self):
        return f"{self.key_shortcut}) {self.text}" if self.key_shortcut is not None else self.text

def print_title(screen, title, y):
    for line in title:
        y += 1
        x = 2
        screen.print_at(line, x, y)

    return y

def print_messages(screen, messages: list[str], x: int, y: int, character_limit: int=60):
    last_y = y

    for message in messages:
        if len(message) > character_limit:
            sub_messages = message.split(" ")
            while len(sub_messages) > 0:
                sub_message = ""
                if len(sub_messages[0]) > character_limit:
                    sub_message += sub_messages[0][:int(character_limit-1)] + "-"
                    sub_messages[0] = sub_messages[0][int(character_limit-1):]
                else:
                    while len(sub_message) + len(sub_messages[0]) < character_limit:
                        sub_message += sub_messages[0] + " "
                        sub_messages.pop(0)
                        if len(sub_messages) == 0:
                            break
                screen.print_at(sub_message, x, last_y)
                last_y += 1
        else:
            screen.print_at(message, x, last_y)
            last_y += 1

    return last_y

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

def navigate_items(screen, pre_y: int, pre_x: int, items: list[UIMenuItem], active_index: int=0) -> int:
    logger.debug(f"{type(screen)}")
    while True:
        for index, item in enumerate(items):
            screen.print_at(item.label, item.x_offset + pre_x, item.y_offset + pre_y)

            if index == active_index:
                if item.item_type == UIMenuItemType.TEXT_INPUT:
                    screen.print_at(item.label, item.x_offset + pre_x, item.y_offset + pre_y, attr=Screen.A_REVERSE)
                    screen.print_at("", item.x_offset + pre_x + len(item.label) + 1, item.y_offset + pre_y)
                elif item.item_type == UIMenuItemType.COMBO_BOX:
                    screen.print_at(item.label, item.x_offset + pre_x, item.y_offset + pre_y, attr=Screen.A_REVERSE)
                    target_item = item.data_target
                    target_item_data = target_item.page_data[item.data_target_item]
                    if not target_item_data:
                        target_item_data = list(item.combo_items.keys())[0]
                    max_label = max([len(x) for x in item.combo_items.values()])
                    target_item.page_data[item.data_target_item] = target_item_data
                    combo_box_text = item.combo_items[target_item_data]
                    screen.print_at(combo_box_text, item.x_offset + pre_x + len(item.label) + 1, item.y_offset + pre_y)
                    screen.print_at(" " * (max_label - len(combo_box_text)), item.x_offset + pre_x + len(item.label) + 1 + len(combo_box_text), item.y_offset + pre_y)
                else:
                    screen.print_at(item.label, item.x_offset + pre_x, item.y_offset + pre_y, attr=Screen.A_REVERSE)
            else:
                if item.item_type == UIMenuItemType.TEXT_INPUT:
                    screen.print_at(item.label, item.x_offset + pre_x, item.y_offset + pre_y)
                    screen.print_at("", item.x_offset + pre_x + len(item.label) + 1, item.y_offset + pre_y)
                elif item.item_type == UIMenuItemType.COMBO_BOX:
                    screen.print_at(item.label, item.x_offset + pre_x, item.y_offset + pre_y)
                    target_item = item.data_target
                    target_item_data = target_item.page_data[item.data_target_item]
                    if not target_item_data:
                        target_item_data = list(item.combo_items.keys())[0]
                    max_label = max([len(x) for x in item.combo_items.values()])
                    target_item.page_data[item.data_target_item] = target_item_data
                    combo_box_text = item.combo_items[target_item_data]
                    screen.print_at(combo_box_text, item.x_offset + pre_x + len(item.label) + 1, item.y_offset + pre_y)
                    screen.print_at(" " * (max_label - len(combo_box_text)), item.x_offset + pre_x + len(item.label) + 1 + len(combo_box_text), item.y_offset + pre_y)
                else:
                    screen.print_at(item.label, item.x_offset + pre_x, item.y_offset + pre_y)

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
                for idx, item in enumerate(items):
                    if item.key_shortcut == number:
                        active_index = idx
                        logger.debug(f"Triggered item: {idx}")
                        break
                else:
                    continue
                break
            elif key == 10 or key == 13:
                item = items[active_index]
                if item.item_type == UIMenuItemType.TEXT_INPUT:
                    target_item = item.data_target
                    screen.print_at(item.label + " ", item.x_offset + pre_x, item.y_offset + pre_y)
                    screen.refresh()
                    user_input = read_user_input(screen, target_item.page_data[item.data_target_item], item.x_offset + pre_x + len(item.label) + 1, item.y_offset + pre_y)
                    target_item.page_data[item.data_target_item] = user_input
                elif item.item_type == UIMenuItemType.COMBO_BOX:
                    target_item = items[active_index].data_target
                    target_item_data = target_item.page_data[items[active_index].data_target_item]
                    values = list(items[active_index].combo_items.keys())
                    idx = values.index(target_item_data)
                    idx = (idx - 1) % len(values)
                    target_item_data = values[idx]
                    target_item.page_data[items[active_index].data_target_item] = target_item_data
                else:
                    break

    logger.debug("Selected item: %s", items[active_index].label)
    return active_index

def navigate_items_old(screen, pre_y, pre_x, items, active_index=0):
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