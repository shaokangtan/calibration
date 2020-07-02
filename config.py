# ea tester will has its own camera ip, roku ip, cv2 camera id.
# camera id and input device will be based on the camera server's platform. currently, we support Windows and Mac OS.
#CAMERA_IP = "192.168.8.152:33"
CAMERA_IP = "10.0.2.15:1027"
ROKU_IP = "192.168.8.201:8060"
#CV2_CAMERA_ID = 1
CV2_CAMERA_ID = 0
import platform

system = platform.system()
print(f"running on {system} platform")

if system == 'Windows':
    # Windows
    CAMERA_ID = "video=\"UHD Capture\""
    INPUT_DEVICE = "dshow"
elif system == 'Darwin':
    # Mac OS
    CAMERA_ID = "\"0:none\""
    INPUT_DEVICE = "avfoundation"
elif system == 'Linux':
    # Linux
    CAMERA_ID = "\"0:none\""
    INPUT_DEVICE = "avfoundation"
else:
    assert False, "platform not supported"
