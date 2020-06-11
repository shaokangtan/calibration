from behave import step
from lib.vudu_image import match, ocr, Region, image_diff, get_default_match_parameter
from lib.helper import debug, WORK_DIR, search_by_image, SEARCH_BY_IMAGE_USE_BRIGHTNESS, get_frame_name
from lib import keys
from features.steps.roku_steps import press
import time
import cv2
import re
import os
from lib.roku.regions import REGION_PROGRESS_BAR, REGION_PROGRESS_BAR_TIME, REGION_PLAYBACK_PAGE_TITLE ,REGION_CHAPTER_GRID
from lib.roku_images import PLAYER_BACK, PLAYER_15_SECS, PLAYER_BUTTON_UHD_AT_PROGRESS_BAR, PLAYER_BUTTON_HDX_AT_PROGRESS_BAR,\
    PLAYER_SYMBOL_PROGRESS_BAR_UHD_UNHI, PLAYER_SYMBOL_PROGRESS_BAR_HDX_UNHI, PLAYER_SYMBOL_PROGRESS_BAR_SD_UNHI,\
    PLAYER_BUTTON_SD_AT_PROGRESS_BAR, PLAYER_CHAPTER_GRID, PLAYER_RW_BUTTON, KM_PLAYER_FF_BUTTON, PLAYER_CC, PLAYER_CC_UNHI, \
    PLAYER_CC_ENG, PLAYER_CC_ENG_UNHI, FAMILY_PLAY_SYMBOL_FOCUS, FAMILY_PLAY_SYMBOL_UNFOCUS, FAMILY_PLAY_SYMBOL_ON_FOCUS, \
    FAMILY_PLAY_SYMBOL_ON_UNFOCUS, PLAYER_SYMBOL_UHD, PLAYER_SYMBOL_HDX, PLAYER_SYMBOL_SD,\
    PLAYBACK_CHAPTER_CHAPTER_1, PLAYBACK_CHAPTER_CHAPTER_1_UNHI, PLAYBACK_CHAPTER_CHAPTER, PLAYBACK_CHAPTER_CHAPTER_UNHI

CHAPTER_GRID_COLS = 5
CHAPTER_GRID_ROWS = 3


playback_soft_buttons = {"back": [keys.KEY_LEFT, PLAYER_BACK],
                         "replay": [keys.KEY_LEFT, PLAYER_15_SECS],
                         "video quality": [keys.KEY_LEFT, PLAYER_BUTTON_HDX_AT_PROGRESS_BAR],
                         "uhd": [keys.KEY_LEFT, PLAYER_BUTTON_UHD_AT_PROGRESS_BAR],
                         "hdx": [keys.KEY_LEFT, PLAYER_BUTTON_HDX_AT_PROGRESS_BAR],
                         "sd": [keys.KEY_LEFT, PLAYER_BUTTON_SD_AT_PROGRESS_BAR],
                         "uhd unhilite": [keys.KEY_LEFT, PLAYER_SYMBOL_PROGRESS_BAR_UHD_UNHI],
                         "hdx unhilite": [keys.KEY_LEFT, PLAYER_SYMBOL_PROGRESS_BAR_HDX_UNHI],
                         "sd unhilite": [keys.KEY_LEFT, PLAYER_SYMBOL_PROGRESS_BAR_SD_UNHI],
                         "chapter": [keys.KEY_LEFT, PLAYER_CHAPTER_GRID],
                         "rewind": [keys.KEY_LEFT, PLAYER_RW_BUTTON],
                         "play or pause": [],
                         "fast forward": [keys.KEY_RIGHT, KM_PLAYER_FF_BUTTON],
                         "closed caption": [keys.KEY_RIGHT, PLAYER_CC],
                         "cc off": [keys.KEY_RIGHT, PLAYER_CC],
                         "cc off unhilite": [keys.KEY_RIGHT, PLAYER_CC_UNHI],
                         "cc on": [keys.KEY_RIGHT, PLAYER_CC_ENG],
                         "cc on unhilite": [keys.KEY_RIGHT, PLAYER_CC_ENG_UNHI],
                         "family play off": [keys.KEY_RIGHT, FAMILY_PLAY_SYMBOL_FOCUS],
                         "family play off unhilite": [keys.KEY_RIGHT, FAMILY_PLAY_SYMBOL_UNFOCUS],
                         "family play on": [keys.KEY_RIGHT, FAMILY_PLAY_SYMBOL_ON_FOCUS],
                         "family play on unhilite": [keys.KEY_RIGHT, FAMILY_PLAY_SYMBOL_ON_UNFOCUS]}

