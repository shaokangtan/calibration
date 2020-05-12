import cv2
# pip install opencv-python-headless
# from goprocam import GoProCamera, constants
# comment out goprocam, we are reading GoPro from HDMI to USB directly.
# pip install flask
# pip install flask_extension
# pip install Flask_Session
# pip install Werkzeug == 0.15
# brew install ffmpeg ffmpeg --with-freetype
import os
import signal
import subprocess
from flask import Flask, session, make_response
from flask_session import Session
import config
from helper import debug


app = Flask(__name__)
print(f"__name__={__name__}")


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World -Universal capture platform!"



# curl --request get http://localhost:5000/start_live
# broadcast video to address
# address = ip:port e.g. 192.168.8.3:12345
# TBD: Add parameters to control w, h and rate
@app.route('/start_live/<address>/<timestamp>/<frame_rate>')
def start_live(address, timestamp, frame_rate):
    debug(f"=== rest api:get_live at {address}, timestamp: {timestamp} ===")
    if eval(timestamp) == 1:
        ffmpeg = "ffmpeg -f {device} -framerate 30 -video_size 1280x720 -i '{camera}:none' -vcodec libx264 " \
                 "-preset ultrafast -tune zerolatency -pix_fmt yuv422p " \
                 "-vf drawtext=\"fontfile=/System/Library/Fonts/NewYork.ttf: text=\"{text}\": fontcolor=white: fontsize=36: x=(w-text_w)/2: y=(h-text_h)/2\" " \
                 "-r {rate} -f mpegts udp://{addr}".format(device= config.INPUT_DEVICE, camera=config.CAMERA_ID, text="%\{gmtime\}", rate=frame_rate, addr=address)
    else:
        ffmpeg = "ffmpeg -f {device} -framerate 30 -video_size 1280x720 -i '{camera}:none' -vcodec libx264 " \
                 "-preset ultrafast -tune zerolatency -pix_fmt yuv422p " \
                 "-r {rate} -f mpegts udp://{addr}".format(device=config.INPUT_DEVICE, camera=config.CAMERA_ID, rate=frame_rate, addr=address)

        # ffmpeg -f avfoundation -framerate 30 -video_size 1280x720 -i "0:none" -vcodec libx264 -preset ultrafast
    #        -tune zerolatency -pix_fmt yuv422p -f mpegts udp://192.168.8.3:12345
    # return_code = subprocess.run([ffmpeg], shell=True)
    # debug(f"=== subprocess.run return {return_code} ===")
    debug(f"{ffmpeg}")
    process = subprocess.Popen(ffmpeg, shell=True)
    debug(f"=== subprocess.Popen return {process.pid} ===")
    session["ffmpeg_process"] = process.pid
    debug(f"process: {process.pid}")
    debug(f"process: {session['ffmpeg_process']}")
    return "success"


@app.route('/stop_live')
def stop_live():
    debug(f"=== rest api:stop_live ===")
    if 'ffmpeg_process' not in session:
        return "success"
    debug(f"kill process: {session['ffmpeg_process']}")
    # os.killpg(os.getpgid(session['ffmpeg_process']), signal.SIGTERM)
    # os.killpg(session['ffmpeg_process'], signal.SIGTERM)
    os.kill(session['ffmpeg_process'], signal.SIGTERM)
    return "success"


# curl --request get http://localhost:5000/get_frame
# capture new frame
@app.route('/get_frame')
def get_frame():
    debug("=== rest api:get_frame ===")
    CAMERA_ID = 0

    cap = cv2.VideoCapture(int(CAMERA_ID))
    ret, _frame = cap.read()
    session['frame'] = _frame
    cap.release()
    retval, buffer = cv2.imencode('.png', _frame)
    response = make_response(buffer.tobytes())
    response.headers.set('Content-Type', 'image/png')
    # response.headers.set(
    #     'Content-Disposition', 'attachment', filename='_frame.png')
    debug(f"return response ===")
    return response
    # return "success"


# curl --request get http://localhost:5000/_frame
# return current frame
@app.route('/_frame')
def _frame():
    debug("=== rest_api:_frame ===")
    # debug(f"session: {session}")
    # debug(f"session type: {type(session)}")
    # if 'test' not in session:
    #     session['test'] = 1
    #     debug(f"set session[test]={session['test']}")
    # else:
    #     debug(f"get session[test]={session['test']}")
    # return "success"
    if 'frame' not in session:
        debug(f"no frame found in seesion")
        return get_frame()
    # put _frame in response
    debug(f"put current _frame to response ===")

    retval, buffer = cv2.imencode('.png', session['frame'])
    response = make_response(buffer.tobytes())
    response.headers.set('Content-Type', 'image/png')
    #
    debug(f"return response ===")
    return response
    # return "success"

# curl --request get http://localhost:5000/ocr
# return text using provided region params
# param: new_frame, region
@app.route('/ocr')
def ocr():
    debug("=== rest_api:ocr ===")
    return "success"

# curl post http://localhost:5000/match
# return image match result, including found location using image, region, method param
# param: new_frame, region, threshold, method
@app.route('/match')
def match():
    debug("=== rest_api:match ===")
    return "success"

# curl --request get http://localhost:5000/detect_video_motion
# return True if video is detected
@app.route('/detect_video_motion')
def detect_video_motion():
    debug("=== rest_api:detect_video_motion ===")
    return "success"

# curl --request get http://localhost:5000/detect_audio_motion
# return True if audio is detected
@app.route('/detect_audio_motion')
def detect_audio_motion():
    debug("=== rest_api:detect_audio_motion ===")
    return "success"

# curl --request post http://localhost:5000/navigate
# navigate key(s). [ {"key": "KEY_DOWN", "WAIT_SEC": "3"}, {}, .... ]
@app.route('/navigate')
def navigate():
    debug("=== rest_api:navigate ===")
    return "success"


sess = Session()

print("start routes")
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

sess.init_app(app)


app.debug = True
print("start app")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port="33")
