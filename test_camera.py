from camera_lib import _frame, get_frame

if __name__ == "__main__":
   #URL = 'http://localhost:33'
   URL = 'http://0.0.0.0:33'
   status = get_frame(URL, path = 'output/_frame.png')
   status = _frame(URL, path = 'output/new_frame.png')
   for i in range(100):
       status = get_frame(URL, path=f'output/_frame-{i}.png')