playback_video_quality = {"uhd": PLAYER_SYMBOL_UHD,
                          "hdx": PLAYER_SYMBOL_HDX,
                          "sd": PLAYER_SYMBOL_SD}

playback_chapter = {"chapter 1": PLAYBACK_CHAPTER_CHAPTER_1,
                    "chapter 1 unhilite": PLAYBACK_CHAPTER_CHAPTER_1_UNHI,
                    "chapter": PLAYBACK_CHAPTER_CHAPTER,
                    "chapter unhilite": PLAYBACK_CHAPTER_CHAPTER_UNHI
                    }

def navigate_to(context, button, focus_threshold=None):
    assert button in playback_soft_buttons
    press(context, keys.KEY_DOWN, 1)  # to show progress bar
    key_to_press = playback_soft_buttons[button][0]
    mp = (3, 0.65, *get_default_match_parameter()[2::])  # use fixed method 3 and threshold =0.65
    return search_by_image(context, REGION_PROGRESS_BAR, playback_soft_buttons[button][1],
                           key_to_press, max_tries=7, mp=mp, hist=SEARCH_BY_IMAGE_USE_BRIGHTNESS, focus_threshold=focus_threshold)


@step('I navigate to "{button}" button on the playback progress bar')
def step_impl(context, button):
    assert navigate_to(context, button), f"fail to navigate to {button}"

@step('I can find play time is reduced on the playback progress bar')
def step_impl(context):
    # read watch time and program time
    press(context, keys.KEY_DOWN)
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    counter = ocr(cv2.imread(context.frame), REGION_PROGRESS_BAR_TIME, grayscale=True, invert_grayscale=True, ocr_parameter='-c tessedit_char_whitelist=0123456789/:')
    debug(f"counter: {counter}\n")
    assert "/" in counter, "no counter found"
    play_time, program_time = parse_play_time_and_program_time(counter)
    debug(f"play time / program time: {play_time}/{program_time}")
    debug(f"prev. play time / program time: {context.play_time}/{context.program_time}")
    assert context.play_time > play_time


@step('I can find play time is increased on the playback progress bar')
def step_impl(context):
    # read watch time and program time
    press(context, keys.KEY_DOWN)
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    counter = ocr(cv2.imread(context.frame), REGION_PROGRESS_BAR_TIME, grayscale=True, invert_grayscale=True, ocr_parameter='-c tessedit_char_whitelist=0123456789/:')
    debug(f"counter: {counter}\n")
    assert "/" in counter, "no counter found"
    play_time, program_time = parse_play_time_and_program_time(counter)
    debug(f"play time / program time: {play_time}/{program_time}")
    debug(f"prev. play time / program time: {context.play_time}/{context.program_time}")
    assert context.play_time < play_time


@step('I can find play time is not the same on the playback progress bar')
def step_impl(context):
    # read watch time and program time
    press(context, keys.KEY_DOWN)
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    counter = ocr(cv2.imread(context.frame), REGION_PROGRESS_BAR_TIME, grayscale=True, invert_grayscale=True, ocr_parameter='-c tessedit_char_whitelist=0123456789/:')
    debug(f"counter: {counter}\n")
    assert "/" in counter, "no counter found"
    play_time, program_time = parse_play_time_and_program_time(counter)
    debug(f"play time / program time: {play_time}/{program_time}")
    debug(f"prev. play time / program time: {context.play_time}/{context.program_time}")
    assert abs(context.play_time - play_time) > 10


@step('I can find play time is the same on the playback progress bar')
def step_impl(context):
    # read watch time and program time
    press(context, keys.KEY_DOWN)
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    counter = ocr(cv2.imread(context.frame), REGION_PROGRESS_BAR_TIME, grayscale=True, invert_grayscale=True, ocr_parameter='-c tessedit_char_whitelist=0123456789/:')
    debug(f"counter: {counter}\n")
    assert "/" in counter, "no counter found"
    play_time, program_time = parse_play_time_and_program_time(counter)
    debug(f"play time / program time: {play_time}/{program_time}")
    debug(f"prev. play time / program time: {context.play_time}/{context.program_time}")
    assert abs(context.play_time - play_time) < 10, f"abs({context.play_time} - {play_time}) <10"


