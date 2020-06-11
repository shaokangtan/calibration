import difflib
from lib.vudu_image import match, ocr, Region, get_default_match_parameter
from features.steps.roku_steps import press
import cv2
from datetime import datetime
import time
from lib import keys

WORK_DIR = "./output/"

def find_selection_text(frame, left_bk, right_bk=None, x_offset=0, y_offset=5, region=Region(x=0, y=0, right=1280, bottom=720),
                        convert_to_grayscale=True, match_parameter=None):
    print(f"find_selection_text: region {region}")
    debug("search for left bracket")
    if match_parameter is None:
        match_parameter = get_default_match_parameter()

    l_result = match(frame, left_bk, region=region, match_parameter=match_parameter)
    if l_result[0] is False:
        debug("Error: fail to search left bracket")
        return None, None
    if right_bk is None:
        region = Region(x=l_result[1].x + x_offset, y=l_result[1].y + y_offset,
                        right=l_result[1].right - x_offset, bottom=l_result[1].bottom - y_offset)
    else:
        debug("search for right bracket")
        r_result = match(frame, right_bk, region=region, match_parameter=match_parameter)
        if r_result[0] is False:
            debug("Error: fail to search right bracket")
            return None, None
        if l_result[1].right + x_offset > r_result[1].x - x_offset:
            return None, None
        region = Region(x=l_result[1].x + x_offset, y=l_result[1].y + y_offset,
                        right=r_result[1].right - x_offset, bottom=r_result[1].bottom - y_offset)
        print(f"find_selection_text: search text in {region}")
    if convert_to_grayscale is True:
        text = ocr(frame=cv2.cvtColor(frame[region.y:region.bottom, region.x:region.right], cv2.COLOR_BGR2GRAY))

    else:
        text =  ocr(frame=frame[region.y:region.bottom, region.x:region.right])
    print(f"find_selection_text: found {text} in selected region")
    return text, region

# target: is either a string or a list of string
def search_by_text_from_ext_capture(context, region, left_bk, right_bk, target, key_to_press, max_tries, x_offset=0, y_offset=5,
                                    ignore_space=False,
                                    match_parameter=None,
                                    fuzzy_match_ratio=0.6,
                                    convert_to_grayscale=True, # !!! do not change the parameters below !!! -Henry
                                    key_to_press_func=None):
    """
    Read/Scan text in with referent background(by 1 pixel vertical line of that background).
    :param y_offset:
    :param x_offset:
    :param ignore_space:
    :param ocr_mode:
    :param region: region to focus on.
    :param background: image of one pixel line in vertical
    :param target: expected text string when scan out base on back-ground color image1px
    :param key_to_press: what direction key of the key you try to press
    :param max_tries: how many presses
    :param region: region to focus on.
    :return: (bool) whether text is found.
    """
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    if type(target) is list:
        targets = target
    else:
        targets =[ target ]
    if ignore_space is True:
        for i in range(len(targets)):
            targets[i] = targets[i].replace(" ", "")
    print("\n\n=== search_by_text: look for text [{}] ====\n".format(target))
    for _ in range(max_tries):
        assert 200 == cam.get_frame(path=context.frame)
        frame = cv2.imread(context.frame)
        text_read_out, _ = find_selection_text(frame, left_bk, right_bk, x_offset=x_offset, y_offset=y_offset,
                                               region=region, match_parameter=match_parameter,
                                               convert_to_grayscale=convert_to_grayscale)
        if text_read_out is not None:
            if ignore_space is True:
                text_read_out = text_read_out.replace(" ", "")
            for target in targets:
                if target in text_read_out:
                    print(f"\n\n==== Found text !! {text_read_out}, returning ... ====\n\n")
                    return True
                else:
                    if fuzzy_match(target, text_read_out, fuzzy_match_ratio):
                        print("\n\n==== fuzzy_match found text !! [%s], returning ... ====\n\n" % text_read_out)
                        return True
                    print("===== Read out text [{}] but not match, proceed to next scan ... ".format(text_read_out))
        print(f"press {key_to_press}")
        if not key_to_press_func:
            press(context, key_to_press, delay=2)
        else:
            key_to_press_func(key_to_press, 2)
        # press_key_and_wait(key_to_press, 3)
    return False


