from lib.vudu_image import match, ocr, Region, image_diff
from lib.helper import debug
from lib import keys
from features.steps.roku_steps import press
import time
import cv2

@step('I navigate to movie poster on the movie page')
def step_impl(context):
    press(context, keys.KEY_DOWN) # submenu
    press(context, keys.KEY_DOWN)




@step('I select a movie poster on the movie page')
def step_impl(context):
    # press(context, keys.KEY_RIGHT)
    press(context, keys.KEY_SELECT)


@step('I read movie title on the movie page')
def step_impl(context):
    pass


@step('I read movie info on the movie page')
def step_impl(context):
    pass