@step('I read play time and program time on the playback progress bar')
def step_impl(context):
    # read watch time and program time
    press(context, keys.KEY_DOWN)
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    counter = ocr(cv2.imread(context.frame), REGION_PROGRESS_BAR_TIME, grayscale=True, invert_grayscale=True, ocr_parameter='-c tessedit_char_whitelist=0123456789/:')
    debug(f"counter: {counter}\n")
    assert "/" in counter, "no counter found"
    play_time, program_time = parse_play_time_and_program_time(counter)
    debug(f"play time / program time: {play_time}/{program_time}")
    context.play_time = play_time
    context.program_time = program_time


@step('I can read play time and program time on the playback progress bar')
def step_impl(context):
    # read watch time and program time
    press(context, keys.KEY_DOWN)
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    counter = ocr(cv2.imread(context.frame), REGION_PROGRESS_BAR_TIME, grayscale=True, invert_grayscale=True, ocr_parameter='-c tessedit_char_whitelist=0123456789/:')
    debug(f"counter: {counter}\n")
    assert "/" in counter, "no counter found"
    play_time, program_time = parse_play_time_and_program_time(counter)
    debug(f"play time / program time: {play_time}/{program_time}")
    context.play_time = play_time
    context.program_time = program_time


def parse_play_time_and_program_time(counter):
    prog_time = counter.split("/")

    debug(f"parse_play_time_and_program_time: {prog_time}")
    play_pattern = '(\\d{1,2}):(\\d{1,2}):(\\d{1,2})$'
    program_pattern = '^(\\d{1,2}):(\\d{1,2}):(\\d{1,2})'
    valid_prog_time = []
    # clean up prog_time
    for i in range(len(prog_time)):
        valid_prog_time.append(prog_time[i].strip())
    player_time_sec = movie_time_sec = 0
    if len(valid_prog_time) >= 2:
        player_time = valid_prog_time[0]
        movie_time = valid_prog_time[1]
        counter_match = re.search(play_pattern, player_time)
        if counter_match is None:
            player_time_sec = 0
        else:
            player_time_sec = int(counter_match.group(1)) * 3600
            player_time_sec = player_time_sec + int(counter_match.group(2)) * 60
            player_time_sec = player_time_sec + int(counter_match.group(3))
        counter_match = re.search(program_pattern, movie_time)
        if counter_match is None:
            movie_time_sec = 0
        else:
            movie_time_sec = int(counter_match.group(1)) * 3600
            movie_time_sec = movie_time_sec + int(counter_match.group(2)) * 60
            movie_time_sec = movie_time_sec + int(counter_match.group(3))
    else:
        debug("no valid prog_time found")
    debug(f"parse_play_time_and_program_time: {player_time_sec} sec, {movie_time_sec} sec")
    return player_time_sec, movie_time_sec


def detect_shoppable_ads(context):
    debug("=== detect_shoppable_ads ===")
    frame = cv2.imread(context.frame)
    ads = "./images/Roku/shoppable_ads.png"
    ads1 = "./images/Roku/shoppable_ads_1.png"
    ads2 = "./images/Roku/shoppable_ads_2.png"
    ads_region = Region(x=1000, y=400, right=1280, bottom=600)
    ads1_region = Region(x=1000, y=360, right=1280, bottom=620)
    ads2_region = Region(x=1070, y=260, right=1166, bottom=350)
    return match(frame, ads, rads_region)[0] or \
        match(frame, ads1, ads1_region)[0] or \
        match(frame, ads2, ads2_region)[0]


def parse_ads_and_counter(ads, counter):
    counter_pattern = '(\\d+):(\\d+)'
    ads_pattern_of = 'Ad[\s]*(\\d+)[\s]*[o0]f[\s]*(\\d+)'
    if ads is None:
        ads_match = None
    else:
        ads = ads.replace('l', '1')
        ads_match = re.search(ads_pattern_of, ads)
    if counter is None:
        counter_match = None
    else:
        counter_match = re.search(counter_pattern, counter)
    # assert ads_match and counter_match, "=== Ads not found ==="
    if ads_match is None:
        current_ads = total_ads = None
    else:
        current_ads = int(ads_match.group(1))
        total_ads = int(ads_match.group(2))
    if counter_match is None:
        ads_sec = ads_min = None
    else:
        ads_min = int(counter_match.group(1))
        ads_sec = int(counter_match.group(2))

    return current_ads, total_ads, ads_min, ads_sec


