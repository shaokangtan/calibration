from lib.vudu_image import match, ocr, Region, image_diff
from lib.helper import get_frame_name, WORK_DIR, search_by_text_from_ext_capture
from lib import keys
from features.steps.roku_steps import press
import time
import cv2
from lib.roku_images import DETAIL_TAB_SEL
from lib.roku.regions import REGION_DETAIL_BUTTONS, REGION_DETAILS_PAGE_TITLE
from lib.consts import DETAIL_PAGE_BUTTONS

def title(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    frame = cv2.imread(context.frame)
    return ocr(frame, region=REGION_DETAILS_PAGE_TITLE)


@step('I select "{button}" on the detail page')
def step_impl(context, button):
    assert button in DETAIL_PAGE_BUTTONS, f"{button} is an unknown button"
    result = search_by_text_from_ext_capture(context, region=REGION_DETAIL_BUTTONS, left_bk=cv2.imread(DETAIL_TAB_SEL), right_bk=None,
                                             target=button, key_to_press=keys.KEY_DOWN, max_tries=len(DETAIL_PAGE_BUTTONS))
    assert result, f"{button} is not found/selected"
    context.movie_title = title(context)
    press(context, key=keys.KEY_SELECT)