SEARCH_BY_IMAGE_USE_BRIGHTNESS = 3
SEARCH_BY_IMAGE_USE_RED_COLOR = 0
SEARCH_BY_IMAGE_USE_GREEN_COLOR = 1
SEARCH_BY_IMAGE_USE_BLUE_COLOR = 2


# hist = None, 0, 1, 2, 3, 4
#        0, use r for measurement
#        1, use g for measurement
#        2, use b for measuement
#        3, use brightness for mesaurement
def search_by_image(context, region, target, key_to_press, max_tries, interval_secs=1, mp=None, hist=None, key_to_press_func=None, focus_threshold=None):
    """
    This function is mainly used in the menu or sub-menu where direction could be horizontal or vertical.
    :param mp: the match_parameters
    :param region: narrow down the region to search
    :param target: target image
    :param key_to_press: direction to press the arrow key on the remote control
    :param max_tries: maximum number of presses
    :param mp: match parameters for image match
    :param hist: use historgram/brightness to compare the difference to avoid false positive
    :return: (bool) whether image is found.
    """
    debug(f" Search by image: {target}, region: {region}, max_tries: {max_tries}, mp: {mp}, hist: {hist}")
    MIN_DIFFERENCE = 0.15
    ex_per_pixel = None
    ex_region = None
    found = 0
    cam = context.cam
    for tries in range(max_tries):
        path = get_frame_name(context, f"{WORK_DIR}/_frame.png")
        cam.get_frame(path)
        _frame = cv2.imread(path)
        if mp is not None:
            result = match(frame=_frame, image=cv2.imread(target), region=region, match_parameter=mp)
        else:
            result = match(frame=_frame, image=cv2.imread(target), region=region)
        if result[0] is True:
            found += 1
            # if wait_until(lambda: match(image=target), timeout_secs=1):
            if hist is None:
                print("\n\n==== Found image !! returning... ====\n\n")
                return True
            else:
                print(f"\n\n==== Found image !! check hist... {tries}====\n\n")
                # copy the detected image
                found_target = _frame[result[1].y:result[1].bottom, result[1].x:result[1].right]
                debug(f"frame shape{_frame.shape}, found target shape:{found_target.shape}, "
                      f"region: {result[1]}, size: {found_target.size}")
                size = found_target.shape[0] * found_target.shape[1]
                if hist != SEARCH_BY_IMAGE_USE_BRIGHTNESS:
                    total_r = total_g = total_b = 0
                    for r in (found_target):
                        for c in (r):
                            total_b += c[0]
                            total_g += c[1]
                            total_r += c[2]
                    debug(f"total r, g, b: {total_r, total_g, total_b}, avg. r, g, b "
                          f"{total_r/size, total_g/size, total_b/size}")
                    if hist == SEARCH_BY_IMAGE_USE_RED_COLOR:
                        total = total_r
                        diff = 1.0 - (total_g + total_b) / 2 / total_r
                        debug(f"diff = {diff}")
                    elif hist == SEARCH_BY_IMAGE_USE_GREEN_COLOR:
                        total = total_g
                        diff = 1.0 - (total_r + total_b) / 2 / total_g
                        debug(f"diff = {diff}")
                    elif hist == SEARCH_BY_IMAGE_USE_BLUE_COLOR:
                        total = total_b
                        diff = 1.0 - (total_r + total_g) / 2 / total_b
                        debug(f"diff = {diff}")
                    per_pixel = total / size
                    threshold = 15.0 if focus_threshold is not None else focus_threshold
                else:
                    # path = f"{WORK_DIR}/_frame_{tries}_c.png"
                    # cv2.imwrite(path, found_target)
                    greyscale_found_target = cv2.cvtColor(found_target, cv2.COLOR_BGR2GRAY)
                    # path = f"{WORK_DIR}/_frame_{tries}_g.png"
                    # cv2.imwrite(path, greyscale_found_target)

                    debug(f"greyscale found target shape: {greyscale_found_target.shape}")
                    total = 0
                    for i in range(greyscale_found_target.shape[0]):
                        total += sum(greyscale_found_target[i])
                    per_pixel = total / size
                    threshold = 40.0 if focus_threshold is None else focus_threshold

                debug(f"total: {total}, per pixel avg: {per_pixel}")
                # continue
                if ex_per_pixel is None:
                    ex_per_pixel = per_pixel
                    ex_region = result[1]
                else:
                    debug (f"=== Region.intersect: {Region.intersect(ex_region,result[1])}")
                    if Region.intersect(ex_region,result[1]) is False:
                        print(f"=== result region is changed, reset ")
                        ex_per_pixel = per_pixel
                        ex_region = result[1]
                    else:
                        debug(f"ex per pixel: {ex_per_pixel}, per pixel: {per_pixel}, diff: "
                              f"{(per_pixel - ex_per_pixel)/per_pixel * 100} %")
                        if per_pixel > ex_per_pixel and ((per_pixel - ex_per_pixel) / per_pixel * 100 > threshold):
                            if hist == SEARCH_BY_IMAGE_USE_BRIGHTNESS:
                                print("\n\n==== Found image in current position !! returning... ====\n\n")
                                return True
                            else:
                                # Due to the background video can introduce brightness influnce,
                                # if the difference between the other two colors are too low,
                                # we will just assume it is a false positive
                                if diff > MIN_DIFFERENCE:
                                    print(f"\n\n==== Found image in current position, diff: {diff} !! returning... "
                                          f"====\n\n")
                                    return True
                        # elif tries == 1 and per_pixel < ex_per_pixel and (
                        elif per_pixel < ex_per_pixel and (
                                # if highlight is the previous one, it is moving away instead of moving in
                                (ex_per_pixel - per_pixel) / per_pixel * 100 > threshold):
                            debug("\n\n==== Found image in last position ? verifying ... ====\n\n")
                            if hist == SEARCH_BY_IMAGE_USE_BRIGHTNESS or (hist != SEARCH_BY_IMAGE_USE_BRIGHTNESS and diff > MIN_DIFFERENCE): # diff is used to make sure the difference is not introduced by fade in effect
                                debug("\n\n==== Found image in last position!! verified and returning... ====\n\n")
                                if key_to_press == keys.KEY_RIGHT:
                                    if not key_to_press_func:
                                        press(context, keys.KEY_LEFT)
                                    else:
                                        key_to_press_func(keys.KEY_LEFT, 2)
                                elif key_to_press == keys.KEY_LEFT:
                                    if not key_to_press_func:
                                        press(context,keys.KEY_RIGHT)
                                    else:
                                        key_to_press_func(keys.KEY_LEFT, 2)
                                elif key_to_press == keys.KEY_UP:
                                    if not key_to_press_func:
                                        press(context,keys.KEY_DOWN)
                                    else:
                                        key_to_press_func(keys.KEY_LEFT, 2)
                                elif key_to_press == keys.KEY_DOWN:
                                    if not key_to_press_func:
                                        press(context,keys.KEY_UP)
                                    else:
                                        key_to_press_func(keys.KEY_LEFT, 2)
                                else:
                                    assert_that(False, "dont know how to navigate back to previous position")
                                return True
                        else:
                            debug(f"\n\n=== Still not sure why we come here! per_pixel:{per_pixel}, ex_per_pixel{ex_per_pixel}, diff: {(ex_per_pixel - per_pixel) / per_pixel * 100 } ===\n\n")
                        ex_per_pixel = per_pixel
        stable_secs=1.0
        if not key_to_press_func:
            press(context, key_to_press, 1)
            if interval_secs > stable_secs:
                time.sleep(interval_secs - stable_secs)
            # helper.press_key_and_wait(key_to_press, 2.0)
        else:
            key_to_press_func(context, key_to_press)

    # To Be improved. If this button is the only button, there is no actions to compare. -Henry
    if found == max_tries:
        debug("Found image but no actions detected !!  returning...")
        return True
    return False