@step('I can read ads time on the playback progress bar')
def step_impl(context):
    # read ads watch time and program time
    press(context, keys.KEY_DOWN)
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)

    shoppable_ads_detected = False
    if detect_shoppable_ads is True:
        shoppable_ads_detected = detect_shoppable_ads()
    else:
        shoppable_ads_detected = False

    region = Region(x=950, y=640, right=1110, bottom=720)
    ads = ocr(cv2.imread(context.frame), region, grayscale=True, invert_grayscale=True)
    debug(f"ads: {ads}")
    region = Region(x=1110, y=640, right=1280, bottom=720)
    counter = ocr(cv2.imread(context.frame), region, grayscale=True, invert_grayscale=True)
    debug(f"counter: {counter}")
    debug(f"ads/counter: {ads} / {counter}\n")
    assert "Ad" in ads or ":" in counter, "no ads found"
    current_ads, total_ads, ads_min, ads_sec = parse_ads_and_counter(ads, counter)

    if detect_shoppable_ads is True and shoppable_ads_detected is False:
        assert 200 == cam.get_frame(context.frame)
        shoppable_ads_detected = detect_shoppable_ads()

    debug(f"current_ads:{current_ads}, total_ads:{total_ads}, ads_min:{ads_min}, ads_sec:{ads_sec}, shoppable_ads_detected:{shoppable_ads_detected}")


@step('I wait ads to complete on the playback page')
def step_impl(context):
    # read ads watch time and program time
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    start = time.time()
    success = 0
    while True and time.time() < start+ 180:
        press(context, keys.KEY_DOWN) # to show progress bar
        assert 200 == cam.get_frame(context.frame)
        region = Region(x=900, y=640, right=1110, bottom=720)
        ads = ocr(cv2.imread(context.frame), region, grayscale=True, invert_grayscale=True)
        debug(f"ads: {ads}")
        region = Region(x=1110, y=640, right=1280, bottom=720)
        counter = ocr(cv2.imread(context.frame), region, grayscale=True, invert_grayscale=True)
        debug(f"counter: {counter}")
        debug(f"ads/counter: {ads} / {counter}\n")
        if  "Ad" not in ads and  ":" not in counter:
            success += 1
            if success > 3:
                return
    assert False, "ads is still playing"


playback_buttons = [keys.KEY_PLAYPAUSE, keys.KEY_AGAIN, keys.KEY_REWIND, keys.KEY_FASTFORWARD ]
@step('I press "{button}" on the playback page')
def step_impl(context, button):
    assert button in playback_buttons, f"{button} not known"
    press(context, button)
    pass


@step('I can read play program on the playback page')
def step_impl(context):
    pass


@step('I can rewind "{seconds}" seconds on the playback page')
def step_impl(context, seconds):
    pass


@step('I can fast forward "{seconds}" seconds on the playback page')
def step_impl(context, seconds):
    pass


video_qualities = ["uhd", "hdx", "sd"]
@step('I can change video quality to "{video_quality}" on the playback page')
def step_impl(context, video_quality):
    pass


# detect video changes in 30 seconds
@step('I can detect video on the playback page')
def step_impl(context):
    cam = context.cam
    frame = 0
    timeout = 60
    start = time.time()
    prev_frame = f"{WORK_DIR}/_frame_{frame}.png"
    assert 200 == cam.get_frame(path=prev_frame)
    num_diffs = 0
    while start + timeout > time.time():
        frame += 1
        new_frame = f"{WORK_DIR}/_frame_{frame}.png"
        assert 200 == cam.get_frame(path=new_frame)
        diff_percentage = image_diff(prev_frame, new_frame)
        if diff_percentage:
            debug(f"image_diff({num_diffs}/10):{diff_percentage}")
            num_diffs += 1
            if num_diffs > 10:
                return
        prev_frame = new_frame
    pass
    assert False, "no video detected"

