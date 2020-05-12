import camera_lib
import time
import socket
import subprocess
from helper import debug

if __name__ == "__main__":
   # URL is your camera URL including port
   # #URL = 'http://localhost:33'
   URL = 'http://0.0.0.0:33'
   # status = get_frame(URL, path = 'output/get_frame.png')
   cam = camera_lib.Camera()
   assert  200 == cam.allocate_camera(URL), "alloc camera fail"
   assert  200 == cam._frame(path = 'output/_frame.png')
   assert  200 ==  cam._frame(path = 'output/_frame.png')
   hostname = socket.gethostname()
   IPAddr = socket.gethostbyname(hostname)
   debug(f"=== start ffplay ===")
   ffplay = 'ffplay udp://' + IPAddr + ':33'
   process = subprocess.Popen(ffplay, shell=True)
   debug(f"=== subprocess.Popen return {process.pid} ===")
   time.sleep(5)

   debug(f"=== start live ===")
   assert  200 ==  cam.start_live(address=IPAddr + ':33',timestamp=True)
   # get new frame while video is live
   assert  200 ==  cam.get_frame(path = 'output/get_frame.png')

   time.sleep(10)
   debug(f"=== stop ffplay  ===")

   process.terminate()
   debug(f"=== start ffplay again (to deplete the buffer)===")
   ffplay = 'ffplay udp://' + IPAddr + ':33'
   process = subprocess.Popen(ffplay, shell=True)
   debug(f"=== subprocess.Popen return {process.pid} ===")

   time.sleep(30)
   process.terminate()
   assert  200 == cam.stop_live()
   # start = time.time()
   # for i in range(10):
   #     assert  200 ==  cam.get_frame(path=f'output/_frame-{i}.png')
   # debug (f"{(time.time()-start)/10} sec. per frame")
   status = cam.free_camera()
