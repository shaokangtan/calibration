from behave import step
from lib.vudu_image import match, ocr, Region, image_diff
from lib.helper import debug
from lib import keys
from features.steps.roku_steps import press
import time
import cv2

@step('I navigate to movie poster in the New This Month on the free page')
def step_impl(context):
    press(context, keys.KEY_DOWN,1) # submenu
    press(context, keys.KEY_DOWN,1) # Promo
    press(context, keys.KEY_DOWN,1) # Browse All Free Titles
    press(context, keys.KEY_DOWN,1) # New This Month
    #press(context, keys.KEY_RIGHT) # move next poster



@step('I select a movie poster on the free page')
def step_impl(context):
    press(context, keys.KEY_SELECT)


@step('I select the movie poster at "{no}" on the free page')
def step_impl(context, no):
    row = (int(no) - 1 ) // 5
    col = int(no) - row * 5 - 1
    for _ in range(row):
        press(context, keys.KEY_DOWN)
    for _ in range(col):
        press(context, keys.KEY_RIGHT)
    press(context, keys.KEY_SELECT)


@step('I save title on the detail page')
def step_impl(context):
    pass