# detect video changes in 30 seconds
@step('I can detect frozen video on the playback page')
def step_impl(context):
    cam = context.cam
    frame = 0
    new_frame = f"{WORK_DIR}/_frame{frame}.png"
    timeout = 30
    start = time.time()
    prev_frame = f"{WORK_DIR}/_frame_{frame}.png"
    assert 200 == cam.get_frame(path=prev_frame)
    num_diffs = 0
    while start + timeout > time.time():
        frame += 1
        new_frame = f"{WORK_DIR}/_frame_{frame}.png"
        assert 200 == cam.get_frame(path=new_frame)
        diff_percentage = image_diff(prev_frame, new_frame)
        if diff_percentage:
            debug(f"image_diff({num_diffs}/10):{diff_percentage}")
            num_diffs += 1
            if num_diffs > 10:
                assert False, "video is not frozen"
        prev_frame = new_frame
    pass


@step('I exit the playback page')
def step_impl(context):
    press(context, keys.KEY_BACK)


@step('I select "{button}" button on the playback progress bar')
def step_impl(context, button):
    press(context, keys.KEY_DOWN, 1)  # to show progress bar
    press(context, button)


@step('I can find closed caption button on the playback progress bar')
def step_impl(context):
    press(context, keys.KEY_DOWN, 1)  # to show progress bar
    pass


@step('I can find family play button on the playback progress bar')
def step_impl(context):
    press(context, keys.KEY_DOWN, 1)  # to show progress bar
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    frame = cv2.imread(context.frame)
    mp = (0, 0.8, *get_default_match_parameter()[2::])  # use ccorr_normed method 0 and threshold =0.65

    video_quality = "None"
    result = 0.0
    assert os.path.exists(playback_soft_buttons["play off unhilitefamily"][1])
    found = match(frame, cv2.imread(playback_soft_buttons['family play off unhilite'][1]), REGION_PROGRESS_BAR, match_parameter=mp)
    if found[0] is True:
        debug(f"found family play off\n")
        return
    assert os.path.exists(playback_soft_buttons["family play on unhilite"][1])
    found = match(frame, cv2.imread(playback_soft_buttons['family play on unhilite'][1]), REGION_PROGRESS_BAR, match_parameter=mp)
    if found[0] is True:
        debug(f"found family play on\n")
        return
    debug(f"fail to find family play on the progress barn\n")
    assert False, "fail to find family play on the progress bar"

@step('I can turn "{switch}" family play on the playback progress bar')
def step_impl(context, switch):
    press(context, keys.KEY_DOWN, 1)  # to show progress bar
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    frame = cv2.imread(context.frame)
    mp = (3, 0.7, *get_default_match_parameter()[2::])  # use ccorr_normed method 0 and threshold =0.65

    debug("check current switch\n")
    if switch == "off":
        debug(f"match {playback_soft_buttons['family play off unhilite'][1]}")
        if match(frame, cv2.imread(playback_soft_buttons["family play off unhilite"][1]), REGION_PROGRESS_BAR, match_parameter=mp)[0] is True:
            debug(f"family play is already {switch}\n")
            return
    elif switch == "on":
        debug(f"match {playback_soft_buttons['family play on unhilite'][1]}")
        if match(frame, cv2.imread(playback_soft_buttons["family play on unhilite"][1]), REGION_PROGRESS_BAR, match_parameter=mp)[0] is True:
            debug(f"family play is already {switch}\n")
            return
    debug(f"navigate_to family play {switch}\n")
    if navigate_to(context, "family play on" if switch == "off" else "family play off"):
        press(context, keys.KEY_SELECT, 1)
        # press(context, keys.KEY_UP, 1)
        press(context, keys.KEY_SELECT, 1)

        # dismiss family play popup
        press(context, keys.KEY_SELECT, 1)
        if switch == "on":
            press(context, keys.KEY_SELECT, 1) # dismiss family play popup

        return


