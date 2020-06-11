from behave import step
from lib.vudu_image import match, ocr, get_default_match_parameter
from lib.helper import debug, get_frame_name, WORK_DIR, fuzzy_match, find_selection_text
from lib import keys
from features.steps.roku_steps import press
import time
import cv2
from lib.roku.regions import  REGION_PURCHASE_POPUP_GRID_VIDEO_QAULITY, REGION_PURCHASE_POPUP_TITLE, REGION_PURCHASE_POPUP_GRID_PRICE, \
                            REGION_CONFIRM_PURCHASE_POPUP_TITLE, REGION_THANK_YOU_PURCHASE_POPUP_TITLE, REGION_PURCHASE_POPUP_MOVIE_TITLE, \
                            REGION_SINGLE_PRICE_GRID
from lib.roku_images import PURCHASE_POPUP_UHD_UH, PURCHASE_POPUP_HDX_UH, PURCHASE_POPUP_SD_UH, PURCHASE_POPUP_PRICE_20X36, \
                            MOVIE_PURCHASE_POPUP_CANCEL_BUTTON, PURCHASE_POPUP_BUY_UH, PURCHASE_POPUP_RENT, PURCHASE_ORANGE_DISCOUNT,\
                            PURCHASE_ORANGE_DISCOUNT_UH, ORANGE_DISCOUNT_PRICE_DETAILS, PURCHASE_POPUP_BUY_HD, PURCHASE_POPUP_BUY_SD,\
                            PURCHASE_POPUP_BUY_4K, PURCHASE_POPUP_RENT_SD, PURCHASE_POPUP_RENT_HD, \
                            PURCHASE_POPUP_RENT_4K, PURCHASE_POPUP_PRICE_GRID_SEL
import lib.consts as consts
price_4k = '4K'

