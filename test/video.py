import cv2
import numpy as np
import time

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
# cap = cv2.VideoCapture('720.mov')
cap = cv2.VideoCapture('1080p.mov')
# cap = cv2.VideoCapture('720p.mp4')

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video stream or file")

# Read until video is completed
frames = 0
start = time.clock()
while (cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if ret == True:
        frames += 1
        # Display the resulting frame
        cv2.imshow('Frame', frame)

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    # Break the loop
    else:
        break

print(f"{frames/(time.clock()-start)} fp/s" )
# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()