import camera_lib
import time
import socket
import subprocess

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
   ffplay = 'ffplay udp://'+ IPAddr + ':33'
   process = subprocess.Popen(ffplay, shell=True)
   print (f"=== subprocess.Popen return {process.pid} ===")
   assert  200 ==  cam.start_live(address = IPAddr + ':33')
   time.sleep(10)
   process.terminate()
   assert  200 ==  cam.stop_live()
   time.sleep(5)
   ffplay = 'ffplay udp://' + IPAddr + ':33'
   process = subprocess.Popen(ffplay, shell=True)
   print(f"=== subprocess.Popen return {process.pid} ===")
   assert  200 ==  cam.start_live(address = IPAddr + ':33')
   time.sleep(10)
   assert  200 == cam.stop_live()
   start = time.time()
   for i in range(10):
       assert  200 ==  cam.get_frame(path=f'output/_frame-{i}.png')
   print (f"{(time.time()-start)/10} sec. per frame")
   status = cam.free_camera()