def get_frame_name(context, prefix):
    context.frame_no += 1
    if ".png" in prefix :
        path= prefix.replace('.png','')
    elif ".PNG" in prefix:
        path= prefix.replace('.PNG','')
    else:
        path=prefix
    return f"{path}-{context.frame_no}.png"

def _fuzzy_match(a, b, ratio=0.6):
    # fuzzy match two words
    # sample usage: assert fuzzy_match(page.movie_title, "Buried")
    print("fuzzy_match: {}".format(difflib.SequenceMatcher(a=a, b=b).ratio()))
    return difflib.SequenceMatcher(a=a, b=b).ratio() > ratio


def fuzzy_match(a, b, ratio=0.6, is_paragraph=None):
    # fuzzy match two words
    # sample usage: assert fuzzy_match(page.movie_title, "Buried")
    # if is_paragraph, match the word within a paragraph
    if a is None or b is None:
        print("=== input is None, return False")
        return False
    a_len = len(a)
    b_len = len(b)
    if is_paragraph is None or a_len > b_len:
        return _fuzzy_match(a, b, ratio)
    offset = 0
    while offset + a_len < b_len:
        if _fuzzy_match(a, b[offset:offset + a_len], ratio) is True:
            print(f"offset: { offset }")
            return True
        offset += 1
    return _fuzzy_match(a, b, ratio)


