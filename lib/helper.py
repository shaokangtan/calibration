import difflib
from lib.vudu_image import match, ocr, Region
import cv2
from datetime import datetime

def find_selection_text(frame, left_bk, right_bk, x_offset=0, y_offset=5, region=Region(x=0, y=0, right=1280, bottom=720),
                        convert_to_grayscale=True, match_parameter=None):
    print(f"find_selection_text: region {region}")
    debug("search for left bracket")
    l_result = match(frame, left_bk, region=region, match_parameter=match_parameter)
    if l_result[0] is False:
        debug("Error: fail to search left bracket")
        return None, None
    if left_bk == right_bk:
        region = Region(x=l_result[1].x + x_offset, y=l_resultl_result[1].y + y_offset,
                        right=l_result[1].right - x_offset, bottom=l_result[1].bottom - y_offset)
    else:
        debug("search for left bracket")
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


def debug(str):
    now = datetime.now()
    print(now.strftime("%m/%d/%Y, %H:%M:%S "), end="")
    print(str)
