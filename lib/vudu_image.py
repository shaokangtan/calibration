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
import pytesseract
from cv2 import imwrite, cvtColor, COLOR_BGR2GRAY

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


# compare the difference of two colors
# return a list of four floats,
# 1.  distance of two color in color spectrum space.
# 2.  difference of r1,r2 - cutoff
# 3.  difference of g1, g2 - cutoff
# 4.  difference of b1, b2 - cutoff
# cutoff = min(r,g,b)
def comp_rgb(rgb1, rgb2):
    space_diff = comp_color_distance(rgb1, rgb2)
    m1 = min(rgb1)  # cutoff is the min of three
    m2 = min(rgb2)
    delta_r = abs((rgb1[0] - m1) - (rgb2[0] - m2))
    delta_g = abs((rgb1[1] - m1) - (rgb2[1] - m2))
    delta_b = abs((rgb1[2] - m1) - (rgb2[2] - m2))
    return space_diff, delta_r, delta_g, delta_b


def comp_color_distance(rgb1, rgb2):
    color1_rgb = sRGBColor(rgb1[0] / 255, rgb1[1] / 255, rgb1[2] / 255)
    color2_rgb = sRGBColor(rgb2[0] / 255, rgb2[1] / 255, rgb2[2] / 255)

    # Convert from RGB to Lab Color Space
    color1_lab = convert_color(color1_rgb, LabColor)

    # Convert from RGB to Lab Color Space
    color2_lab = convert_color(color2_rgb, LabColor)
    return delta_e_cie2000(color1_lab, color2_lab)

default_match_parameter =(-1, 0.80, 25.0, 50.0)

def set_default_match_paramter(match_paramter):
    global default_match_parameter
    default_match_parameter = match_paramter

def get_default_match_parameter():
    return default_match_parameter


