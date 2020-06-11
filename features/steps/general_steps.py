from behave import step
from lib.helper import find_selection_text, WORK_DIR, get_frame_name, debug, fuzzy_match
from lib.vudu_image import match, ocr, Region, get_default_match_parameter
from cv2 import *
from features.steps.roku_steps import press, goto_vudu_home, set_default_match_paramter, MATCH_PARAMETER, launch_vudu
import time
from lib import keys
from lib.roku_images import  MAIN_MENU_SEL_LEFT, MAIN_MENU_SEL_RIGHT, SETTINGS_MENU_SEL
from lib.consts import MENU_SCREEN_TABS

@step('I am already on the home menu page')
def step_impl(context):
    # check if we are on mai menu ? if not use home key to return home page.
    # if soptlight selection not on focus, restart Vudu
    press(context, keys.KEY_BACK)
    press(context, keys.KEY_REWIND)
    set_default_match_paramter(MATCH_PARAMETER)

    current_menu_sel_text = current_menu_selection(context)
    if current_menu_sel_text is not None and "spotlight" in current_menu_sel_text.lower():
        return
    launch_vudu(context)



@step('I can verify all navigation bar tabs visible on the menu page')
def step_impl(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    region = Region(0, 0, 1000, 70)
    match_result = ocr(cv2.imread(context.frame), region)
    for tab in MENU_SCREEN_TABS:
        #assert  tab  in match_result, f"{tab} not found in menu tabs"
        if  tab  not in match_result:
            debug(f"error: {tab} not found in menu tabs")
        else:
            debug(f"{tab} found in menu tabs")


settings_screen_tabs = ["My Account", "Family Settings", "Closed Captioning", "Playback Quality", "Autoplay Settings", "Accessibility",  "About" ]

def current_menu_selection(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    text_in_highlight, region = find_selection_text(cv2.imread(context.frame), cv2.imread(MAIN_MENU_SEL_LEFT), cv2.imread(MAIN_MENU_SEL_RIGHT),
                                                    x_offset=10, y_offset=5, region=Region(0, 0, 1000, 80))
    debug(f"current selection is {text_in_highlight} at {region}")
    return text_in_highlight

@step('I can verify "{tab}" selection on the menu page')
def step_impl(context, tab):
    assert tab in MENU_SCREEN_TABS, "error: {tab} is an unknown screen"
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    text_in_highlight, region = find_selection_text(cv2.imread(context.frame), cv2.imread(MAIN_MENU_SEL_LEFT), cv2.imread(MAIN_MENU_SEL_RIGHT),
                                                    region=Region(0, 0, 1000, 80), match_parameter=get_default_match_parameter())
    debug(f"current selection is {text_in_highlight} at {region}")
    assert tab.lower() in text_in_highlight.lower(), f"{tab} selection not found"


@step('I can verify "{tab}" selection on the settings page')
def step_impl(context, tab):
    assert tab in settings_screen_tabs, "error: {tab} is an unknown screen"
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    text_in_highlight, region = find_selection_text(cv2.imread(context.frame), cv2.imread(SETTINGS_MENU_SEL), None,
                                                    x_offset=20, region=Region(50, 170, 400, 540), match_parameter=get_default_match_parameter())
    debug(f"current selection is {text_in_highlight} at {region}")
    assert fuzzy_match(tab, text_in_highlight), f"{tab} selection not found"


@step('I navigate to "{screen}" on the menu page')
def step_impl(context, screen):
    assert screen in MENU_SCREEN_TABS, f"error: unknown {screen} tab on the menu page"
    if screen == MENU_SCREEN_TABS[0]:
        key = keys.KEY_LEFT
        max_try = 2
    else:
        max_try = len(MENU_SCREEN_TABS) - 1
        key = keys.KEY_RIGHT
    goto_vudu_home(context)
    # we are in menu screen now
    # check current selection is on spotlight
    cam = context.cam
    while max_try:
        context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
        assert 200 == cam.get_frame(path=context.frame)
        text_in_highlight, region = find_selection_text(cv2.imread(context.frame), cv2.imread(MAIN_MENU_SEL_LEFT), cv2.imread(MAIN_MENU_SEL_RIGHT),
                                                        x_offset=10, y_offset=5, region=Region(0, 0, 1000, 80), match_parameter=get_default_match_parameter())
        debug(f"current selection is {text_in_highlight} at {region}")
        if text_in_highlight is not None and screen.lower() in text_in_highlight.lower():
            debug(f"found {screen}")
            return
        press(context, key, 1)
        max_try -= 1
    assert False, f"fail to go to {screen} tab on the menu page"


@step('I wait "{seconds}" seconds')
def step_impl(context, seconds):
    debug(f"wait {seconds} seconds")
    time.sleep(int(seconds))
