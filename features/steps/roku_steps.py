from behave import step
import requests
import xml.etree.ElementTree as ET
import time
from lib import keys

@step('I have a Roku "{roku_url}" with "{vudu}" app installed')
def step_impl(context, roku_url, vudu):
    url = 'http://' + roku_url
    #curl http://192.168.8.32:8060/query/apps
    cmd = url + "/query/apps"
    print(f"get {cmd}")
    r = requests.get(cmd)
    # print(f"response:{r.text}")
    context.url=url
    # find vudu app
    root = ET.fromstring(r.text)
    for child in root:
        # print(child.tag, child.attrib)
        if 'VUDU' == child.text:
            print(f"appid={child.attrib['id']}")
            context.vudu_app_id = child.attrib['id']
            print(f"{vudu} app id:{context.vudu_app_id}")
            return


@step('I select Roku home button')
def step_impl(context):
    goto_roku_home(context)


@step('I launch Vudu apps')
def step_impl(context):
    cmd = context.url + "/launch/" + context.vudu_app_id
    print(f"get {cmd}")
    r = requests.post(cmd)
    print(r.status_code)
    time.sleep(10)


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


def press(context, key):
    assert key in roku_keys, "error: illegal key"
    cmd = context.url + "/keypress/" + roku_keys[key]
    print(f"get {cmd}")
    r = requests.post(cmd)
    print(r.status_code)
    time.sleep(3)


def goto_vudu_home(context):
    press(context, keys.KEY_REWIND)


def goto_roku_home(context):
    cmd = context.url + "/keypress/home"
    print(f"get {cmd}")
    r = requests.post(cmd)
    print(r.status_code)
    time.sleep(5)
