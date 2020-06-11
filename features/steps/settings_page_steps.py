from behave import step
from lib.vudu_image import match, ocr, Region, image_diff
from lib.helper import debug
from lib import keys
from features.steps.roku_steps import press
import time
import cv2
from lib.roku.regions import REGION_SETTINGS_TABS
from lib.roku_images import SETTINGS_MENU_SEL
from lib.consts import SETTINGS_PAGE_TABS
from lib.helper import search_by_text_from_ext_capture

@step('I select "{settings_tab}" on the settings page')
def step_impl(context, settings_tab):
    assert settings_tab in SETTINGS_PAGE_TABS, f"{settings_tab} is an unknown button"
    press(context, key=keys.KEY_SELECT)
    result = search_by_text_from_ext_capture(context, region=REGION_SETTINGS_TABS, left_bk=cv2.imread(SETTINGS_MENU_SEL), right_bk=None,
                                             target=settings_tab, key_to_press=keys.KEY_DOWN, max_tries=len(SETTINGS_PAGE_TABS))
    assert result, f"{settings_tab} is not found/selected"
    press(context, key=keys.KEY_SELECT)



