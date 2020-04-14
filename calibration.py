import sys
import cv2
import pyqtgraph as pg
import pyqtgraph.exporters
from numpy import asarray
from pyqtgraph.dockarea import *
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from  pyqtgraph.console import ConsoleWidget
import numpy as np
import imutils
from PIL import Image
import getopt
import glob
import ntpath
import pytesseract
import json


import time
from image import compare_rgb
VERSION = "0.0.1"

class MyImageItem(pg.ImageItem):
    def __init__(self, image,  console, **kwargs):
        super().__init__(image, **kwargs)
        self.console = console

    def mouseClickEvent(self, ev):
        super().mouseClickEvent(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            #print(f"mouse pos: {ev.pos()}")
            # self.console.write(f"mouse pos: {ev.pos()[0]:.2f}, {ev.pos()[1]:.2f}")
            self.console.write(f"mouse pos: {ev.pos()[0]:.0f}, {ev.pos()[1]:.0f}\n")

class CalibrationView(QMainWindow):
    def __init__(self, pages, templates, parent=None, title=None, verbose=False):
        super(QMainWindow, self).__init__(parent)
        if len(pages) == 0 or len(templates) == 0:
            print("error: no pages/templates loaded")
            return None
        self.videos = []
        self.pages = list(pages)
        self.templates = list(templates)
        self.DEF_COLOR_DISTANCE_THRESHOLD = "10.0"
        self.DEF_RGB_DIFFERENCE_THRESHOLD = "30"
        self.DEF_SCREEN_DIM = "1920,1080"
        self.blurring_types = ["Averaging", "Gaussian Filtering", "Median Filtering",  "Bilateral Filtering"]
        self.color_templates = ["images/color_calibration/blue_tall.png", "images/color_calibration/cyan_tall.png",
                                "images/color_calibration/green_tall.png", "images/color_calibration/purple_short.png",
                                "images/color_calibration/yellow_short.png", "images/color_calibration/blue_short.png",
                                "images/color_calibration/cyan_short.png", "images/color_calibration/gray_gradient.png",
                                "images/color_calibration/magenta_tall.png", "images/color_calibration/red_short.png",
                                "images/color_calibration/yellow_tall.png"]
        self.verbose = verbose
        self.area = DockArea()
        self.setCentralWidget(self.area)
        self.resize(1024, 900)
        self.setWindowTitle(title)
        self.start_streaming = False
        self.deskewed_frame = None

        ## Create docks, place them into the window one at a time.
        ## Note that size arguments are only a suggestion; docks will still have to
        ## fill the entire dock self.area and obey the limits of their internal widgets.
        self.dk_page = Dock("page", size=(1280, 720))  ## give this dock the minimum possible size
        self.dk_template = Dock("template", size=(200, 280))
        self.dk_control = Dock("general", size=(240, 280))
        self.dk_info = Dock("info", size=(800, 280))
        # color
        self.dk_color = Dock("color", size=(240, 280))

        # deskew
        self.dk_deskew = Dock("deskew", size=(240, 280))

        # noise
        self.dk_denoise = Dock("denoise", size=(240, 280))

        self.area.addDock(self.dk_page, 'right')
        self.area.addDock(self.dk_template, 'bottom', self.dk_page)
        self.area.addDock(self.dk_denoise, 'right', self.dk_template)
        self.area.addDock(self.dk_info, 'right', self.dk_denoise)
        self.area.moveDock(self.dk_color, 'above', self.dk_denoise)
        self.area.moveDock(self.dk_deskew, 'above', self.dk_color)
        self.area.moveDock(self.dk_control, 'above', self.dk_deskew)

        # info
        self.widget_info = pg.LayoutWidget()
        self.console = ConsoleWidget()
        self.dk_info.addWidget(self.console)

        # page
        img_bgr = asarray(cv2.imread(pages[0]))
        self.frame = img_bgr
        self.image_item_page = MyImageItem(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), console=self.console, axisOrder='row-major')
        self.image_view = pg.ImageView(imageItem=self.image_item_page)
        self.dk_page.addWidget(self.image_view)

        # ROI
        pen = pg.mkPen(width=2, color='g')
        self.rect_roi = pg.RectROI([20, 20], [100, 100], pen=pen)
        self.image_view.getView().addItem(self.rect_roi)
        self.rect_roi.sigRegionChanged[object].connect(self.on_change_rect_roi)

        # template
        img_rgb = asarray(cv2.imread(templates[0]))
        self.image_item_template = pg.ImageItem(img_rgb, axisOrder='row-major')
        self.template_view = pg.ImageView(imageItem=self.image_item_template)
        self.dk_template.addWidget(self.template_view)


        # deskew
        self.label_deskew_dim = QLabel("screen dimension(w,h):")
        self.edit_deskew_dim = QLineEdit()
        self.edit_deskew_dim.setText(self.DEF_SCREEN_DIM)
        self.label_deskew_top_left = QLabel("top left anchor(x,y):")
        self.edit_deskew_top_left = QLineEdit()
        self.label_deskew_top_right = QLabel("top right anchor(x,y):")
        self.edit_deskew_top_right = QLineEdit()
        self.label_deskew_bot_left = QLabel("bottom left anchor(x,y):")
        self.edit_deskew_bot_left = QLineEdit()
        self.label_deskew_bot_right = QLabel("bottom right anchor(x,y):")
        self.edit_deskew_bot_right = QLineEdit()
        self.btn_search_anchors = QPushButton('search anchors automatically')
        self.btn_deskew = QPushButton('deskew screen')
        self.btn_save_deskewed_screen = QPushButton('save deskewed screen')
        self.dk_deskew.addWidget(self.label_deskew_dim, row=0, col=0)
        self.dk_deskew.addWidget(self.edit_deskew_dim, row=0, col=1)
        self.dk_deskew.addWidget(self.label_deskew_top_left, row=1, col=0)
        self.dk_deskew.addWidget(self.edit_deskew_top_left, row=1, col=1)
        self.dk_deskew.addWidget(self.label_deskew_top_right, row=1, col=2)
        self.dk_deskew.addWidget(self.edit_deskew_top_right, row=1, col=3)
        self.dk_deskew.addWidget(self.label_deskew_bot_left, row=2, col=0)
        self.dk_deskew.addWidget(self.edit_deskew_bot_left, row=2, col=1)
        self.dk_deskew.addWidget(self.label_deskew_bot_right, row=2, col=2)
        self.dk_deskew.addWidget(self.edit_deskew_bot_right, row=2, col=3)
        self.dk_deskew.addWidget(self.btn_search_anchors, row=3, col=0)
        self.dk_deskew.addWidget(self.btn_deskew, row=3, col=1)
        self.dk_deskew.addWidget(self.btn_save_deskewed_screen, row=3, col=2)

        self.btn_save_deskewed_screen.clicked.connect(self.on_btn_save_deskewed_screen)
        self.btn_search_anchors.clicked.connect(self.on_btn_search_anchors)
        self.btn_deskew.clicked.connect(self.on_btn_deskew)

        # noise removal/image blurring
        self.label_image_blurring = QLabel("Denoise type:")
        self.cb_image_blurring = QComboBox()
        for blurring_type in self.blurring_types:
            self.cb_image_blurring.addItem(blurring_type)
        self.cb_image_blurring.currentIndexChanged.connect(self.on_cb_image_blurring_type_change)
        self.btn_image_blurring = QPushButton('apply')
        self.btn_save_denoised_screen = QPushButton('save denoised screen')
        self.btn_save_denoised_screen.clicked.connect(self.on_btn_save_denoised_screen)
        self.btn_image_blurring.clicked.connect(self.on_btn_image_blurring)
        self.dk_denoise.addWidget(self.label_image_blurring, row=0, col=0)
        self.dk_denoise.addWidget(self.cb_image_blurring, row=0, col=1)
        self.dk_denoise.addWidget(self.btn_image_blurring, row=0, col=2)
        self.dk_denoise.addWidget(self.btn_save_denoised_screen, row=0, col=3)

        # color calibration
        self.label_color_calibration = QLabel("color template:")
        self.cb_color_calibration_templates = QComboBox()
        for color_template in self.color_templates:
            self.cb_color_calibration_templates.addItem(color_template)
        self.cb_color_calibration_templates.currentIndexChanged.connect(self.on_cb_color_calibration_template_change)
        self.btn_color_calibration_search = QPushButton('search template')
        # self.btn_color_calibration_search.setEnabled(True)
        self.btn_color_calibration_search.clicked.connect(self.on_btn_color_calibration_search)
        self.btn_color_calibration_search_all = QPushButton('search all templates')
        #self.btn_color_calibration_search_all.setEnabled(True)
        self.label_color_space_threshold = QLabel("color space threshold:")
        self.label_rgb_diff_threshold = QLabel("RGB difference threshold:")
        self.edit_color_space_threshold = QLineEdit()
        self.edit_color_space_threshold.setText(self.DEF_COLOR_DISTANCE_THRESHOLD)
        self.edit_rgb_diff_threshold = QLineEdit()
        self.edit_rgb_diff_threshold.setText(self.DEF_RGB_DIFFERENCE_THRESHOLD)
        self.btn_default_threshold = QPushButton('default threshold')
        # self.btn_default_threshold.setEnabled(True)
        self.btn_default_threshold.clicked.connect(self.on_btn_default_threshold)
        self.btn_color_calibration_search_all.clicked.connect(self.on_btn_color_calibration_search_all)
        self.dk_color.addWidget(self.label_color_calibration, row=0, col=0)
        self.dk_color.addWidget(self.cb_color_calibration_templates, row=0, col=1)
        self.dk_color.addWidget(self.btn_color_calibration_search, row=0, col=2)
        self.dk_color.addWidget(self.btn_color_calibration_search_all, row=0, col=3)
        self.dk_color.addWidget(self.label_color_space_threshold, row=1, col=0)
        self.dk_color.addWidget(self.edit_color_space_threshold, row=1, col=1)
        self.dk_color.addWidget(self.label_rgb_diff_threshold, row=1, col=2)
        self.dk_color.addWidget(self.edit_rgb_diff_threshold, row=1, col=3)
        self.dk_color.addWidget(self.btn_default_threshold, row=2, col=1)

        # general
        self.label_video = QLabel("Video:")
        self.cb_video = QComboBox()
        self.cb_video.currentIndexChanged.connect(self.on_cb_video_change)


        self.label_page = QLabel("Page:")
        self.cb_page = QComboBox()
        for page in self.pages:
            self.cb_page.addItem(page)
        self.cb_page.currentIndexChanged.connect(self.on_cb_page_change)

        self.label_template = QLabel("Template:")
        self.cb_template = QComboBox()
        for template in self.templates:
            self.cb_template.addItem(template)
        self.cb_template.currentIndexChanged.connect(self.on_cb_template_change)
        self.template_rgb_avg(self.cb_template.currentText())

        self.btn_save_dockstn = QPushButton('Save dock state')
        self.btn_restore_dock = QPushButton('Restore dock state')
        self.btn_restore_dock.setEnabled(False)
        self.btn_save_dockstn.clicked.connect(self.btn_save)
        self.btn_restore_dock.clicked.connect(self.btn_load)

        self.btn_load_videos = QPushButton('Load videos...')
        self.btn_load_videos.clicked.connect(self.on_load_videos)
        self.btn_load_pages = QPushButton('Load pages...')
        self.btn_load_pages.clicked.connect(self.on_load_pages)
        self.btn_load_templates = QPushButton('Load templates...')
        self.btn_load_templates.clicked.connect(self.on_load_templates)

        self.label_video_capture = QLabel("video capture:")
        self.cb_video_capture = QComboBox()
        self.cb_video_capture.addItem("0")
        self.cb_video_capture.addItem("1")
        self.cb_video_capture.addItem("udp://127.0.0.1:12345")
        self.cb_video_capture.addItem("udp://192.168.8.19:12345")
        self.cb_video_capture.addItem("udp://192.168.8.3:12345")
        self.btn_start_video = QPushButton('Start video')
        self.btn_stop_video = QPushButton('Stop video')

        self.btn_start_camera = QPushButton('Start camera')
        self.btn_stop_camera = QPushButton('Stop camera')
        self.btn_search = QPushButton('Search template')
        self.btn_search_all = QPushButton('Search all templates')
        self.cb_video_capture.currentIndexChanged.connect(self.on_video_capture_change)
        self.btn_start_video.clicked.connect(self.on_btn_start_video)
        self.btn_stop_video.clicked.connect(self.on_btn_stop_video)
        self.btn_start_camera.clicked.connect(self.on_btn_start_camera)
        self.btn_stop_camera.clicked.connect(self.on_btn_start_camera)
        self.btn_search.clicked.connect(self.on_btn_search)
        self.btn_search_all.clicked.connect(self.run_all)
        self.btn_ocr_roi = QPushButton('OCR ROI')
        self.btn_ocr_roi.clicked.connect(self.on_btn_ocr_roi)
        self.btn_save_roi = QPushButton('Save ROI')
        self.btn_save_roi.clicked.connect(self.on_btn_save_roi)

        self.cb_visual = QCheckBox('Visual', self)
        self.cb_export = QCheckBox('Export', self)

        self.dk_control.addWidget(self.label_page, row=0, col=0)
        self.dk_control.addWidget(self.cb_page, row=0, col=1)
        self.dk_control.addWidget(self.btn_load_pages, row=0, col=2)

        self.dk_control.addWidget(self.label_template, row=1, col=0)
        self.dk_control.addWidget(self.cb_template, row=1, col=1)
        self.dk_control.addWidget(self.btn_load_templates, row=1, col=2)

        self.dk_control.addWidget(self.btn_search, row=2, col=0)
        self.dk_control.addWidget(self.btn_search_all, row=2, col=1)
        self.dk_control.addWidget(self.btn_ocr_roi, row=2, col=2)
        self.dk_control.addWidget(self.btn_save_roi, row=2, col=3)

        self.dk_control.addWidget(self.cb_visual, row=3, col=0)
        self.dk_control.addWidget(self.cb_export, row=3, col=1)
        self.dk_control.addWidget(self.btn_save_dockstn, row=3, col=2)
        self.dk_control.addWidget(self.btn_restore_dock, row=3, col=3)

        self.dk_control.addWidget(self.label_video, row=4, col=0)
        self.dk_control.addWidget(self.cb_video, row=4, col=1)
        self.dk_control.addWidget(self.btn_load_videos, row=4, col=2)
        self.dk_control.addWidget(self.btn_start_video, row=4, col=3)
        self.dk_control.addWidget(self.btn_stop_video, row=4, col=4)

        self.dk_control.addWidget(self.label_video_capture, row=5, col=0)
        self.dk_control.addWidget(self.cb_video_capture, row=5, col=1)
        self.dk_control.addWidget(self.btn_start_camera, row=5, col=2)
        self.dk_control.addWidget(self.btn_stop_camera, row=5, col=3)

        self.show()

    def on_btn_search(self):
        visualize = self.cb_visual.isChecked()
        self.template_matching(self.cb_template.currentText())

    def on_btn_start_video(self):
        # self.sim(calculate=False)
        self.play_video()

    def on_btn_start_camera(self):
        if self.start_streaming is False:
            self.start_streaming = True
            self.streaming(self.cb_video_capture.currentText())

    def on_btn_stop_video(self):
        self.start_streaming = False

    def on_btn_start_camera(self):
        self.start_streaming = False

    def streaming(self, camera="0"):
        import cv2
        import numpy as np
        #from goprocam import GoProCamera
        # from goprocam import constants
        # cascPath = "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml"
        # faceCascade = cv2.CascadeClassifier(cascPath)
        print(f"camera is {camera}")
        if camera.isnumeric():
            cap = cv2.VideoCapture(int(camera))
        else:
            #gpCam = GoProCamera.GoPro()
            cap = cv2.VideoCapture(camera)
        frames = 0
        start = time.time()
        # frame control for player
        player_frame_control = False
        player_fps = 10
        player_spf = 60 / player_fps
        while self.start_streaming is True:
            if player_frame_control is True and int(time.time() * 1000) % player_spf != 0:
                continue
            ret, self.frame = cap.read()
            frames += 1
            self.image_item_page.setImage(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
            QtGui.QGuiApplication.processEvents()
            if time.time() > start + 10 :
                print(f"{frames / (time.time() - start)} fp/s")
                start = time.time()
                frames =0

            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        cap.release()
        cv2.destroyAllWindows()
        print(f"{frames / (time.clock() - start)} fp/s")

    def sim(self, calculate=True):
        self.template_avg()
        visualize = self.cb_visual.isChecked()
        # self.template_matching(self.cb_template.currentText())
        cap = cv2.VideoCapture(self.cb_video.currentText())
        if (cap.isOpened() == False):
            print("Error opening video stream or file")

        # Read until video is completed
        frames = 0
        start = time.clock()
        template = cv2.imread(self.cb_template.currentText())
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template_edge = cv2.Canny(template_gray, 50, 200)
        while (cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                frames += 1
                # Display the resulting frame
                # cv2.imshow('Frame', frame)
                if calculate:
                    print(f"frame: {frames}")
                    self.multi_scale_template_matching(template_edge=template_edge, frame=frame, debug=False, paint=False)
                else:
                    self.image_item_page.setImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # Press Q on keyboard to  exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            # Break the loop
            else:
                break

        print(f"{frames / (time.clock() - start)} fp/s")
        # When everything done, release the video capture object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()

    def play_video(self):
        if self.start_streaming is True:
            return
        self.start_streaming = True
        cap = cv2.VideoCapture(self.cb_video.currentText())
        if (cap.isOpened() == False):
            print("Error opening video stream or file")

        # Read until video is completed
        frames = 0
        start = time.time()
        while cap.isOpened() and self.start_streaming is True:
            # Capture frame-by-frame
            ret, self.frame = cap.read()
            if ret == True:
                frames += 1
                self.image_item_page.setImage(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))

                # Press Q on keyboard to exit
                # if cv2.waitKey(25) & 0xFF == ord('q'):
                #     break
            # Break the loop
            else:
                break
            QtGui.QGuiApplication.processEvents()
            if time.time() > start + 10 :
                print(f"{frames / (time.time() - start)} fp/s")
                start = time.time()
                frames = 0


        print(f"{frames / (time.time() - start)} fp/s")
        # When everything done, release the video capture object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()

    def run_all(self):
        visualize = self.cb_visual.isChecked()
        for template in self.templates:
            self.template_matching( template)

    def on_change_rect_roi(self):
        # pic = Image.open(self.cb_page.currentText())
        # pix = np.array(pic.getdata()).reshape(pic.size[1], pic.size[0], 4)
        dim = (int(self.rect_roi.pos()[0]), int(self.rect_roi.pos()[1]),
               int(self.rect_roi.pos()[0] + self.rect_roi.size()[0]),
               int(self.rect_roi.pos()[1] + self.rect_roi.size()[1]))
        # b = np.average(pix[dim[1]:dim[3],dim[0]:dim[2], 0])
        # g = np.average(pix[dim[1]:dim[3],dim[0]:dim[2], 1])
        # r = np.average(pix[dim[1]:dim[3],dim[0]:dim[2], 2])
        b = int(np.average(self.frame[dim[1]:dim[3], dim[0]:dim[2], 0]))
        g = int(np.average(self.frame[dim[1]:dim[3], dim[0]:dim[2], 1]))
        r = int(np.average(self.frame[dim[1]:dim[3], dim[0]:dim[2], 2]))
        roi_rgb = (r, g, b)

        # print(f"ROI pic size {pic.size}")
        # print(f"ROI pix shape: {pix.shape}, ROI pix size: {pix.size}")
        delta = compare_rgb(self.template_rgb, roi_rgb)
        self.console.write(f"ROI avg RGB: {r}, {g}, {b}, template distance: {delta}\n")
        print(f"ROI avg RGB: {r}, {g}, {b}, template avg RGB: {self.template_rgb}, template distance:{delta}")

    def template_rgb_avg(self, template_file):
        pic = Image.open(template_file)
        print(f"template_rgb_avg: {pic.size}, mode: {pic.mode}")
        if pic.mode == "RGBA":
            colors_depth = 4
        elif pic.mode == "RGB":
            colors_depth = 3
        else:
            assert False, "Unknown color format. Support RGBA and RGB only"
        pix = np.array(pic.getdata()).reshape(pic.size[1], pic.size[0], colors_depth)
        r = int(np.average(pix[:,:,0]))
        g = int(np.average(pix[:,:,1]))
        b = int(np.average(pix[:,:,2]))
        self.template_rgb=(r,g,b)

        print(f"pic size {pic.size}")
        print(f"pix shape: {pix.shape}, pix size: {pix.size}")
        print(f"Template color avg RGB: {r}, {g}, {b}")
        self.console.write(f"template color avg RGB: {r}, {g}, {b}\n")

    def on_load_videos(self):
        fnames = QFileDialog.getOpenFileNames(self, '=Load videos', './', "Video files (*.mov *.mp4)")
        # fnames=[["/Users/h0t00qt/Documents/VuduAutomation/calibration/video.mp4"]]
        print(f"load video: {fnames}")
        if fnames[0] != '':
            for fname in fnames[0]:
                self.cb_video.addItem(fname)
                self.videos.append(fname)

    def on_load_pages(self):
        fnames = QFileDialog.getOpenFileNames(self, '=Load pages', './', "Image files (*.png)")
        print(f"load page: {fnames}")
        if fnames[0] != '':
            for fname in fnames[0]:
                self.cb_page.addItem(fname)
                self.pages.append(fname)
            # upload pages listbox
            self.cb_page.setCurrentIndex(len(self.pages)-1)

    def on_load_templates(self):
        fnames = QFileDialog.getOpenFileNames(self, '=Load templates','./', "Image files (*.png)")
        print(f"load template: {fnames}")
        if fnames[0] !=  '':
            for fname in fnames[0]:
                self.cb_template.addItem(fname)
                self.templates.append(fname)
            self.cb_template.setCurrentIndex(len(self.templates)-1)

    def on_video_capture_change(self):
        pass

    def on_btn_ocr_roi(self):
        assert self.frame is not None
        # im = Image.open(self.cb_page.currentText())
        dim = (int(self.rect_roi.pos()[0]), int(self.rect_roi.pos()[1]),
               int(self.rect_roi.pos()[0] + self.rect_roi.size()[0]),
                int(self.rect_roi.pos()[1] + self.rect_roi.size()[1]))
        # region = im.crop(dim)

        region = self.frame[dim[1]:dim[3],dim[0]:dim[2]]
        text = pytesseract.image_to_string(region)
        # text = pytesseract.image_to_string(self.frame)
        print(f"ocr roi pos: {dim}, result: {text}")
        self.console.write(f"ocr roi pos: {dim}, result: {text}")

    def on_btn_save_roi(self):
        print("roi pos: {}".format(self.rect_roi.pos()))
        print("roi size: {}".format(self.rect_roi.size()))

        im = Image.open(self.cb_page.currentText())
        dim = (int(self.rect_roi.pos()[0]), int(self.rect_roi.pos()[1]), int(self.rect_roi.pos()[0] + self.rect_roi.size()[0]),
               int(self.rect_roi.pos()[1] + self.rect_roi.size()[1]))
        region = im.crop(dim)

        name = ntpath.basename(self.cb_page.currentText()).strip(".png")
        name = "{}_{}_{}_{}_{}.png".format(name,
                                                int(self.rect_roi.pos()[0]), int(self.rect_roi.pos()[1]),
                                                int(self.rect_roi.pos()[0] + self.rect_roi.size()[0]),
                                                int(self.rect_roi.pos()[1] + self.rect_roi.size()[1]))
        region.save(name)
        self.console.write(f"ROI image: {name} is created \n")

    def btn_save(self):
        self.state = self.area.saveState()
        self.btn_restore_dock.setEnabled(True)

    def btn_load(self):
        self.area.restoreState(self.state)

    def on_cb_template_change(self, i):
        img_bgr = asarray(cv2.imread(self.templates[i]))
        self.image_item_template.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        self.template_rgb_avg(self.templates[i])

    def on_cb_page_change(self, i):
        img_bgr = asarray(cv2.imread(self.pages[i]))
        self.image_item_page.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        self.frame = img_bgr

    def on_cb_video_change(self, i):
        pass
        # img_bgr = asarray(cv2.imread(self.videos[i]))
        # self.image_item_page.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

    def on_cb_color_calibration_template_change(self, i):
        img_bgr = asarray(cv2.imread(self.color_templates[i]))
        self.image_item_template.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        self.template_rgb_avg(self.color_templates[i])

    def on_cb_image_blurring_type_change(self, i):
        pass

    def on_btn_image_blurring(self):
        pass

    def on_btn_color_calibration_search(self):
        self.template_matching(self.cb_color_calibration_templates.currentText())

    def on_btn_color_calibration_search_all(self):
        pass

    def on_btn_default_threshold(self):
        self.edit_rgb_diff_threshold.setText(self.DEF_RGB_DIFFERENCE_THRESHOLD)
        self.edit_color_space_threshold.setText(self.DEF_COLOR_DISTANCE_THRESHOLD)

    def on_btn_search_anchors(self):
        pass

    def on_btn_deskew(self):
        img = self.frame  # cv2.imread('sudokusmall.png')
        rows, cols, ch = img.shape
        top_left = list(map(int, self.edit_deskew_top_left.text().split(',')))
        top_right = list(map(int, self.edit_deskew_top_right.text().split(',')))
        bot_left = list(map(int, self.edit_deskew_bot_left.text().split(',')))
        bot_right = list(map(int, self.edit_deskew_bot_right.text().split(',')))
        pts1 = np.float32([top_left, top_right, bot_left, bot_right])
        width,height =  list(map(int, self.edit_deskew_dim.text().split(',')))
        pts2 = np.float32([[0, 0], [width, 0], [0, 1080], [width, height]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        self.deskewed_frame = cv2.warpPerspective(img, M, (width, height))
        self.image_item_page.setImage(cv2.cvtColor(self.deskewed_frame, cv2.COLOR_BGR2RGB))
        self.frame = self.deskewed_frame

    def on_btn_save_denoised_screen(self):
        pass

    def on_btn_save_deskewed_screen(self):
        width, height =  list(map(int, self.edit_deskew_dim.text().split(',')))
        basename = ntpath.basename(self.cb_page.currentText()).strip(".png")
        name = "{}_{}x{}.png".format(basename, width, height)
        cv2.imwrite(name, self.deskewed_frame)
        self.console.write(f"deskewed screen saved ase: {name}  \n")

    def multi_scale_template_matching(self, template_file=None, template_edge=None, frame=None, debug=True, paint=True):
        if template_edge is None:
            template = cv2.imread(template_file)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            template_edge = cv2.Canny(template_gray, 50, 200)
        (tH, tW) = template_edge.shape[:2]
        if paint and self.cb_visual.isChecked():
            self.image_item_template.setImage(template_edge)
        # load the image, convert it to grayscale, and initialize the
        # bookkeeping variable to keep track of the matched region
        if frame is not None:
            image = frame
        else:
            image = cv2.imread(self.cb_page.currentText())
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.found = None

        # loop over the scales of the image
        # for scale in np.linspace(0.2, 1.0, 20)[::-1]:
        for scale in [1]:
        # for scale in np.linspace(1.0, 1.0, 1)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break
            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, template_edge, cv2.TM_CCOEFF)
            result_1 = 1 - result
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # check to see if the iteration should be visualized
            if paint and self.cb_visual.isChecked() is True:
                # draw a bounding box around the detected region
                clone = np.dstack([edged, edged, edged])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                              (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 10)
                self.image_item_page.setImage(clone)
                QtGui.QGuiApplication.processEvents()

                # cv2.waitKey(0)

            # if we have found a new maximum correlation value, then update
            # the bookkeeping variable
            if self.found is None or maxVal > self.found[0]:
                self.found = (maxVal, maxLoc, r)
                if debug:
                    print("{}:  {}".format(page_file, self.found))
                self.console.write(f"{self.cb_page.currentText()} found in {template_file}: {self}\n")


        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio
        (_, maxLoc, r) = self.found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
        if debug:
            print("{}: found: {}".format(page_file, self.found))
        self.console.write("{}: {}\n".format(page_file, self.found))

        # calculate avg color here
        if debug:
            print (f"image size: {image.size}")
            print (f"image shape: {image.shape}")
            print(f"startX: {startX}, endX: {endX}, startY: {startY}, endY: {endY}")
            # cv2 use BGR order ! y-X axis
            b = int(np.average(image[startY:endY,startX:endX,0]))
            g = int(np.average(image[startY:endY,startX:endX,1]))
            r = int(np.average(image[startY:endY,startX:endX,2]))
            self.console.write(f"color avg RGB: {r}, {g}, {b}\n")
            print(f"color avg RGB: {r}, {g}, {b}\n")

        if paint is True:
            # draw a bounding box around the detected result and display the image
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 10)

            self.image_item_page.setImage(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if self.cb_visual.isChecked():
                template = cv2.imread(template_file)
                self.image_item_template.setImage(cv2.cvtColor(template, cv2.COLOR_BGR2RGB))
            QtGui.QGuiApplication.processEvents()

        return

        pic = Image.open(self.cb_page.currentText())
        if debug:
            print(f"pic size {pic.size}")
        pix = np.array(pic.getdata()).reshape(pic.size[1], pic.size[0], 4)
        if debug:
            print(f"startX: {startX}, endX: {endX}, startY: {startY}, endY: {endY}")
            print(f"pix shape: {pix.shape}, pix size: {pix.size}")
        # region = pix[startX:endX,startY:endY]
        # print(f"region shape: {region.shape}, region size: {region.size}")
        # PIL use RGB order
        # r = np.average(pix[startX:endX,startY:endY,0])
        # g = np.average(pix[startX:endX,startY:endY,1])
        # b = np.average(pix[startX:endX,startY:endY,2])
        #
        # self.console.write(f"color avg RGB: {r}, {g}, {b}\n")
        # print(f"color avg RGB: {r}, {g}, {b}\n")
        r = int(np.average(pix[startY:endY,startX:endX,0]))
        g = int(np.average(pix[startY:endY,startX:endX,1]))
        b = int(np.average(pix[startY:endY,startX:endX,2]))

        self.console.write(f"color avg RGB: {r}, {g}, {b}\n")
        if debug:
            print(f"color avg RGB: {r}, {g}, {b}\n")

    def template_matching(self, template_file=None, frame=None,  threshold=0.60, paint=True):

        COLOR_DISTANCE_THRESHOLD = float(self.edit_color_space_threshold.text())
        RGB_DIFFERENCE_THRESHOLD = int(self.edit_rgb_diff_threshold.text())
        # load the image, convert it to grayscale, and initialize the
        # bookkeeping variable to keep track of the matched region
        if frame is not None:
            # img = frame
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            # img = cv2.imread(self.cb_page.currentText(), 0)
            img = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(template_file, 0)
        w, h = template.shape[::-1]

        # All the 6 methods for comparison in a list
        methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
                   'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

        for meth in ['cv2.TM_SQDIFF_NORMED']: # methods:
            method = eval(meth)

            # Apply template Matching
            res = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
                val = min_val
                if  max_val == min_val:
                    result = 0.0
                else:
                    result = 1.0 - val / (max_val) # - min_val)
            else:
                top_left = max_loc
                val = max_val
                if max_val == min_val:
                    result = 0.0
                else:
                    result = val / (max_val) # - min_val)
            bottom_right = (top_left[0] + w, top_left[1] + h)
            (startX, startY) = top_left
            (endX, endY) = bottom_right

            b = int(np.average(self.frame[startY:endY, startX:endX, 0]))
            g = int(np.average(self.frame[startY:endY, startX:endX, 1]))
            r = int(np.average(self.frame[startY:endY, startX:endX, 2]))

            # r = np.average(self.frame[startX:endX, startY:endY, 0])
            # g = np.average(self.frame[startX:endX, startY:endY, 1])
            # b = np.average(self.frame[startX:endX, startY:endY, 2])

            self.console.write(f"color avg RGB: {r}, {g}, {b}\n")
            print(f"color avg RGB: {r}, {g}, {b}\n")
            delta = compare_rgb((r, g, b),self.template_rgb)

            self.console.write(f"result:{result}, distance(color space, r,g,b):{delta[0]:.2f},{delta[1]},{delta[2]},{delta[3]}, loc:{top_left, bottom_right}")
            print(f"result:{result}, distance(color space, r,g,b):{delta}")
            if result < threshold:
               print(f"{meth}: no template found. threshold {result} <  {threshold}")
            elif delta[0] > COLOR_DISTANCE_THRESHOLD:
                print(f"{meth}: no template found. delta_e {delta[0]:.2f} > {COLOR_DISTANCE_THRESHOLD}")
            elif sum(delta[1:]) > RGB_DIFFERENCE_THRESHOLD:
                print(f"{meth}: no template found. delta_rgb {delta[1:]} > {RGB_DIFFERENCE_THRESHOLD}")
            else:
                # check to see if the iteration should be visualized
                # cv2.waitKey(0)
                if paint is True:
                    # draw a bounding box around the detected result and display the image
                    frame = self.frame.copy()
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 5)
                    print(f"{meth}: found template at {top_left}, {bottom_right}, val: {val}({min_val, max_val}), result: {result}")
                    self.image_item_page.setImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    QtGui.QGuiApplication.processEvents()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    def usage():
        print("{} Ver. {} calibrate screen catpure for automation.".format(sys.argv[0], VERSION))
        print("\t -v  --verbose verbose")
        print("\t -h  --help   usage")
        print("\t -p  --page  filename. This file contains pages you want to process. A page is ....")
        print("\t -t  --template filename.  This file contains templates you want to process. A template is ...")


    verbose = False
    page_file = None
    template_file = None
    image_arr = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vhp:t:", ["verbose", "help", "page", "template"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(0)
        elif opt in ("-p", "--page"):
            page_file = arg
        elif opt in ("-t", "--template"):
            template_file = arg
        elif opt in ("-v", "--verbose"):
            verbose = True

    if page_file == None and template_file == None:
        print("error:  file(s) not found")
        # usage()
        sys.exit(2)

    try:
        pages = []
        with open(page_file, "rt") as f:
            for line in f:
                line = line.rstrip("\n")
                line = line.rstrip()
                if line == "" or line[0] == '#':
                    continue
                print("read {}".format(line))
                pages += glob.glob(line)
    except Exception as e:
        print("error: fail to open {}. {} ".format(page_file, e))
        exit(2)
    if len(pages) == 0:
        print("error: no page found in {}".format(page_file))
        exit(2)
    try:
        templates = []
        with open(template_file, "rt") as f:
            for line in f:
                line = line.rstrip("\n")
                line = line.rstrip()
                if line == "" or line[0] == '#':
                    continue
                print("read {}".format(line))
                templates += glob.glob(line)
    except Exception as e:
        print("error: fail to open {}. {} ".format(template_file, e))
        exit(2)
    if len(templates) == 0:
        print("error: no template found in {}".format(template_file))
        exit(2)

    settings_file= "./settings.json"
    with open(settings_file) as f:
        data = json.load(f)

    print(f"device id: {data['device_id']}, user email:{data['user_email']}, user password:{data['user_password']} ")
    for page, value in data["pages"].items():
        print(f"{page}:{value}")


    app = QtGui.QApplication([])

    view = CalibrationView(pages= pages, templates=templates, title="Vudu Screen Capture calibration ver.{}. All rights reserved.".format(VERSION),
                     verbose=verbose)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()



