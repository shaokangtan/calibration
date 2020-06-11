from behave import step
import requests
import xml.etree.ElementTree as ET
import time
from lib import keys
from lib.vudu_image import set_default_match_paramter
DEFAULT_MATCH_PARAMETER=(-1, 0.80, 25.0, 50.0)
MATCH_PARAMETER=(3, 0.70, 50.0, 200.0)


@step('I have a Roku "{roku_url}" with "{vudu}" app installed')
def step_impl(context, roku_url, vudu):
    url = 'http://' + roku_url
    #curl http://192.168.8.32:8060/query/apps
    cmd = url + "/query/apps"
    r = requests.get(cmd)
    print(f"Roku: get {cmd}, response: {r.status_code}")
    assert 200 == r.status_code
    # print(f"response:{r.text}")
    context.url=url
    # find vudu app
    root = ET.fromstring(r.text)
    for child in root:
        print(child.tag, child.attrib)
        if vudu == child.text:
            context.vudu_app_id = child.attrib['id']
            print(f"Roku: {vudu} app id:{context.vudu_app_id}\n\n")
            return
    assert False, "fail to find {vudu} on Roku"


@step('I select Roku home button')
def step_impl(context):
    goto_roku_home(context)


@step('I launch Vudu apps')
def step_impl(context):
    launch_vudu(context)

def launch_vudu(context):
    cmd = context.url + "/launch/" + context.vudu_app_id
    r = requests.post(cmd)
    print(f"Roku: post {cmd}, response: {r.status_code}\n\n")
    assert 200 == r.status_code or 204 == r.status_code
    time.sleep(5)
    set_default_match_paramter(MATCH_PARAMETER)


roku_keys = { keys.KEY_HOME:"Home",
  keys.KEY_REWIND:"Rev",
  keys.KEY_FASTFORWARD:"Fwd",
  keys.KEY_PLAYPAUSE:"Play",
  keys.KEY_SELECT:"Select",
  keys.KEY_LEFT:"Left",
  keys.KEY_RIGHT:"Right",
  keys.KEY_DOWN:"Down",
  keys.KEY_UP:"Up",
  keys.KEY_BACK:"Back",
  keys.KEY_AGAIN:"InstantReplay",
  keys.KEY_INFO:"Info",
  # keys.KEY_BACK:"Backspace",
  keys.KEY_SEARCH:"Search",
  keys.KEY_ENTER:"Enter" }


@step('I select "{key}" button')
def step_impl(context, key):
    press(context, key)


@step('I go to home page')
def step_impl(context):
    press(context, keys.KEY_REWIND)


def press(context, key, delay=3):
    assert key in roku_keys, f"error: {key} is not a valid key"
    cmd = context.url + "/keypress/" + roku_keys[key]
    r = requests.post(cmd)
    print(f"Roku: get {cmd}, response: {r.status_code}, delay:{delay}")
    time.sleep(delay)


def goto_vudu_home(context):
    press(context, keys.KEY_REWIND)


def goto_roku_home(context):
    cmd = context.url + "/keypress/home"
    r = requests.post(cmd)
    print(f"Roku: get {cmd}, response: {r.status_code}")
    time.sleep(5)
