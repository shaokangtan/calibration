import camera_lib
import time
if __name__ == "__main__":
   #URL = 'http://localhost:33'
   URL = 'http://0.0.0.0:33'
   # status = get_frame(URL, path = 'output/get_frame.png')
   cam = camera_lib.Camera()
   status = cam.init_camera(URL)
   status = cam._frame(URL, path = 'output/_frame.png')
   status = cam._frame(URL, path = 'output/_frame.png')
   status = cam.start_live(URL, address = '0.0.0.0:33')
   time.sleep(5)
   status = cam.stop_live(URL)
   status = cam.start_live(URL, address='0.0.0.0:33')
   time.sleep(5)
   status = cam.stop_live(URL)
   exit()
   start = time.time()
   for i in range(10):
       status = cam.get_frame(URL, path=f'output/_frame-{i}.png')
   print (f"{(time.time()-start)/10} sec. per frame")
