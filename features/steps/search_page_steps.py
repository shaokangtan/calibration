from behave import step
from lib.vudu_image import ocr, get_default_match_parameter
from lib.helper import debug, get_frame_name, WORK_DIR, find_selection_text, find_keyboard_mapping, \
    move_to_char_pos_keyboard
from lib import keys
from features.steps.roku_steps import press
import time
import cv2
from lib.roku.regions import REGION_SEARCH_TITLE, REGION_SEARCH_SUGGESTIONS
from lib.roku_images import SEARCH_SUGGESTION_SEL_LEFT, SEARCH_SUGGESTION_SEL_RIGHT
# keyboard:
KBD_SPACE = "SPACE"
KBD_CLEAR = "CLEAR"


search_kb_layout = [
            ["ABC / 123", " ", " ", '@!=', " ", " "],
            ["A", "B", "C", "D", "E", "F"],
            ["G", "H", "I", "J", "K", "L"],
            ["M", "N", "O", "P", "Q", "R"],
            ["S", "T", "U", "V", "W", "X"],
            ["Y", "Z", "1", "2", "3", "4"],
            ["5", "6", "7", "8", "9", "0"],
            ["DEL", " ", "SPACE", " ", "CLEAR", ""]]

search_kb_row_total = len(search_kb_layout)

search_kb_col_total = len(search_kb_layout[0])

search_num_items = 10



def enter_string(context, title, move_to_search_result=True):
    """
    TODO: need to add code to handle special chars.
    Takes a string and uses soft keyboard to input the title
    After entering the string, move the highlight to bottom right corner of the keyboard.
    :param title: (str) content title
    :param move_to_search_result: (bool) if True, move to search result, otherwise move to suggestions
    :return: (int, int) coordinate of last character at input string
    """
    print("\n === Search title: [{}] ====\n\n".format(title))
    # Start from row 1 and col 0 to skip first row which only has two keys.
    # We can directly move to (0, 0) to locate "ABC / 123" key,
    # or directly move to (0, 0), then press KEY_RIGHT to locate "#!@" key
    current_coordinate = [1, 0]
    for c in title:
        if c == " ":
            c = KBD_SPACE
        print("========= Character ", c)
        next_coordinate = find_keyboard_mapping(search_kb_layout, c)
        move_to_char_pos_keyboard(context, current_coordinate[0], current_coordinate[1], next_coordinate[0],
                                  next_coordinate[1])
        current_coordinate = next_coordinate
        press(context, keys.KEY_SELECT, delay=1)
        print("=== OK pressed ===")

    print(f"current_coordinate is: {current_coordinate}")
    context.current_coordinate = current_coordinate


def move_to_search_result(context):
        """
        Navigate to the first poster in search result in right side.
        :param r_location: (int) current row position.
        """
        print("---- Navigate right to the first poster.")
        move_loop_count = search_kb_col_total - context.current_coordinate[1]
        print("move_loop_count: {}".format(move_loop_count))
        for no in range(move_loop_count):
            print("\n\n === Count to move right {}".format(no))
            press(context, keys.KEY_RIGHT, delay=1)


def move_to_search_suggestions(context):
        """
        Navigate down to the first search suggestions result
        :param col_location: (int) current col position.
        """
        print(f"current_coordinate is: {context.current_coordinate}")
        move_loop_count = search_kb_row_total - context.current_coordinate[0]
        print("move_loop_count: {}".format(move_loop_count))
        for no in range(move_loop_count):
            print(f"\n\n === Count to move right {no}")
            press(context, keys.KEY_DOWN, delay=1)


@step('I enter search "{search_string}" on the search page')
def step_impl(context, search_string):
    press(context, keys.KEY_DOWN)
    enter_string(context, search_string)


@step('I can verify search "{result}" on the search page')
def step_impl(context, result):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")

    move_to_search_result(context)
    for count in range(3):
        # search_region = regions.REGION_SIDE_PANEL_DICT[consts.SEARCH]
        assert 200 == cam.get_frame(context.frame)
        frame = cv2.imread(context.frame)
        read_title = ocr(region=REGION_SEARCH_TITLE, frame=frame).replace('\n', " ").upper()
        debug("=== Read out text: {}".format(read_title))
        if result in read_title:
            debug(f"Find result: {result}")
            return result
        else:
            debug(f"Didn't find the expected {result}. Move to next poster: ")
            press(context, keys.KEY_RIGHT, delay=2)
    assert False, f"Didn't find the expected {result}."

@step('I can verify suggestion "{result}" on the search page')
def step_impl(context, result):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")

    move_to_search_suggestions(context)
    debug("\n\n=== Read search suggestion.")
    mp = (3, 0.65, *get_default_match_parameter()[2::])  # use fixed method 3 and threshold =0.65

    for _ in range(3):
        assert 200 == cam.get_frame(context.frame)
        frame = cv2.imread(context.frame)
        text_read_out, region = find_selection_text(cv2.imread(context.frame), cv2.imread(SEARCH_SUGGESTION_SEL_LEFT), cv2.imread(SEARCH_SUGGESTION_SEL_RIGHT),
                                                    region=REGION_SEARCH_SUGGESTIONS, match_parameter=mp)
        format_read_out = text_read_out.upper()
        debug(f"The formatted read out: {format_read_out}")

        if result in format_read_out:
            debug("Find expected search string in search suggestion")
            return

        press(context, keys.KEY_DOWN, delay=1)
        time.sleep(2)

    raise AssertionError(f"Failed to find {result} in search menu")

@step('I select a movie poster on the search page')
def step_impl(context):
    press(context, keys.KEY_SELECT)


@step('I select the suggestion on the search page')
def step_impl(context):
    press(context, keys.KEY_SELECT)