def move_to_char_pos_keyboard(context, curr_row=None, curr_col=None, next_row=None, next_col=None):
    """
    This function calculate where to move to next character with current coordinate and next coordinate on keyboard
    :param curr_row: (int) current character row location
    :param curr_col: (int) current character column location
    :param next_row: (int) next character row location
    :param next_col: (int) next character column location
    """
    if curr_row is None:
        curr_row = 0
    if curr_col is None:
        curr_col = 0
    if next_row is None:
        next_row = 0
    if next_col is None:
        next_col = 0

    # row to go up/down"
    if next_row > curr_row:
        if next_col > curr_col:
            for _ in range(curr_col, next_col):
                press(context, keys.KEY_RIGHT, 1)
        elif next_col < curr_col:
            for _ in range(next_col, curr_col):
                press(context, keys.KEY_LEFT, 1)

        for _ in range(curr_row, next_row):
            press(context, keys.KEY_DOWN, 1)

    elif next_row < curr_row:
        for _ in range(next_row, curr_row):
            press(context, keys.KEY_UP, 1)
        if next_col > curr_col:
            for _ in range(curr_col, next_col):
                press(context, keys.KEY_RIGHT,1)

        elif next_col < curr_col:
            for _ in range(next_col, curr_col):
                press(context, keys.KEY_LEFT, 1)

    else:
        if next_col > curr_col:
            for _ in range(curr_col, next_col):
                press(context, keys.KEY_RIGHT, 1)

        elif next_col < curr_col:
            for _ in range(next_col, curr_col):
                press(context, keys.KEY_LEFT, 1)


def find_keyboard_mapping(keyboard_layout, char):
    """
    This function maps coordinates of all characters to an array depending on which
    OS (WebOS or Lua)
    Convert every pass-in character char to upper case
    :param keyboard_layout: (array).
    :param char: (str)
    :return: (int, int) current coordinate x, y of input char
    """

    print("========= Picked keyboard ========",)
    for s_row in range(0, len(keyboard_layout)):
        for s_col in range(0, len(keyboard_layout[0])):
            if keyboard_layout[s_row][s_col] == char.upper():
                print(f"==== find [{char}] position: s_row = [{s_row}], s_col = [{s_col}] ===")
                return [s_row, s_col]

    assert False, "Coordinate for Char [{}] not found ===\n\n".format(char)


def debug(str):
    now = datetime.now()
    print(now.strftime("%m/%d/%Y, %H:%M:%S "), end="")
    print(str)
