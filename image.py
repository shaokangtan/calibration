# install color math:
# sudo pip install colormath
# reference, credits and acknolegement 
# https://en.wikipedia.org/wiki/CIE_1931_color_space
# http://hanzratech.in/2015/01/16/color-difference-between-2-colors-using-python.html
# transformation
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_geometric_transformations/py_geometric_transformations.html#affine-transformation
# https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
import cv2
import imutils
import numpy as np


from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# compare the difference of two colors
# return a list of four floats,
# 1.  distance of two color in color spectrum space.
# 2.  difference of r - cutoff
# 3.  difference of g - cutoff
# 4.  difference of b - cutoff
def compare_rgb(rgb1, rgb2):
    color1_rgb = sRGBColor(rgb1[0]/255, rgb1[1]/255, rgb1[2]/255);
    color2_rgb = sRGBColor(rgb2[0]/255, rgb2[1]/255, rgb2[2]/255);

    # Convert from RGB to Lab Color Space
    color1_lab = convert_color(color1_rgb, LabColor);

    # Convert from RGB to Lab Color Space
    color2_lab = convert_color(color2_rgb, LabColor);

    # Find the color difference
    delta_e = delta_e_cie2000(color1_lab, color2_lab);
    m1 = min(rgb1) # cutoff is the min of three
    m2 = min(rgb2)
    delta_r = abs((rgb1[0]-m1) - (rgb2[0]-m2))
    delta_g = abs((rgb1[1]-m1) - (rgb2[1]-m2))
    delta_b = abs((rgb1[2]-m1) - (rgb2[2]-m2))
    return (delta_e, delta_r, delta_g, delta_b)

def search_corners(frame):
    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (15, 15), 0)
    # blur = cv2.GaussianBlur(gray, (1, 1), 1000)
    edged = cv2.Canny(gray, 75, 200)

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    cnts = cnts[1] if imutils.is_cv2() else cnts[0]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    # loop over the contours
    screenCnt = None
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximated contour has four points, then we
        # can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break
    if screenCnt is None:
        print(f"search anchors fail")
        return None, None, None, None, None, None, screenCnt
    else:
        print(f"search anchors found: {approx}")
        # update edit box
        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        pts = [screenCnt[0][0], screenCnt[1][0], screenCnt[2][0], screenCnt[3][0]]
        s = np.sum(pts, axis=1)
        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        
        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis=1)
        tr = pts[np.argmin(diff)]
        bl = pts[np.argmax(diff)]
        # diff = list()
        # for c in screenCnt:
        #     diff.append(abs (c[0][0] - c[0][1]))
        # tr = (screenCnt[np.argmin(diff)][0][0], screenCnt[np.argmin(diff)][0][1])
        # bl = (screenCnt[np.argmax(diff)][0][0], screenCnt[np.argmax(diff)][0][1])

        # compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        # compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        # now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a "birds eye view",
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left
        # order
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        return tl,tr,bl,br,maxWidth,maxHeight

if __name__ == "__main__":

    for c in range(255):
        color1 = (128,128,128)
        color2 = (c,c,c)
        delta = compare_rgb(color1, color2)
        print(f"color {color1}, {color2} = {delta}")


    delta = compare_rgb((255,0,0),(0,0,255))
    print ("The difference between the 2 color = ", delta)