def visible(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    frame = cv2.imread(context.frame)
    return is_old_purchase_popup_visible(context, frame) or is_single_purchase_price_visible(context, frame)


def is_old_purchase_popup_visible(context, frame):
    read_title = title(context, frame).upper()
    print("Read out title on purchase pop-up page: {} ".format(read_title))
    return (consts.OWN_RENT_TITLE.upper() in read_title) or (consts.BUY_RENT_TITLE.upper() in read_title) or \
           (consts.PRE_ORDER_RENT_TITLE.upper() in read_title) or (consts.RENT_BUY_TITLE.upper() in read_title)


def title(context, frame):
    purchase_title =  ocr(frame, region=REGION_PURCHASE_POPUP_TITLE)
    debug(f"tile:{purchase_title}")
    return purchase_title


def purchase_popup_movie_title(context, frame):
    purchase_title =  ocr(frame, region=REGION_PURCHASE_POPUP_MOVIE_TITLE)
    debug(f"tile:{purchase_title}")
    return purchase_title


def confirm_purchase_popup_title(context, frame):
    purchase_title = ocr(frame, region=REGION_CONFIRM_PURCHASE_POPUP_TITLE)
    purchase_title_1 = ocr(frame, region=REGION_CONFIRM_PURCHASE_POPUP_TITLE, grayscale=True, invert_grayscale=True)
    debug(f"confirm purchase popup tile:{purchase_title}")
    return purchase_title


def thank_you_purchase_popup_title(context, frame):
    purchase_title =  ocr(frame, region=REGION_THANK_YOU_PURCHASE_POPUP_TITLE)
    debug(f"thank you purchase popup tile:{purchase_title}")
    return purchase_title


def is_hdx_visible(context, frame):
    """
    :return: HDX icon on screen
   """
    return match(frame, PURCHASE_POPUP_HDX_UH, REGION_PURCHASE_POPUP_GRID_VIDEO_QAULITY)


def is_sd_visible(context, frame):
    """
    :return: SD icon on screen.
   """
    return match(frame, PURCHASE_POPUP_SD_UH, REGION_PURCHASE_POPUP_GRID_VIDEO_QAULITY)


def is_uhd_visible(context, frame):
    """
    :return: un-highlighted SD icon on screen.
   """
    return match(frame, PURCHASE_POPUP_UHD_UH, REGION_PURCHASE_POPUP_GRID_VIDEO_QAULITY)


def check_discount_price(context, frame):
    """
    :return: if discount_price is visible.
   """
    return (match(frame, PURCHASE_ORANGE_DISCOUNT)[0]) or \
           (match(frame, PURCHASE_ORANGE_DISCOUNT_UH)[0])


def is_discount_price_visible(context, frame):
    """
    :return: if discount_price (orange price) is visible.
    """
    return match(frame, ORANGE_DISCOUNT_PRICE_DETAILS)


def is_single_purchase_price_un_focus_buy_visible(context, frame):
    # unfocused buy
    return match(frame, PURCHASE_POPUP_BUY_UH)[0]
    #match_parameters=match_parameters(threshold=self.thread_hold_high, confirm=ConfirmMethod.ABSDIFF))


def navigate_to_single_price_grid_buy(context, quality=consts.QUALITY_HDX):
    # new single price pop up
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    frame = cv2.imread(context.frame)
    assert is_single_purchase_price_buy_visible(context, frame), "Single price buy is not visible."
    if is_single_purchase_price_un_focus_buy_visible(context,frame):
        press(context, keys.KEY_RIGHT, 1)

    print(f"Move to {quality}")
    price_selection = current_price_grid_selection(context)
    print(f"The selected price option is: {price_selection}")

    if quality == consts.QUALITY_ANY:
        return

    if quality == consts.QUALITY_HDX:
        if price_4k in price_selection:
            press(context, keys.KEY_DOWN, 1)

        price_selection = current_price_grid_selection(context)
        print(f"HDX: The selected price option is: {price_selection}")
        if consts.QUALITY_HDX in price_selection:
            return True
    elif quality == consts.QUALITY_SD:
        press(context, keys.KEY_DOWN, 1)
        press(context, keys.KEY_DOWN, 1)
        return True
    else:
        if price_4k in price_selection:
            return True

    assert False, f"Failed to navigate to rent {quality} option"

def current_price_grid_selection(context, frame=None):
    # sel_text = find_selection_horizontal_repeat(frame=get_frame(),
    #                                             background=self.images.PURCHASE_POPUP_PRICE_GRID_PIX,
    #                                             region=REGION_SINGLE_PRICE_GRID).text
    # print(f"=== Dump current price selection: {sel_text}")
    # return sel_text
    if frame is None:
        cam = context.cam
        context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
        assert 200 == cam.get_frame(path=context.frame)
        frame = cv2.imread(context.frame)
    mp = (3, 0.8, *get_default_match_parameter()[2::])  # use ccorr_normed method 0 and threshold =0.65
    sel_text, region = find_selection_text(frame, left_bk=PURCHASE_POPUP_PRICE_GRID_SEL, right_bk=None,
                                           x_offset=10, y_offset=10, region=REGION_SINGLE_PRICE_GRID,
                                           match_parameter=mp)
    return sel_text

def current_price_grid_selection1(context, frame=None):
    return ""
    # sel_text = find_selection_horizontal_repeat(frame=get_frame(),
    #                                             background=self.images.PURCHASE_POPUP_PRICE_GRID_PIX1,
    #                                             region=REGION_SINGLE_PRICE_GRID).text
    # selection = sel_text.replace('\n', ' ')
    # print(f"=== Dump current price selection 1: {selection}")
    # return selection

def current_price_grid_selection2(context, frame=None):
    return ""
    # sel_text = find_selection_horizontal_repeat(frame=get_frame(),
    #                                             background=self.images.PURCHASE_POPUP_PRICE_GRID_PIX2,
    #                                             region=REGION_SINGLE_PRICE_GRID).text
    # selection = sel_text.replace('\n', ' ')
    # print(f"=== Dump current price selection 2: {selection}")
    # return selection


def is_single_purchase_price_rent_visible(context, frame=None):
    if frame is None:
        cam = context.cam
        context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
        assert 200 == cam.get_frame(path=context.frame)
    return match(context.frame, PURCHASE_POPUP_RENT)


def is_single_purchase_price_buy_visible(context, frame=None):
    if frame is None:
        cam = context.cam
        context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
        assert 200 == cam.get_frame(path=context.frame)
        frame = cv2.imread(context.frame)
    return is_single_purchase_price_focus_buy_visible(context, frame) is not None or \
           is_single_purchase_price_un_focus_buy_visible(context, frame)

def is_single_purchase_price_un_focus_buy_visible(context, frame):
    # unfocused buy
    return match(frame, PURCHASE_POPUP_BUY_UH)[0]
                 # match_parameters=match_parameters(threshold=self.thread_hold_high, confirm=ConfirmMethod.ABSDIFF))

def is_single_purchase_price_focus_buy_visible(context, frame):

        # return match(self.images.PURCHASE_POPUP_BUY_EP, frame=self._frame, match_parameters=match_parameters(
        #         threshold=self.thread_hold_high, confirm=ConfirmMethod.ABSDIFF)) or \
        #        self.is_single_purchase_price_buy_4k_visible or self.is_single_purchase_price_buy_hdx_visible or match(
        #     self.images.PURCHASE_POPUP_BUY_SEASON, frame=self._frame, match_parameters=match_parameters(
        #         threshold=self.thread_hold_high, confirm=ConfirmMethod.ABSDIFF))

        cur_sel = current_price_grid_selection(context, frame)
        if cur_sel:
            return "Buy" in cur_sel
        return None

def is_single_purchase_price_buy_hdx_visible(context, frame):
        return match(frame, PURCHASE_POPUP_BUY_HD)[0]
        # match_parameters=match_parameters(threshold=self.thread_hold_high, confirm=ConfirmMethod.ABSDIFF))

def is_single_purchase_price_buy_sd_visible(context, frame):
    # unfocused buy
    return match(frame, PURCHASE_POPUP_BUY_SD)[0]
    # match_parameters=match_parameters(threshold=self.thread_hold_high, confirm=ConfirmMethod.ABSDIFF))

def is_single_purchase_price_buy_4k_visible(context, frame):
    # focused buy
    return match(frame, PURCHASE_POPUP_BUY_4K)[0]
    # match_parameters=match_parameters(threshold=self.thread_hold_high, confirm=ConfirmMethod.ABSDIFF))

def is_single_purchase_price_rent_hdx_visible(context, frame):
    return match(frame, PURCHASE_POPUP_RENT_HD)[0]
    # match_parameters=match_parameters(threshold=self.thread_hold_low, confirm=ConfirmMethod.ABSDIFF))

def is_single_purchase_price_rent_sd_visible(context, frame):
    return match(frame, PURCHASE_POPUP_RENT_SD)[0]
    #  match_parameters=match_parameters(threshold=self.thread_hold_low, confirm=ConfirmMethod.ABSDIFF))

def is_single_purchase_price_rent_4k_visible(context, frame):
    return match(frame, PURCHASE_POPUP_RENT_4K)[0]
    # match_parameters=match_parameters(threshold=self.thread_hold_low, confirm=ConfirmMethod.ABSDIFF))

# def is_single_purchase_price_select_button_visible(context, frame):
#     # select button inside tab
#     return match(frame, PURCHASE_POPUP_SELECT_BTN)[0]
#     # match_parameters=match_parameters(threshold=self.thread_hold_low, confirm=ConfirmMethod.ABSDIFF))



def is_single_purchase_price_visible(context, frame):
    return is_single_purchase_price_rent_visible(context, frame) or is_single_purchase_price_buy_visible(context, frame)

def navigate_to_single_price_grid_rent(context, quality=consts.QUALITY_HDX):
        # new single price pop
        cam = context.cam
        context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
        assert 200 == cam.get_frame(path=context.frame)
        frame = cv2.imread(context.frame)
        assert is_single_purchase_price_rent_visible(context, frame), "Single price rent is not visible."
        price_selection = current_price_grid_selection(context, frame)
        print(f"The selected price option is: {price_selection}")

        print(f"Move to {quality}")
        if quality == consts.QUALITY_ANY:
            return

        if quality == consts.QUALITY_HDX:
            if price_4k in price_selection:
                press(context, keys.KEY_DOWN, 1)

            price_selection = current_price_grid_selection(context)
            print(f"The selected price option is: {price_selection}")
            # HDX + SD
            if consts.QUALITY_HDX in price_selection:
                return True
        elif quality == consts.QUALITY_SD:
            press(context, keys.KEY_DOWN, 1)
            press(context, keys.KEY_DOWN, 1)
            return True
        else:
            if price_4k in price_selection:
                return True

        assert False, f"Failed to navigate to rent {quality} option"

def select_own_button(context, quality=consts.QUALITY_HDX):
    """
    Arrow right to move to Own button. The button orders are: Rent -> Own -> Disc
    :quality: (str) HDX or SD
    :return: new page
    """
    if is_single_purchase_price_buy_visible(context):
        print("Info: Single price grid is enabled.")
        navigate_to_single_price_grid_buy(context, quality)
    else:
        print("Info: This is old price grid")
        press(context, keys.KEY_RIGHT)  # TBD: fix the case there is no rent but buy and D+D options
        assert (quality in consts.QUALITY)
        current_quality = get_current_rental_quality(context)
        print(f"current quality: {current_quality}, dest quality: {quality}")
        navigate_to_rent_own_button(context, quality)

    print(f"=== Press [OK] to select own quality: {quality}")
    press (context, keys.KEY_SELECT, 3)
    # show confirm purchase popup


def navigate_to_rent_button(context, quality=consts.QUALITY_HDX):

    if is_single_purchase_price_rent_visible(context):
        return navigate_to_single_price_grid_rent(context, quality)
    else:
        return navigate_to_rent_own_button(context, quality)


def navigate_to_rent_own_button(context, quality=consts.QUALITY_HDX):
        assert (quality in consts.QUALITY)
        current_quality = get_current_rental_quality(context)
        print(f"The current quality: {current_quality}")
        if quality == consts.QUALITY_ANY:
            assert current_quality in consts.QUALITY
            return
        print("current quality: {}, dest quality: {}".format(current_quality, quality))
        for i in range(3):
            if quality == consts.QUALITY_SD:
                if current_quality == consts.QUALITY_UHD:
                    print("Move down")
                    press(context, keys.KEY_DOWN, 1)
                elif current_quality == consts.QUALITY_HDX:
                    print("Move down")
                    press(context, keys.KEY_DOWN, 1)
                else:
                    assert (current_quality == consts.QUALITY_SD)
                    return
            elif quality == consts.QUALITY_HDX:
                if current_quality == consts.QUALITY_UHD:
                    print("Move down")
                    press(context, keys.KEY_DOWN, 1)
                elif current_quality == consts.QUALITY_SD:
                    print("Move up")
                    press(context, keys.KEY_UP, 1)
                else:
                    assert (current_quality == consts.QUALITY_HDX)
                    return
            elif quality == consts.QUALITY_UHD:
                if current_quality == consts.QUALITY_SD:
                    print("Move up")
                    press(context, keys.KEY_UP)
                elif current_quality == consts.QUALITY_HDX:
                    print("Move up")
                    press(context, keys.KEY_UP)
                else:
                    assert (current_quality == consts.QUALITY_UHD)
                    return
            current_quality = get_current_rental_quality(context)
            print("current quality: {}".format(current_quality))
            if current_quality == quality:
                return
        assert (current_quality == quality)


def get_current_rental_quality(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    frame = cv2.imread(context.frame)
    uhd_sym_match = is_uhd_visible(context, frame)
    hdx_sym_match = is_hdx_visible(context, frame)
    sd_sym_match = is_sd_visible(context, frame)
    uhd_set = hdx_set = sd_set = set()
    if uhd_sym_match is not None and uhd_sym_match[0] is True:
        uhd_set = set(range(uhd_sym_match[1].y, uhd_sym_match[1].bottom))
    if hdx_sym_match is not None and hdx_sym_match[0] is True:
        hdx_set = set(range(hdx_sym_match[1].y, hdx_sym_match[1].bottom))
    if sd_sym_match is not None and sd_sym_match[0] is True:
        sd_set = set(range(sd_sym_match[1].y, sd_sym_match[1].bottom))

    current_quality_match = match(frame, PURCHASE_POPUP_PRICE_20X36, region=REGION_PURCHASE_POPUP_GRID_PRICE)
    assert current_quality_match[0], "fail to find current purchase"
    curent_quality_set = set(range(current_quality_match[1].y, current_quality_match[1].bottom))

    if len(list(curent_quality_set & uhd_set)) > 0:
        current_quality = consts.QUALITY_UHD
    elif len(list(curent_quality_set & hdx_set)) > 0:
        current_quality = consts.QUALITY_HDX
    elif len(list(curent_quality_set & sd_set)) > 0:
        current_quality = consts.QUALITY_SD
    else:
        assert False, "=== cannot find selected quality ==="
    return current_quality


def select_rent_button(context, quality=consts.QUALITY_HDX):
        """
        Arrow right to move to Rent button. The button orders are: Rent -> Own -> Disc
        :return: new page
        """

        if is_single_purchase_price_rent_visible(context):
            navigate_to_single_price_grid_rent(context, quality)
        else:
            navigate_to_rent_own_button(context, quality)
        press(context, keys.KEY_SELECT, 3)
        # show confirm purchase popup

def check_cancel_button_visible(context):
        cam = context.cam
        context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
        assert 200 == cam.get_frame(path=context.frame)
        frame = cv2.imread(context.frame)
        return match(frame, MOVIE_PURCHASE_POPUP_CANCEL_BUTTON)

def navigate_to_cancel_button(context):

        for _ in range(3):
            press(context, keys.KEY_DOWN, 1)
            if check_cancel_button_visible(context):
                return
        AssertionError("Failed to navigate to cancel button.")


def check_orange_price_tag(self):
    # check orange price on purchase pop up page.
    if self.check_discount_price():
        print("Find orange price tag")
        return True
    else:
        # This is the case, the current select is the only once price. Move to cancel button so that we can check
        # the price
        print("Need to navigate to Cancel button first to check orange price tag.")
        self.navigate_to_cancel_button()
        if self.check_discount_price():
            print("Need to move up back")
            press(context, keys.KEY_DOWN, 1)
            press(context, keys.KEY_UP)
            return True
    return False



@step('I can detect the title on the purchase page')
def step_impl(context):
    # cam = context.cam
    # context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    # assert 200 == cam.get_frame(path=context.frame)
    # frame = cv2.imread(context.frame)
    assert visible(context), " no purchase page found"
    # purchase_title = title(context, frame)
    # debug(f"purchase popup title: {purchase_title}")
    # assert fuzzy_match("Rent / Buy", purchase_title, 0.9), f"purchase title {purchase_title} is not found"
    # movie_title = purchase_popup_movie_title(context,frame)
    # debug(f"purchase popup title: {movie_title}")
    # if fuzzy_match(context.movie_title, movie_title, 0.8) is False:
    #     debug(f"movie title {movie_title} does not match {context.movie_title}")


@step('I can detect the confirm purchase popup')
def step_impl(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    frame = cv2.imread(context.frame)
    confirm_purchase_title = confirm_purchase_popup_title(context,frame)
    debug(f"confirm purchase popup title: {confirm_purchase_title}")
    assert fuzzy_match("Confirm Purchase", confirm_purchase_title, 0.9) or \
        fuzzy_match("Confirm Rental", confirm_purchase_title, 0.9), f"Confirm purchase popup title {confirm_purchase_title} is not found "


@step('I rent the "{video_quality}" on the purchase page')
def step_impl(context, video_quality):
    select_rent_button(context, video_quality)
    # press(context, keys.KEY_SELECT, 3)


@step('I buy the "{video_quality}" on the purchase page')
def step_impl(context, video_quality):
    select_own_button(context, video_quality)
    # press(context, keys.KEY_SELECT, 3)


@step('I can detect the thank you purchase popup')
def step_impl(context):
    cam = context.cam
    context.frame = get_frame_name(context, f"{WORK_DIR}/_frame.png")
    assert 200 == cam.get_frame(path=context.frame)
    frame = cv2.imread(context.frame)
    thank_you_purchase_title = thank_you_purchase_popup_title(context,frame)
    debug(f"thank you purchase popup title: {thank_you_purchase_title}")
    assert fuzzy_match("Thank You", thank_you_purchase_title, 0.9), f"thank you purchase popup title {thank_you_purchase_title} is not found"


@step('I select watch now on the thank you purchase popup')
def step_impl(context):
    press(context, keys.KEY_SELECT, 3)


@step('I select watch later on the thank you purchase popup')
def step_impl(context):
    press(context, keys.KEY_DOWN, 1)
    press(context, keys.KEY_SELECT, 3)


@step('I select "{button}" on the confirm purchase popup')
def step_impl(context, button):
    if button == "ok":
        press(context, keys.KEY_SELECT, 3)
    else:
        press(context, keys.KEY_RIGHT, 3)
        press(context, keys.KEY_SELECT, 3)
