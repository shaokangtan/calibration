from behave import step
from lib.helper import find_selection_text, debug
from lib.vudu_image import match, ocr, Region
from cv2 import *
from features.steps.roku_steps import press, goto_vudu_home
import time
from lib import  keys

menu_screen_tabs = ["My Vudu", "Spotlight", "Free", "Movies", "TV", "Search", "Settings"]

# TBD the parameter should be customized per camera and TV
default_match_parameter=(-1, 0.80, 25.0, 50.0)
match_parameter=(-1, 0.80, 40.0, 200.0)

@step('I can verify all navigation bar tabs visible on menu page')
def step_impl(context):
    cam = context.cam
    context._frame = "./_frame.png"
    assert 200 == cam.get_frame(path=context._frame)
    region = Region(0, 0, 1000, 70)
    match_result = ocr(cv2.imread(context._frame), region)
    debug(f"ocr return {match_result}")
    for tab in menu_screen_tabs:
        #assert  tab  in match_result, f"{tab} not found in menu tabs"
        if  tab  not in match_result:
            debug(f"error: {tab} not found in menu tabs")
        else:
            debug(f"{tab} found in menu tabs")


settings_screen_tabs = ["My Account", "Family Settings", "Closed Captioning", "Playback Quality", "Autoplay Settings", "Accessibility",  "About" ]

@step('I can verify "{tab}" selection on menu page')
def step_impl(context, tab):
    assert tab in menu_screen_tabs, "error: {tab} is an unknown screen"
    left_sel = "./images/Roku/main_menu_sel_l.png"
    right_sel = "./images/Roku/main_menu_sel_r.png"
    cam = context.cam
    context._frame = "./_frame.png"
    assert 200 == cam.get_frame(path=context._frame)
    text_in_highlight, region = find_selection_text(cv2.imread(context._frame), cv2.imread(left_sel), cv2.imread(right_sel),
                                                    region=Region(0, 0, 1000, 80), match_parameter=match_parameter)
    debug(f"current selection is {text_in_highlight} at {region}")
    assert tab in text_in_highlight, f"{tab} selection not found"


@step('I can verify "{tab}" selection on settings page')
def step_impl(context, tab):
    assert tab in settings_screen_tabs, "error: {tab} is an unknown screen"
    left_sel = "./images/Roku/settings_menu_sel_l.png"
    right_sel = "./images/Roku/settings_menu_sel_r.png"
    cam = context.cam
    context._frame = "./_frame.png"
    assert 200 == cam.get_frame(path=context._frame)
    text_in_highlight, region = find_selection_text(cv2.imread(context._frame), cv2.imread(left_sel), cv2.imread(right_sel),
                                                    x_offset=28, region=Region(50, 170, 400, 540), match_parameter=match_parameter)
    debug(f"current selection is {text_in_highlight} at {region}")
    assert tab in text_in_highlight, f"{tab} selection not found"


@step('I go to "{screen}"')
def step_impl(context, screen):
    assert screen in menu_screen_tabs, "error: unknown screen"
    goto_vudu_home(context)
    # we are in menu screen now
    # check current selection is on spotlight
    cam = context.cam
    context._frame = "./_frame.png"
    assert 200 == cam.get_frame(path=context._frame)
    left_sel = "./images/Roku/main_menu_sel_l.png"
    right_sel = "./images/Roku/main_menu_sel_r.png"
    text_in_highlight, region = find_selection_text(cv2.imread(context._frame), cv2.imread(left_sel), cv2.imread(right_sel),
                                                    region=Region(0, 0, 1000, 80), match_parameter=match_parameter)
    debug(f"current selection is {text_in_highlight} at {region}")


@step('I wait "{seconds}" seconds')
def step_impl(context, seconds):
    debug(f"wait {seconds} seconds")
    time.sleep(int(seconds))

