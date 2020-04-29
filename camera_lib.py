#this the python wrapper for camera support
#the API calls camera_server REST API
import requests
response = requests.get('https://google.com/')
print(f"google response: {response}")

def ping(url):
    print(f"=== get_live ===")
    r = requests.get(url=f'{url}/', stream=True)
    # if r.status_code == 200:
        # with open(path, 'wb') as f:
        #     for chunk in r.iter_content(1024):
        #         f.write(chunk)
    return r.status_code

def get_live(url, path):
    print(f"=== get_live ===")
    r = requests.get(url=f'{url}/_live', stream=True)
    # if r.status_code == 200:
        # with open(path, 'wb') as f:
        #     for chunk in r.iter_content(1024):
        #         f.write(chunk)
    return r.status_code


def _frame(url, path=None):
    # example to read file
    # https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
    print(f"=== _frame ===")
    r = requests.get(url=f'{url}/_frame', stream=True)
    if r.status_code == 200:
        if path is not None:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
    return r.status_code

def get_frame(url, path=None):
    print(f"=== get_frame ===")
    r = requests.get(url=f'{url}/get_frame', stream=True)
    if r.status_code == 200:
        if path is not None:
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
    return r.status_code

'''
def match(url, image_path, region=[0,0,1280,1080], method=None):
    print(f"=== match ===")
    data = open(image_path, 'rb').read()
    r = requests.post(url=f'{url}/match', data=data,
                             headers={'Content-Type': 'application/octet-stream',
                                      'Region': f'{region[0]},{region[1]},{region[2]},{region[3]}'})
    return r.status_code

def ocr(url, region=[0,0,1280,1080]):
    print(f"=== ocr ===")
    r = requests.post(url=f'{url}/ocr',
                      headers={'Region': f'{region[0]},{region[1]},{region[2]},{region[3]}'})
    ocr_result = ""
    if r.status_code == 200:
        for chunk in r.iter_content(1024):
            ocr_result = ocr_result + chunk
    return r.status_code, ocr_result

def detect_video_motion(url):
    print(f"=== detect_video_motion ===")
    r = requests.get(url=f'{url}/detect_video_motion', stream=True)
    motion_result = False
    if r.status_code == 200:
        motion_result = True
    return r.status_code, motion_result
'''
#
# print(f"=== test match ===")
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
   # URL = 'http://localhost:5000'
   URL = 'http://0.0.0.0:33'
   status = ping(URL)
   print(f"response: {status}")

   status = _frame(URL, path = '../output/_frame.png')
   print(f"response: {status}")

   status = get_frame(URL, path = '../output/new_frame.png')
   print(f"response: {status}")

   # status, ret = match(URL, './images/test/playerBack.png')
   # status, ret = ocr(URL,[0,0,320,320])