# MATCH_PARAMETER=(method, template_threshold, color distance_threhold, rgb_threshold)
# method: -1 auto, others cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED
# return (match, region, template difference, (color space delta, R delta, G delta, B delta))
# match: True if found, False if not found
# region: the location of found match. x, y, w and h
def match(frame, image, region=None, match_parameter=None):
    if match_parameter is None:
        match_parameter=get_default_match_parameter()

    if type(frame) is str:
        print(f"match source: {frame}, ", end="")
        frame = cv2.imread(frame)
    if type(image) is str:
        print(f"match target: {image}, ", end="")
        image = cv2.imread(image)
    print(f"match region: {region}, match param: {match_parameter}")
    h, w, d = image.shape[::]
    if region is None:
        search_region = (0, 0, frame.shape[0], frame.shape[1])
    else:
        search_region = (region.y, region.x, region.bottom, region.right)  # swap w, h
    if search_region[2] - search_region[0] < h or search_region[3] - search_region[1] < w:
        # self.console.write(f"error: search region < template size")
        print(f"error: search region{region} < template size {w} * {h}")
        return None

    if match_parameter[0] == -1:
        methods = [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED]
    else:
        methods = [match_parameter[0]]
    for method in methods:
        # Apply template Matching
        res = cv2.matchTemplate(cvtColor(frame[search_region[0]:search_region[2], search_region[1]:search_region[3]],
                                         COLOR_BGR2GRAY), cvtColor(image, COLOR_BGR2GRAY), method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        '''
        # get all the matches:
        res2 = np.reshape(res, res.shape[0] * res.shape[1])
        sort = np.argsort(res2)
        (y1, x1) = np.unravel_index(sort[0], res.shape)  # best match
        (y2, x2) = np.unravel_index(sort[1], res.shape)  # second best match
        '''

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
            val = min_val
            if max_val == min_val:
                result = 0.0
            else:
                result = 1.0 - val / max_val  # - min_val)
        else:
            top_left = max_loc
            val = max_val
            if max_val == min_val:
                result = 0.0
            elif method in [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR]:
                if min_val > 0:
                    result = val / max_val
                else:
                    result = val / (max_val - min_val)
            else:
                result = val
        top_left = (top_left[0] + search_region[1], top_left[1] + search_region[0])
        bottom_right = (top_left[0] + w, top_left[1] + h)
        (startX, startY) = top_left
        (endX, endY) = bottom_right

        b = int(np.average(frame[startY:endY, startX:endX, 0]))
        g = int(np.average(frame[startY:endY, startX:endX, 1]))
        r = int(np.average(frame[startY:endY, startX:endX, 2]))
        print(f"method: {method}, frame color avg RGB: {r}, {g}, {b}, ", end="")

        b1 = int(np.average(image[:, :, 0]))
        g1 = int(np.average(image[:, :, 1]))
        r1 = int(np.average(image[:, :, 2]))

        # self.console.write(f"color avg RGB: {r}, {g}, {b}\n")
        print(f"image color avg RGB: {r1}, {g1}, {b1}")
        delta = comp_rgb((r, g, b), (r1, g1, b1))

        if result < match_parameter[1]:
            print(f"no template found!!!. result {result:.2f} at {top_left}, {bottom_right} < threshold {match_parameter[1]} ({min_val:.2f}, "
                  f"{max_val:.2f}) in region: {region}")
        elif delta[0] > match_parameter[2]:
            print(f"detect at {top_left}, {bottom_right}, val: {val:.2f}({min_val:.2f}, {max_val:.2f}), "
                  f"result: {result:.2f}\n")
            print(f"template found but color doesnt match???. color space diff {delta[0]:.2f} > {match_parameter[2]}")
        elif sum(delta[1:]) > match_parameter[3]:
            print(f"detect at {top_left}, {bottom_right}, val: {val:.2f}({min_val:.2f}, {max_val:.2f}), "
                  f"result: {result:.2f}\n")
            print(f"template found but color doesnt match???. color rgb diff {delta[1:]} > {match_parameter[3]}")
        else:
            print(
                f"found template result: {result:.2f} at {top_left}, {bottom_right}, val: {val:.2f}({min_val:.2f}, {max_val:.2f}) in region: {region}")
            return (True, Region(*top_left, *bottom_right), result, delta, method)

        if len(methods) > 1:
            print(f"try different method again")

    return (False, Region(*top_left, *bottom_right), result, delta, method)


# search_corners
# search the corners of the skewed image.
# the function find the largest contour and return the image's corners and width and height of the fixed image.
# inputs -
# frame: skewed image in BGR format
# threshold: valid vaule is in the range of 0 to 255
# When a  color  < threshold, it is assigned as black, when color > then threshold is assigned as white
# return -
# top_left, top_right, bottom_left, bottom_right, deskewed width, deskewed height
def search_corners(frame, threshold=10):
    # convert the image to grayscale, blur it, and find edges
    # in the image
    blur = cv2.pyrMeanShiftFiltering(frame, 21, 51)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    # gray = cv2.GaussianBlur(gray, (15, 15), 0)
    # blur = cv2.GaussianBlur(gray, (1, 1), 1000)
    # edged = cv2.Canny(gray, 75, 200)
    ret, threshold = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    # cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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
        return None, None, None, None, None, None
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
        return tl, tr, bl, br, maxWidth, maxHeight

def init_deskew(pts1, pts2):
    M = cv2.getPerspectiveTransform(pts1, pts2)
    return (M, pts2[3])


def run_deskew(frame, perspective_transform_info):
    return cv2.warpPerspective(frame, perspective_transform_info[0], tuple(perspective_transform_info[1]))

# recognize text on the frame
# region defines the area to process OCR
# grayscale is True when you want to convert frame to grayscale before OCR
def ocr(frame, region=None, grayscale=False, invert_grayscale=False, ocr_parameter=None):
    if region is not None:
        _frame = frame[region.y:region.bottom, region.x:region.right]
    else:
        _frame = frame
    if grayscale is True:
        _frame = cvtColor(_frame, cv2.COLOR_BGR2GRAY)
        if invert_grayscale:
            _frame = 255-_frame[:,:]

    if ocr_parameter:
        text = pytesseract.image_to_string(_frame, config=ocr_parameter)
    else:
        text = pytesseract.image_to_string(_frame)
    print(f"ocr return {text} at region: {region if region is not None else 'all'}")
    return text

def image_diff(image1, image2):
    noise_threshold = 20
    frame1 = cvtColor(cv2.imread(image1), cv2.COLOR_BGR2GRAY)
    frame2 = cvtColor(cv2.imread(image2), cv2.COLOR_BGR2GRAY)
    if frame1.shape[0] != frame2.shape[0] or frame1.shape[1] != frame2.shape[1]:
        return 100
    frame3 = cv2.subtract(frame1, frame2)
    # a0 = np.sum(frame3, 0)
    # a1 = np.sum(a0,0)
    different_pixels = (frame3[:,:] > noise_threshold ).sum()
    return int(different_pixels / (frame1.shape[0] * frame1.shape[1]) * 100)


class Region():
    def __init__(self, x, y, right, bottom):
        self._x = x
        self._y = y
        self._right = right
        self._bottom = bottom


    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @property
    def top(self):
        return self._y

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

    @property
    def left(self):
        return self._x

    @property
    def w(self):
        return self._right - self._x

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    @property
    def h(self):
        return self._bottom - self._x

    @property
    def bottom(self):
        return self._bottom

    @bottom.setter
    def bottom (self, value):
        self._bottom = value

    def __str__(self):
        return f"{self.x}, {self.y}, {self.right}, {self.bottom}"

    @staticmethod
    def intersect(region1, region2):
        if region1.x <= region2.x and region2.x <= region1.right:
            if region1.y <= region2.y and region2.y <= region1.bottom:
                return True
            if region1.y <= region2.bottom and region2.bottom <= region1.bottom:
                return True
        if region2.x <= region1.x and region1.x <= region2.right:
            if region2.y <= region1.y and region2.y <= region2.bottom:
                return True
            if region2.y <= region1.bottom and region1.bottom <= region2.bottom:
                return True

        return False

    @staticmethod
    def intersect_area(region1, region2):
        #print(f"region 1: {region1.left}{region1.top}{region1.right}{region1.bottom}")
        #print(f"region2: {region1.left}{region1.top}{region1.right}{region1.bottom}")
        left = max(region1.left, region2.left)
        right = min(region1.right, region2.right)
        bottom = min(region1.bottom, region2.bottom)
        top = max(region1.top, region2.top)
        if left < right and bottom > top:
            return (right - left) * (bottom - top)
        else:
            return 0


if __name__ == "__main__":

    for c in range(255):
        color1 = (128, 128, 128)
        color2 = (c, c, c)
        delta = comp_rgb(color1, color2)
        print(f"color {color1}, {color2} = {delta}")

    delta = comp_rgb((255, 0, 0), (0, 0, 255))
    print("The difference between the 2 color = ", delta)
    assert abs( sum(delta[1::]) - 510 )< 3.0, "comp_rgb failed"

    delta = comp_color_distance((255, 0, 0), (0, 0, 255))
    print("The distance between the 2 color = ", delta)
    assert abs(delta - 52.0) < 3.0, "comp_color_distance failed"

    frame = cv2.imread("pages/Samsung/play_page_1.png")
    region = ( 20, 20, 292, 84 )
    result = ocr(frame, region)
    print("The ocr result = ", result)
    assert 'A Star Is Born' in result, "ocr failed"