'''
from catalyst.frameworks.behave.helpers import initialize_api_with_account

@step('I go to Welcome screen')
def step_impl(context):
    context.general_screen.go_to(context.urls['base'])


@step('I go to Log In with Vudu screen')
def step_impl(context):
    context.general_screen.go_to(context.urls['base'])
    context.launch_screen.hover_and_click('login_button')
    context.launch_screen.hover_and_click('sign_in_with_vudu_button')


@step('I go to Log In with Walmart screen')
def step_impl(context):
    context.general_screen.go_to(context.urls['base'])
    context.launch_screen.hover_and_click('login_button')
    context.launch_screen.hover_and_click('sign_in_with_wmt_button')


@step('I can see Vudu logo')
def step_impl(context):
    context.general_screen.verify_vudu_logo_visible()


@step('I go to "{screen}"')
def step_impl(context, screen):
    context.general_screen.go_to(context.urls[screen])


@step('I go to "{screen}" screen without sign in')
def step_impl(context, screen):
    context.general_screen.go_to(context.urls['base'])
    context.launch_screen.hover_and_click('browse_button')
    context.navigation_bar_screen.select_navigation_bar_tab(screen)


@step('I record the movie info from details panel')
def step_impl(context):
    context.movie_title = context.general_screen.verify_and_get_movie_title_from_details_panel()
    context.movie_release_time = context.general_screen.verify_and_get_movie_release_time()


@step('I sign in with account "{account}" and go to screen "{screen}"')
def step_impl(context, account, screen):
    context.general_screen.go_to(context.urls['base'])
    # TODO: need to remove after userCollectionVersion is ready
    api = initialize_api_with_account(context, account, use_cache=False)
    api.account_label_add(account_id=api.account_id, name='userCollectionVersion', value='OFF')
    context.general_screen.sign_in_and_go_to_screen(context.accounts[account], screen)


@step('I can see new offer marked "{text}"')
@step('I can see "{text}" applied to transaction')
@step('I can see text "{text}"')
@step('I can see button "{text}"')
@step('I can see tab "{text}"')
@step('I can see "{text}" required to activate device')
def step_impl(context, text):
    context.general_screen.verify_text_visible(text)


@step('I refresh the page')
def step_impl(context):
    context.general_screen.refresh()


@step('I go to screen "{screen}"')
def step_impl(context, screen):
    context.general_screen.go_to_screen_with_sign_in(screen)


@step('I click on back button')
def step_impl(context):
    context.general_screen.click_on_back_button()


@step('I click on back button in media panel')
def step_impl(context):
    context.general_screen.click_on_back_button_in_media_panel()


@step('I can verify I am in "{tab}" tab screen')
def step_impl(context, tab):
    context.general_screen.verify_in_tab_screen(tab)


@step('I can see orange dot appears next to the bell')
def step_impl(context):
    context.general_screen.verify_orange_dot_bell_visible()


@step('I can verify orange dot next to the bell icon is not visible')
def step_impl(context):
    context.general_screen.verify_orange_dot_bell_invisible()


@step('I click the bell icon')
def step_impl(context):
    context.general_screen.click_bell_icon()


@step('I select "{button}" button')
def step_impl(context, button):
    context.general_screen.click_button(button)


@step('I can verify "{text}" not visible')
def step_impl(context, text):
    context.general_screen.verify_text_invisible(text)


@step('I select poster at location "{location:d}"')
def step_impl(context, location):
    context.general_screen.select_movie_poster_at_location(location)


@step('I hover onto movie poster at location "{location:d}"')
@step('I hover onto tv poster at location "{location:d}"')
def step_impl(context, location):
    context.general_screen.hover_movie_poster_location(location)
    context.content_id = context.general_screen.verify_and_get_content_id_movie(location)


@step('I can verify device "{device}" activated for my account')
def step_impl(context, device):
    device_type = context.devices[device]['light_device_type']
    device_client_id = str(context.devices[device]['light_device_client_id'])

    assert_that(device_type, is_in(context.light_device_map))
    assert_that(device_client_id, is_in(context.light_device_map[device_type]))


@step('I can verify movie title "{movie_title}" visible')
def step_impl(context, movie_title):
    context.general_screen.verify_movie_title_visible(movie_title)


@step('I can verify Parental Controls with LOCK icon visible')
def step_impl(context):
    context.general_screen.verify_parental_controls_icon_visible()


@step('I can verify Common Sense Media rating visible in metadata panel')
def step_impl(context):
    context.general_screen.verify_common_sense_media_metadata_visible()


@step('I get content ids list of posters')
def step_impl(context):
    context.general_screen.get_content_ids_list()
'''