def find_video_quality_on_playback_page(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    frame = cv2.imread(context.frame)
    mp = (3, 0.8, *get_default_match_parameter()[2::])  # use ccorr_normed method 0 and threshold =0.65

    video_quality = "None"
    result = 0.0
    assert os.path.exists(playback_video_quality["uhd"])
    found = match(frame, cv2.imread(playback_video_quality['uhd']), REGION_PLAYBACK_PAGE_TITLE, match_parameter=mp)
    if found[0] is True and found[2] > result:
        video_quality = "uhd"
        result = found[2]
        debug(f"found uhd")
    found = match(frame, cv2.imread(playback_video_quality['hdx']), REGION_PLAYBACK_PAGE_TITLE, match_parameter=mp)
    if found[0] is True and found[2] > result:
        video_quality = "hdx"
        result = found[2]
        debug(f"found hdx")
    found = match(frame, cv2.imread(playback_video_quality['sd']), REGION_PLAYBACK_PAGE_TITLE, match_parameter=mp)
    if found[0] is True and found[2] > result:
        video_quality = "sd"
        result = found[2]
        debug(f"found sd")
    print("\n\n")

    return video_quality


def find_video_quality_on_progress_bar(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    frame = cv2.imread(context.frame)
    mp = (3, 0.8, *get_default_match_parameter()[2::])  # use ccorr_normed method 0 and threshold =0.65

    video_quality = None
    found_uhd = match(frame, cv2.imread(playback_soft_buttons['uhd unhilite'][1]), REGION_PROGRESS_BAR, match_parameter=mp)[0]
    if found_uhd is True:
        video_quality = "uhd"
        debug(f"found uhd")
    found_hdx = match(frame, cv2.imread(playback_soft_buttons['hdx unhilite'][1]), REGION_PROGRESS_BAR, match_parameter=mp)[0]
    if found_hdx is True:
        video_quality = "hdx"
        debug(f"found hdx")
    found_sd = match(frame, cv2.imread(playback_soft_buttons['sd unhilite'][1]), REGION_PROGRESS_BAR, match_parameter=mp)[0]
    if found_sd is True:
        video_quality = "sd"
        debug(f"found sd")

    return video_quality


@step('I can find video quality button on the playback progress bar')
def step_impl(context):
    press(context, keys.KEY_DOWN, 1)  # to show progress bar


    found = find_video_quality_on_progress_bar(context)

    assert found is not None, "fail to find video quality buttons on the playback progress bar"


@step('I can find "{video_quality}" on the playback progress bar')
def step_impl(context, video_quality):
    press(context, keys.KEY_DOWN, 1)  # to show progress bar

    found = find_video_quality_on_progress_bar(context)

    assert found == video_quality , "fail to find video quality buttons on the playback progress bar"


@step('I can change video quality to "{video_quality}" on the playback progress bar')
def step_impl(context, video_quality):
    assert video_quality in video_qualities
    press(context, keys.KEY_DOWN)  # to show progress bar
    # find current video quaility
    current_video_qaulity = find_video_quality_on_progress_bar(context)
    assert current_video_qaulity is not None, "no video quality found in play page"
    if video_quality == current_video_qaulity:
        debug(f"video quality is already {video_quality}\n\n")
        return
    elif video_quality == current_video_qaulity:
        debug(f"video quality is already {video_quality}\n\n")
        return
    elif video_quality == current_video_qaulity:
        debug(f"video quality is already {video_quality}\n\n")
        return

    debug(f"navigate_to {current_video_qaulity}\n\n")
    if navigate_to(context, current_video_qaulity):
        press(context, keys.KEY_SELECT, 1)
        if video_quality == 'uhd' or video_quality == 'hdx':
            if current_video_qaulity == "sd":
                press(context, keys.KEY_UP, 1)
                press(context, keys.KEY_UP, 1)
            else:
                press(context, keys.KEY_UP, 1)
        if video_quality == 'sd':
            press(context, keys.KEY_UP, 1)
            press(context, keys.KEY_UP, 1)
        press(context, keys.KEY_SELECT, 1)
        return
    assert False, f"fail to change video quality to  {video_quality} "


@step('I can find video is playing "{video_quality}" on the playback page')
def step_impl(context, video_quality):
    press(context, keys.KEY_DOWN, 1)  # to show progress bar

    found = find_video_quality_on_playback_page(context)

    assert found == video_quality , f"fail to find playing '{video_quality}' on the playback page"


@step('I can turn "{switch}" closed caption on the playback page')
def step_impl(context, switch):
    assert switch == "on" or switch == "off"
    press(context, keys.KEY_DOWN, 1)  # to show progress bar
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    region = REGION_PROGRESS_BAR
    frame = cv2.imread(context.frame)
    mp = (3, 0.8, *get_default_match_parameter()[2::])  # use ccorr_normed method 0 and threshold =0.65

    if switch == "off":
        debug(f"match {playback_soft_buttons['cc off unhilite'][1]}")
        if match(frame, cv2.imread(playback_soft_buttons["cc off unhilite"][1]), region, match_parameter=mp)[0] is True:
            debug(f"closed caption is already {switch}\n\n")
            return
    elif switch == 'on':
        debug(f"match {playback_soft_buttons['cc on unhilite'][1]}")
        if match(frame, cv2.imread(playback_soft_buttons["cc on unhilite"][1]), region, match_parameter=mp)[0] is True:
            debug(f"closed caption is already {switch}")
            return
    debug(f"navigate_to {switch}\n\n")
    if navigate_to(context, "cc on" if switch == "off" else "cc off"):
        press(context, keys.KEY_SELECT, 1)
        # press(context, keys.KEY_UP, 1)
        press(context, keys.KEY_SELECT, 1)
        return
    assert False, f"fail to switch {switch} closed caption"


# return chpater
def find_current_chapters(context):
    press(context, keys.KEY_SELECT, 1)  # to show chapter grid
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(context.frame)
    frame = cv2.imread(context.frame)
    mp = (3, 0.8, *get_default_match_parameter()[2::])  # use ccorr_normed method 0 and threshold =0.65
    debug(f"match {playback_chapter['chapter']}")
    result = match(frame, cv2.imread(playback_chapter["chapter"]), REGION_CHAPTER_GRID, match_parameter=mp)
    print("\n\n")
    assert result[0] is True, f"fail to find current chapter"

    # find current chapter
    chapter_grids_width = REGION_CHAPTER_GRID.right - REGION_CHAPTER_GRID.x
    chapter_grids_height = REGION_CHAPTER_GRID.bottom - REGION_CHAPTER_GRID.top

    chapter_width = chapter_grids_width // CHAPTER_GRID_COLS
    chapter_height = chapter_grids_height // CHAPTER_GRID_ROWS
    chapters_regions = []
    for row in range(CHAPTER_GRID_ROWS):
        for col in range(CHAPTER_GRID_COLS):
            chapters_regions.append(Region(REGION_CHAPTER_GRID.x + col * chapter_width,
                                           REGION_CHAPTER_GRID.y + row * chapter_height,
                                           REGION_CHAPTER_GRID.x + (col + 1) * chapter_width,
                                           REGION_CHAPTER_GRID.y + (row + 1) * chapter_height))
            # debug(f"chapter: {len(chapters_regions) + 1}, {chapters_regions[-1]}")
    found_chapters = []
    focused_chapter = 0
    focused_chapter_area = 0
    for chp in range(len(chapters_regions)):
        area = Region.intersect_area(result[1], chapters_regions[chp])
        # debug(f"intersect area {result[1]} and  {chapters_regions[chp]}, area: {area}")
        if area > 0:
            found_chapters.append((chp, area))
            debug(f"chapter {chp + 1}, area: {area}")
            if area > focused_chapter_area:
                focused_chapter = chp + 1
                focused_chapter_area = area


    return focused_chapter


@step('I can find chapter on the playback page')
def step_impl(context):
    assert navigate_to(context, "chapter", focus_threshold=30), "fail to find chapter on progress bar"
    found_chapter = find_current_chapters(context)
    assert found_chapter > 0, "no focused chapter found"

@step('I can play chapter "{no}" on the playback page')
def step_impl(context, no):
    assert navigate_to(context, "chapter",  focus_threshold=30), "fail to find chapter on progress bar"

    # navigate to the dest. chapter
    found_chapter = find_current_chapters(context)
    assert found_chapter > 0, "no focused chapter found"
    cur_row = (found_chapter - 1) // CHAPTER_GRID_COLS
    cur_col = (found_chapter - 1) % CHAPTER_GRID_COLS

    debug(f"cur row:{cur_row}, cur col:{cur_col}")

    dest_row = (int(no) -1) // CHAPTER_GRID_COLS
    dest_col = (int(no) -1) % CHAPTER_GRID_COLS

    debug(f"dest row:{dest_row}, dest col:{dest_col}")

    for _ in range(abs(dest_col - cur_col)):
        if dest_col > cur_col :
            press(context, keys.KEY_RIGHT, 1)
        elif dest_col < cur_col:
            press(context, keys.KEY_RIGHT, 1)

    for _ in range(abs(dest_row - cur_row)):
        if dest_row > cur_row :
            press(context, keys.KEY_DOWN, 1)
        elif dest_row < cur_row:
            press(context, keys.KEY_UP, 1)

    press(context, keys.KEY_SELECT)

@step('I can click on stoppable ads on the playback page')
def step_impl(context):
    pass
