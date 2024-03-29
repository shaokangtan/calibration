# this the python bindings for camera server support
# the API calls camera server REST API
import requests
# response = requests.get('https://google.com/')
# print(f"google response: {response}")
from lib.util import debug


class Camera():
    def __init__(self, url=None):
        self.session_cookie = None
        self.init = False
        self.url = None
        if url is not None:
            self.allocate_camera(url)

    def allocate_camera(self, url):
        debug(f"=== init_camera ===")
        r = self.ping(url)
        if r == 200:
            self.init = True
            self.url = url
        return r

    def free_camera(self):
        debug(f"=== free_camera ===")
        if self.init is True:
            self.init = False
            self.url = None
        return 200

    def ping(self, url):
        debug(f"=== ping ===")
        r = requests.get(url=f'{url}/', cookies=self.session_cookie)
        if r.status_code == 200:
            debug(f"cookies:{r.cookies}")
            if 'session' in r.cookies:
                self.session_cookie = {'session': r.cookies['session']}
        # if r.status_code == 200:
            # with open(path, 'wb') as f:
            #     for chunk in r.iter_content(1024):
            #         f.write(chunk)
        return r.status_code

    def start_live(self, address, timestamp=False, frame_rate=30):
        debug(f"=== start_live ===")
        if self.init is False:
            return 404
        r = requests.get(url=f'{self.url}/start_live/{address}/{ 1 if timestamp is True else 0 }/{frame_rate}', cookies=self.session_cookie)
        # if r.status_code == 200:
        # with open(path, 'wb') as f:
        #     for chunk in r.iter_content(1024):
        #         f.write(chunk)
        return r.status_code

    def stop_live(self):
        debug(f"=== stop_live ===")
        if self.init is False:
            return 404
        r = requests.get(url=f'{self.url}/stop_live', cookies=self.session_cookie)
        # if r.status_code == 200:
        # with open(path, 'wb') as f:
        #     for chunk in r.iter_content(1024):
        #         f.write(chunk)
        return r.status_code

    def _frame(self, path=None):
        # example to read file
        # https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
        debug(f"=== _frame ===")
        if self.init is False:
            return 404
        r = requests.get(url=f'{self.url}/_frame', cookies=self.session_cookie)
        if r.status_code == 200:
            if path is not None:
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        return r.status_code

    def get_frame(self, path=None):
        debug(f"=== get_frame {path} ===")
        if self.init is False:
            return 404
        r = requests.get(url=f'{self.url}/get_frame', cookies=self.session_cookie)
        if r.status_code == 200:
            if path is not None:
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        return r.status_code

#
# debug(f"=== test match ===")
# data = open('./images/test/playerBack.png', 'rb').read()
# response = requests.post(url = 'http://localhost:5000/match', data=data,
#                          headers={'Content-Type': 'application/octet-stream', 'Region': '0,0,1280,1080'})
# # let's check if what we sent is what we intended to send...
# import json
# import base64
# assert base64.b64decode(res.json()['data'][len('data:application/octet-stream;base64,'):]) == data


# example to receive data from server
# https://answers.splunk.com/answers/306952/return-binary-data-such-as-images-via-rest-api-or.html

# curl examples
# https://www.keycdn.com/support/popular-curl-examples


if __name__ == "__main__":

    import os

    if not os.path.exists('output'):
        os.makedirs('output')
    # URL = 'http://localhost:5000'
    URL = 'http://0.0.0.0:33'
    cam = Camera()
    status = cam.allocate_camera(URL)
    debug(f"response: {status}")

    status = cam._frame(path='output/_frame.png')
    debug(f"response: {status}")
    assert 200 == status

    status = cam.get_frame(path='output/new_frame.png')
    debug(f"response: {status}")
    assert 200 == status

    status = cam.start_live('127.0.0.1:12345')
    debug(f"response: {status}")
    assert 200 == status

    status = cam.stop_live()
    debug(f"response: {status}")
    assert 200 == status

    status = cam.free_camera()
    debug(f"response: {status}")
    assert 200 == status

    # status, ret = match('./images/test/playerBack.png')
    # status, ret = ocr([0,0,320,320])
