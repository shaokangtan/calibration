from behave import step
from lib import vudu_image, camera_lib
import time
import socket
import subprocess
import os
import cv2
from lib.helper import Region, debug


@step('I have a camera "{url}"')
def step_impl(context, url):
    url = 'http://' + url
    cam = camera_lib.Camera()
    assert 200 == cam.allocate_camera(url), "alloc camera fail"
    context.cam = cam
    context.frame_no = 0


@step('I save a frame as "{file}"')
def step_impl(context, file):
    cam = context.cam
    assert 200 == cam._frame(path=file)


@step('I can verify the frame "{file}" is valid')
def step_impl(context, file):
    print(f"verify file: {file}")
    # TBD: verify the photo
    if os.path.isfile(file):
        frame = cv2.imread(file)
        cv2.imshow('frame', frame)
        cv2.waitKey(10000)
        cv2.destroyAllWindows()
    else:
        assert False, f"cannot find {file}"


@step('I have an image "{image}"')
def step_impl(context, image):
    print(f"verify image file: {image}")
    if os.path.isfile(image):
        context.image = image
    else:
        assert False, f"cannot find file: {image}"


@step('I match "{template}" at "{region}"')
def step_impl(context, template, region):
    print(f"verify template file: {template}")
    if os.path.isfile(template):
        where = list(map(int, region.split(",")))
        # region = vudu_image.Region(where[0], where[1], where[2], where[3])
        region = Region(*where)
        print (f"match in region:{region}")
        match_result = vudu_image.match( cv2.imread(context.image), cv2.imread(template), region)
        context.match_result = match_result
    else:
        assert False, f"cannot find file: {template}"


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Returns true if  rectangles(l1, r1)
# is inside (l2, r2)
def doOverlap(region1, region2):
    # If one rectangle is on left side of other
    print(f"doOverlap {region1}, {region2}")
    print(f"doOverlap {type(region1)}, {type(region2)}")
    print(f"doOverlap {type(region1)}, {type(region2)}")

    if region1.x < region2.x or region1.right > region2.right:
        return False
    if region1.y < region2.y or region1.bottom > region2.bottom:
        return False

    return True


@step('I can find the "{template}" at "{location}"')
def step_impl(context, template, location):
    print(f"verify match: {template}")
    if context.match_result is not None:
        print(f"match result: {context.match_result}")
        assert context.match_result[0] is True, f"fail to match {template}"
        print(f"verify match location: {location}")
        region = Region(*list(map(int, location.split(","))))
        print(f"region={region}")
        assert doOverlap(context.match_result[1], region), f"match didnt find {template} in {location}"

    else:
        assert False, f"fail to match {template}"


@step('I OCR "{image}" at "{region}"')
def step_impl(context, image, region):
    print(f"ocr in region:{region}")
    where = list(map(int, region.split(",")))
    region = vudu_image.Region(where[0],where[1],where[2],where[3])
    match_result = vudu_image.ocr(cv2.imread(context.image), region)
    print(f"match_result: {match_result}")
    context.match_result = match_result


@step('I can find the text {text}')
def step_impl(context, text):
    assert context.match_result in text, "fail to ocr {text}"


@step('I start the video on port {port}')
def step_impl(context, port):
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    cam = context.cam
    assert 200 == cam.start_live(address=ip_addr + f':{port}')

@step('I can verify the video on port {port} is valid')
def step_impl(context, port):
    print("verify video on ffplay and wait for 30 seconds")
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    ffplay = 'ffplay udp://' + ip_addr + f':{port}'
    process = subprocess.Popen(ffplay, shell=True)
    print(f"=== subprocess.Popen return {process.pid} ===")
    time.sleep(30)
    process.terminate()



@step('I stop the video')
def step_impl(context):
    cam = context.cam
    assert 200 == cam.stop_live()


'''
# deeplinks
from catalyst.frameworks.behave.helpers import initialize_api_with_account

@step('I deeplink to "{movie_title}" movie details screen for account "{account}" on device "{device}"')
def step_impl(context, movie_title, account, device):
    api = initialize_api_with_account(context, account)
    light_device_id = get_light_device_id(api, context, device)
    message = get_client_message(ClientMessageType.SHOW_CONTENT_DETAILS,
                                 content_id=context.contents[movie_title]['content_id'])
    api.client_message_send(account_id=api.account_id, destination_light_device_id=light_device_id, message=message)


@step('I deeplink to search screen with text "{text}" for account "{account}" on device "{device}"')
def step_impl(context, text, account, device):
    api = initialize_api_with_account(context, account)
    light_device_id = get_light_device_id(api, context, device)
    message = get_client_message(ClientMessageType.SHOW_SEARCH_RESULTS, search_query=text)
    api.client_message_send(account_id=api.account_id, destination_light_device_id=light_device_id, message=message)


@step('I deeplink to play trailer with content "{content_id}" for account "{account}" on device "{device}"')
def step_impl(context, content_id, account, device):
    api = initialize_api_with_account(context, account)
    light_device_id = get_light_device_id(api, context, device)
    message = get_client_message(ClientMessageType.PLAY_TRAILER, content_id=content_id)
    api.client_message_send(account_id=api.account_id, destination_light_device_id=light_device_id, message=message)

'''
