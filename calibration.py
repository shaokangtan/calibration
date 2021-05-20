'''
Known issues:
1. load video contain worng path
2. video total frame count is incorrect sometimes
'''
import sys
import cv2
import pyqtgraph as pg
from numpy import asarray
from pyqtgraph.dockarea import DockArea
from pyqtgraph.dockarea.DockArea import Dock
from pyqtgraph.Qt import QtCore, QtGui
# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QSlider, QHBoxLayout, QLabel, QWidget, QLineEdit, QPushButton, QComboBox, QFileDialog,\
    QCheckBox, QMainWindow
# from PyQt5.Qt import *
from PyQt5.QtCore import Qt
from pyqtgraph.console import ConsoleWidget
import numpy as np
import imutils
from PIL import Image
import getopt
import glob
import ntpath
import json
import socket
import config

import time
from lib.vudu_image import comp_rgb, search_corners, match, ocr, init_deskew, run_deskew, Region
from lib.camera_lib import Camera
from lib.util import debug

VERSION = "0.0.1"


class MyImageItem(pg.ImageItem):
    def __init__(self, image, console, **kwargs):
        super().__init__(image, **kwargs)
        self.console = console

    def mouseClickEvent(self, ev):
        super().mouseClickEvent(ev)
        if ev.button() == QtCore.Qt.LeftButton:
            # print(f"mouse pos: {ev.pos()}")
            # self.console.write(f"mouse pos: {ev.pos()[0]:.2f}, {ev.pos()[1]:.2f}")
            self.console.write(f"mouse pos: {ev.pos()[0]:.0f}, {ev.pos()[1]:.0f}\n")


class CalibrationView(QMainWindow):
    def __init__(self, pages, templates, parent=None, title=None, verbose=False):
        super(QMainWindow, self).__init__(parent)
        self.cv2_version_major = int(cv2.__version__.split('.')[0])
        if len(pages) == 0 or len(templates) == 0:
            print("error: no pages/templates loaded")
            return None
        self.videos = []
        self.pages = list(pages)
        self.templates = list(templates)
        self.DEF_TEMP_MATCH_THRESHOLD = 0.80
        self.DEF_COLOR_DISTANCE_THRESHOLD = "25.0"
        self.DEF_RGB_DIFFERENCE_THRESHOLD = "50"
        self.DEF_SCREEN_DIM = "1920,1080"
        self.DEF_SCALE_DIM = "1280,720"
        self.DEF_TEMPLATE_SEARCH_REGION = "0, 0, -1,-1"
        self.TEMPLATE_MATCH_METHODS = ['cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED',
                                       'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED',
                                       'cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED'
                                       ]
        self.DEF_TEMPLATE_SEARCH_METHOD = 'cv2.TM_CCORR_NORMED'

        # self.DEF_RC_URL = "http://192.168.8.19:33" # remote
        import config
        self.DEF_RC_URL = "http://" + config.CAMERA_IP # local
        self.DEF_STREAM_PORT = "1000"
        self.DEF_STREAM_FRAME_RATE = "30"
        self.DEF_RC_FRAME_PATH = "_frame.png"

        self.blurring_types = ["Averaging 3x3", "Averaging 5x5", "Gaussian Filtering 3x3", "Gaussian Filtering 5x5",
                               "Median Filtering 3", "Median Filtering", "Bilateral Filtering"]
        self.color_templates = ["images/color_calibration/blue_tall.png", "images/color_calibration/blue_short.png",
                                "images/color_calibration/cyan_tall.png", "images/color_calibration/cyan_short.png",
                                "images/color_calibration/green_tall.png", "images/color_calibration/purple_short.png",
                                "iges/color_calibration/yellow_tall.png", "images/color_calibration/yellow_short.png",
                                "images/color_calibration/gray_tall.png",
                                "images/color_calibration/gray_light_tall.png",
                                "images/color_calibration/gray_gradient.png",
                                "images/color_calibration/magenta_tall.png",
                                "images/color_calibration/red_tall.png", "images/color_calibration/red_short.png"
                                ]
        self.verbose = verbose
        self.area = DockArea()
        self.setCentralWidget(self.area)
        self.resize(1024, 900)
        self.setWindowTitle(title)
        self.start_streaming = False
        self.pause_video = False
        self.cap = None
        self.deskewed_frame = None
        self.PerspectiveTransform = None


        # Create docks, place them into the window one at a time.
        # Note that size arguments are only a suggestion; docks will still have to
        # fill the entire dock self.area and obey the limits of their internal widgets.
        self.dk_page = Dock("page", size=(1280, 720))  # give this dock the minimum possible size
        self.dk_template = Dock("template", size=(200, 280))
        self.dk_control = Dock("general", size=(500, 280))
        self.dk_info = Dock("info", size=(500, 280))
        # color
        self.dk_color = Dock("color", size=(500, 280))

        # deskew
        self.dk_deskew = Dock("deskew", size=(500, 280))

        # noise
        self.dk_denoise = Dock("denoise", size=(500, 280))

        # remote camera
        self.dk_remote = Dock("remote cam", size=(500, 280))

        self.area.addDock(self.dk_page, 'right')
        self.area.addDock(self.dk_template, 'bottom', self.dk_page)
        self.area.addDock(self.dk_remote, 'right', self.dk_template)
        self.area.addDock(self.dk_info, 'right', self.dk_remote)
        self.area.addDock(self.dk_denoise, 'above', self.dk_remote)
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
        self.image_item_page = MyImageItem(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), console=self.console,
                                           axisOrder='row-major')
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
        self.label_deskew_dim = QLabel("Deskew screen size(w,h):")
        self.edit_deskew_dim = QLineEdit()
        self.edit_deskew_dim.setFixedWidth(80)
        self.edit_deskew_dim.setText(self.DEF_SCREEN_DIM)
        self.label_deskew_top_left = QLabel("Top left corner(x,y):")
        self.edit_deskew_top_left = QLineEdit()
        self.edit_deskew_top_left.setFixedWidth(80)
        self.label_deskew_top_right = QLabel("Top right corner(x,y):")
        self.edit_deskew_top_right = QLineEdit()
        self.edit_deskew_top_right.setFixedWidth(80)
        self.label_deskew_bot_left = QLabel("Bottom left corner(x,y):")
        self.edit_deskew_bot_left = QLineEdit()
        self.edit_deskew_bot_left.setFixedWidth(80)
        self.label_deskew_bot_right = QLabel("Bottom right corner(x,y):")
        self.edit_deskew_bot_right = QLineEdit()
        self.edit_deskew_bot_right.setFixedWidth(80)
        self.btn_search_corners = QPushButton('Search corners')
        self.btn_deskew = QPushButton('deskew screen')
        self.btn_save_deskewed_screen = QPushButton('save deskewed screen')
        self.cb_apply_deskewed_screen = QCheckBox('Apply deskew to video')
        self.label_scale_dim = QLabel("Scale screen to (w,h):")
        self.edit_scale_dim = QLineEdit()
        self.edit_scale_dim.setFixedWidth(80)
        self.edit_scale_dim.setText(self.DEF_SCALE_DIM)
        self.btn_scale = QPushButton('scale screen')
        self.btn_save_scaled_screen = QPushButton('save scaled screen')
        # deskew tab calibration
        self.dk_deskew.addWidget(self.label_deskew_dim, row=0, col=0, rowspan=1, colspan=1)
        self.dk_deskew.addWidget(self.edit_deskew_dim, row=0, col=1, rowspan=1, colspan=1)
        self.dk_deskew.addWidget(self.label_deskew_top_left, row=1, col=0)
        self.dk_deskew.addWidget(self.edit_deskew_top_left, row=1, col=1)
        self.dk_deskew.addWidget(self.label_deskew_top_right, row=1, col=2)
        self.dk_deskew.addWidget(self.edit_deskew_top_right, row=1, col=3)
        self.dk_deskew.addWidget(self.label_deskew_bot_left, row=2, col=0)
        self.dk_deskew.addWidget(self.edit_deskew_bot_left, row=2, col=1)
        self.dk_deskew.addWidget(self.label_deskew_bot_right, row=2, col=2)
        self.dk_deskew.addWidget(self.edit_deskew_bot_right, row=2, col=3)
        self.dk_deskew.addWidget(self.btn_search_corners, row=3, col=0)
        self.dk_deskew.addWidget(self.btn_deskew, row=3, col=1)
        self.dk_deskew.addWidget(self.btn_save_deskewed_screen, row=3, col=2)
        self.dk_deskew.addWidget(self.cb_apply_deskewed_screen, row=3, col=3)
        self.dk_deskew.addWidget(self.label_scale_dim, row=4, col=0)
        self.dk_deskew.addWidget(self.edit_scale_dim, row=4, col=1)
        self.dk_deskew.addWidget(self.btn_scale, row=4, col=2)
        self.dk_deskew.addWidget(self.btn_save_scaled_screen, row=4, col=3)

        self.btn_save_deskewed_screen.clicked.connect(self.on_btn_save_deskewed_screen)
        self.btn_save_scaled_screen.clicked.connect(self.on_btn_save_scaled_screen)
        self.btn_search_corners.clicked.connect(self.on_btn_search_corners)
        self.btn_deskew.clicked.connect(self.on_btn_deskew)
        self.btn_scale.clicked.connect(self.on_btn_scale)

        # noise removal/image blurring
        self.label_image_blurring = QLabel("Denoise type:")
        self.cb_image_blurring = QComboBox()
        for blurring_type in self.blurring_types:
            self.cb_image_blurring.addItem(blurring_type)
        self.cb_image_blurring.currentIndexChanged.connect(self.on_cb_image_blurring_type_change)
        self.btn_denoise_screen = QPushButton('denoise screen')
        self.btn_save_denoised_screen = QPushButton('save denoised screen')
        self.btn_save_denoised_screen.clicked.connect(self.on_btn_save_denoised_screen)
        self.btn_denoise_screen.clicked.connect(self.on_btn_denoise_screen)
        # denoise tab layout
        self.dk_denoise.addWidget(self.label_image_blurring, row=0, col=0)
        self.dk_denoise.addWidget(self.cb_image_blurring, row=0, col=1)
        self.dk_denoise.addWidget(self.btn_denoise_screen, row=0, col=2)
        self.dk_denoise.addWidget(self.btn_save_denoised_screen, row=0, col=3)

        # color calibration
        self.label_color_calibration = QLabel("color template:")
        self.cb_color_calibration_templates = QComboBox()
        self.cb_color_calibration_templates.setFixedWidth(250)
        for color_template in self.color_templates:
            self.cb_color_calibration_templates.addItem(color_template)
        self.cb_color_calibration_templates.currentIndexChanged.connect(self.on_cb_color_calibration_template_change)
        self.btn_color_calibration_search = QPushButton('search template')
        # self.btn_color_calibration_search.setEnabled(True)
        self.btn_color_calibration_search.clicked.connect(self.on_btn_color_calibration_search)
        self.btn_color_calibration_search_all = QPushButton('search all temps')
        # self.btn_color_calibration_search_all.setEnabled(True)
        self.label_color_space_threshold = QLabel("Color space threshold:")
        self.label_rgb_diff_threshold = QLabel("RGB diff. threshold:")
        self.edit_color_space_threshold = QLineEdit()
        self.edit_color_space_threshold.setFixedWidth(80)
        self.edit_color_space_threshold.setText(self.DEF_COLOR_DISTANCE_THRESHOLD)
        self.edit_rgb_diff_threshold = QLineEdit()
        self.edit_rgb_diff_threshold.setFixedWidth(80)
        self.edit_rgb_diff_threshold.setText(self.DEF_RGB_DIFFERENCE_THRESHOLD)
        self.btn_default_threshold = QPushButton('default threshold')
        # self.btn_default_threshold.setEnabled(True)
        self.btn_default_threshold.clicked.connect(self.on_btn_default_threshold)
        self.btn_color_calibration_search_all.clicked.connect(self.on_btn_color_calibration_search_all)
        # color calib. layout
        # self.dk_color.addWidget(self.label_color_calibration, row=0, col=0)
        self.dk_color.addWidget(self.cb_color_calibration_templates, row=0, col=0, colspan=2)
        self.dk_color.addWidget(self.btn_color_calibration_search, row=0, col=2)
        self.dk_color.addWidget(self.btn_color_calibration_search_all, row=0, col=3)
        self.dk_color.addWidget(self.label_color_space_threshold, row=1, col=0)
        self.dk_color.addWidget(self.edit_color_space_threshold, row=1, col=1)
        self.dk_color.addWidget(self.label_rgb_diff_threshold, row=2, col=0)
        self.dk_color.addWidget(self.edit_rgb_diff_threshold, row=2, col=1)
        self.dk_color.addWidget(self.btn_default_threshold, row=3, col=0)

        # remote camera
        self.start_rc_streaming = False
        self.remote_camera = Camera()
        self.edit_rc_remote_camera_url = QLineEdit()
        self.edit_rc_remote_camera_url.setFixedWidth(150)
        self.edit_rc_remote_camera_url.setText(self.DEF_RC_URL)
        self.label_rc_remote_camera_url = QLabel("Camera url:")
        self.edit_rc_stream_port = QLineEdit()
        self.edit_rc_stream_port.setFixedWidth(80)
        self.edit_rc_stream_port.setText(self.DEF_STREAM_PORT)
        self.label_rc_stream_port = QLabel("Stream port:")
        self.edit_rc_stream_rate = QLineEdit()
        self.edit_rc_stream_rate.setFixedWidth(80)
        self.edit_rc_stream_rate.setText(self.DEF_STREAM_FRAME_RATE)
        self.label_rc_stream_rate = QLabel("Stream frame rate:")
        self.btn_rc_get_frame = QPushButton('get frame')
        self.btn_rc_current_frame = QPushButton('current frame')
        self.btn_rc_start_video = QPushButton('start video')
        self.btn_rc_stop_video = QPushButton('stop video')
        self.btn_rc_alloc = QPushButton('alloc')
        self.btn_rc_free = QPushButton('free')
        self.cb_add_timestamp = QCheckBox('Add timestamp to video')
        self.btn_save_frame = QPushButton('save frame')

        self.btn_rc_alloc.clicked.connect(self.on_btn_rc_alloc)
        self.btn_rc_free.clicked.connect(self.on_btn_rc_free)
        self.btn_rc_current_frame.clicked.connect(self.on_btn_rc_current_frame)
        self.btn_rc_get_frame.clicked.connect(self.on_btn_rc_get_frame)
        self.btn_rc_start_video.clicked.connect(self.on_btn_rc_start_video)
        self.btn_rc_stop_video.clicked.connect(self.on_btn_rc_stop_video)

        self.btn_save_frame.clicked.connect(self.on_btn_save_frame)


        # remote camera layout
        self.dk_remote.addWidget(self.label_rc_remote_camera_url, row=0, col=0)
        self.dk_remote.addWidget(self.edit_rc_remote_camera_url, row=0, col=1)
        self.dk_remote.addWidget(self.btn_rc_alloc, row=0, col=2)
        self.dk_remote.addWidget(self.btn_rc_free, row=0, col=3)
        self.dk_remote.addWidget(self.label_rc_stream_port, row=2, col=0)
        self.dk_remote.addWidget(self.edit_rc_stream_port, row=2, col=1)

        self.dk_remote.addWidget(self.btn_rc_current_frame, row=3, col=0)
        self.dk_remote.addWidget(self.btn_rc_get_frame, row=3, col=1)
        self.dk_remote.addWidget(self.btn_rc_start_video, row=3, col=2)
        self.dk_remote.addWidget(self.btn_rc_stop_video, row=3, col=3)
        self.dk_remote.addWidget(self.label_rc_stream_rate, row=4, col=0)
        self.dk_remote.addWidget(self.edit_rc_stream_rate, row=4, col=1)
        self.dk_remote.addWidget(self.cb_add_timestamp, row=4, col=2)
        self.dk_remote.addWidget(self.btn_save_frame, row=4, col=3)


        # general tab
        self.label_video = QLabel("Video:")
        self.cb_video = QComboBox()
        self.cb_video.currentIndexChanged.connect(self.on_cb_video_change)

        self.label_page = QLabel("Page:")
        self.cb_page = QComboBox()
        self.cb_page.setFixedWidth(250)
        for page in self.pages:
            self.cb_page.addItem(page)
        self.cb_page.currentIndexChanged.connect(self.on_cb_page_change)

        self.label_template = QLabel("Template:")
        self.cb_template = QComboBox()
        self.cb_template.setFixedWidth(250)
        for template in self.templates:
            self.cb_template.addItem(template)
        self.cb_template.currentIndexChanged.connect(self.on_cb_template_change)
        self.template_rgb_avg(self.cb_template.currentText())

        self.label_template_search_method = QLabel("Search method:")
        self.cb_template_search_methods = QComboBox()
        self.cb_template_search_methods.setFixedWidth(200)
        for template in self.TEMPLATE_MATCH_METHODS:
            self.cb_template_search_methods.addItem(template)
        self.cb_template_search_methods.setCurrentText(self.DEF_TEMPLATE_SEARCH_METHOD)
        self.label_template_search_method_retry = QLabel("Try again:")
        self.cb_try_diff_temp_search_if_fail = QCheckBox("when temp. search failed")

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
        self.cb_video_capture.addItem("2")
        self.cb_video_capture.addItem("3")
        self.cb_video_capture.addItem("udp://127.0.0.1:12345")
        self.cb_video_capture.addItem("udp://192.168.8.19:12345")
        self.cb_video_capture.addItem("udp://192.168.8.3:12345")
        self.btn_start_video = QPushButton('Start/Pause video')
        self.btn_stop_video = QPushButton('Stop video')
        self.btn_fwd_one_frame_video = QPushButton('fwd one frame')
        self.btn_fwd_one_frame_video.setEnabled(False)


        self.btn_start_camera = QPushButton('Start camera')
        self.btn_stop_camera = QPushButton('Stop camera')
        self.btn_search = QPushButton('Search template')
        self.btn_search_all = QPushButton('Search all temps')

        self.frame_slider = Slider(0, 100 - 1, Qt.Horizontal)
        self.frame_slider.slider.valueChanged.connect(self.frame_update)

        self.cb_video_capture.currentIndexChanged.connect(self.on_video_capture_change)
        self.btn_start_video.clicked.connect(self.on_btn_start_video)
        self.btn_stop_video.clicked.connect(self.on_btn_stop_video)
        self.btn_fwd_one_frame_video.clicked.connect(self.on_btn_fwd_one_frame_video)
        self.btn_start_camera.clicked.connect(self.on_btn_start_camera)
        self.btn_stop_camera.clicked.connect(self.on_btn_stop_camera)
        self.btn_search.clicked.connect(self.on_btn_search)
        self.btn_search_all.clicked.connect(self.run_all)
        self.btn_ocr_roi = QPushButton('OCR ROI')
        self.btn_ocr_roi.clicked.connect(self.on_btn_ocr_roi)
        self.btn_save_roi = QPushButton('Save ROI')
        self.btn_save_roi.clicked.connect(self.on_btn_save_roi)

        self.label_template_search_region = QLabel("Search temp. in:")
        self.edit_template_search_region = QLineEdit()
        self.edit_template_search_region.setFixedWidth(120)
        self.edit_template_search_region.setText(self.DEF_TEMPLATE_SEARCH_REGION)

        # general tab layout
        self.dk_control.addWidget(self.label_page, row=0, col=0)
        self.dk_control.addWidget(self.cb_page, row=0, col=1)
        self.dk_control.addWidget(self.btn_load_pages, row=0, col=2)

        self.dk_control.addWidget(self.label_template, row=1, col=0)
        self.dk_control.addWidget(self.cb_template, row=1, col=1)
        self.dk_control.addWidget(self.btn_load_templates, row=1, col=2)

        self.dk_control.addWidget(self.label_template_search_method, row=2, col=0)
        self.dk_control.addWidget(self.cb_template_search_methods, row=2, col=1)

        self.dk_control.addWidget(self.btn_search, row=2, col=2)
        self.dk_control.addWidget(self.btn_search_all, row=2, col=3)

        self.dk_control.addWidget(self.label_template_search_method_retry, row=3, col=0)
        self.dk_control.addWidget(self.cb_try_diff_temp_search_if_fail, row=3, col=1)
        self.dk_control.addWidget(self.btn_ocr_roi, row=3, col=2)
        self.dk_control.addWidget(self.btn_save_roi, row=3, col=3)

        self.dk_control.addWidget(self.label_template_search_region, row=4, col=0)
        self.dk_control.addWidget(self.edit_template_search_region, row=4, col=1)
        self.dk_control.addWidget(self.btn_save_dockstn, row=4, col=2)
        self.dk_control.addWidget(self.btn_restore_dock, row=4, col=3)

        self.dk_control.addWidget(self.label_video, row=5, col=0)
        self.dk_control.addWidget(self.cb_video, row=5, col=1)
        self.dk_control.addWidget(self.btn_load_videos, row=5, col=2)
        self.cb_apply_template_search_to_video = QCheckBox('search template on video')
        self.dk_control.addWidget(self.cb_apply_template_search_to_video, row=5, col=3)


        self.dk_control.addWidget(self.frame_slider, row=6, col=0, colspan=2)
        self.dk_control.addWidget(self.btn_start_video, row=6, col=2)
        self.dk_control.addWidget(self.btn_stop_video, row=6, col=3)
        self.dk_control.addWidget(self.btn_fwd_one_frame_video, row=6, col=4)

        self.dk_control.addWidget(self.label_video_capture, row=7, col=0)
        self.dk_control.addWidget(self.cb_video_capture, row=7, col=1)
        self.dk_control.addWidget(self.btn_start_camera, row=7, col=2)
        self.dk_control.addWidget(self.btn_stop_camera, row=7, col=3)

        # self.current_frame  = 0
        # self.frame_slider.position(self.current_frame)
        # self.frame_update()

        self.show()

    def on_btn_search(self):
        # visualize = self.cb_visual.isChecked()
        self.template_matching(self.cb_template.currentText())

    def on_btn_start_video(self):
        # self.sim(calculate=False)
        self.fwd_one_frame = False
        self.play_video()

    def on_btn_start_camera(self):
        if self.start_streaming is False:
            self.start_streaming = True
            self.streaming(self.cb_video_capture.currentText())

    def on_btn_stop_video(self):
        self.start_streaming = False
        self.pause_video = False
        self.fwd_one_frame = False
        self.btn_fwd_one_frame_video.setEnabled(False)


    def on_btn_fwd_one_frame_video(self):
        if self.start_streaming is True:
            self.fwd_one_frame = True
            self.play_video()

    def on_btn_stop_camera(self):
        self.start_streaming = False

    def streaming(self, camera="0"):
        import cv2
        # from goprocam import GoProCamera
        # from goprocam import constants
        # cascPath = "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml"
        # faceCascade = cv2.CascadeClassifier(cascPath)
        print(f"camera is {camera}")
        if camera.isnumeric():
            cap = cv2.VideoCapture(int(camera))
        else:
            # gpCam = GoProCamera.GoPro()
            cap = cv2.VideoCapture(camera)
        cv2_version_major = int(cv2.__version__.split('.')[0])
        if cv2_version_major > 3:
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print("width:{}, height:{}".format(width, height))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        else:  # before 3.0
            width = cap.get(cv2.CV_CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CV_CAP_PROP_FRAME_HEIGHT)
            print("width:{}, height:{}".format(width, height))
            cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        apply_template_search = self.cb_apply_template_search_to_video.isChecked()

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
            assert ret, "cap.read fails"
            frames += 1
            self.image_item_page.setImage(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
            QtGui.QGuiApplication.processEvents()
            if time.time() > start + 10:
                print(f"{frames / (time.time() - start)} fp/s")
                start = time.time()
                frames = 0

            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            if apply_template_search is True:
                self.template_matching(self.cb_template.currentText())

        cap.release()
        cv2.destroyAllWindows()
        print(f"{frames / (time.time() - start)} fp/s")

    def sim(self, calculate=True):
        self.template_avg()
        # visualize = self.cb_visual.isChecked()
        # self.template_matching(self.cb_template.currentText())
        cap = cv2.VideoCapture(self.cb_video.currentText())
        if (cap.isOpened() is False):
            print("Error opening video stream or file")
        apply_template_search = self.cb_apply_template_search_to_video.isChecked()

        # Read until video is completed
        frames = 0
        start = time.clock()
        template = cv2.imread(self.cb_template.currentText())
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template_edge = cv2.Canny(template_gray, 50, 200)
        while (cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret is True:
                frames += 1
                # Display the resulting frame
                # cv2.imshow('Frame', frame)
                if calculate:
                    print(f"frame: {frames}")
                    self.multi_scale_template_matching(template_edge=template_edge, frame=frame, debug=False,
                                                       paint=False)
                else:
                    self.image_item_page.setImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # Press Q on keyboard to  exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
                if apply_template_search is True:
                    self.template_matching(self.cb_template.currentText())
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
            if self.pause_video is False:
                self.pause_video = True
                self.btn_fwd_one_frame_video.setEnabled(True)
                print(f"pause video")
                return
            elif self.fwd_one_frame is True:
                print(f"foward video one frame")
            else:
                # resume video
                self.pause_video = False
                self.btn_fwd_one_frame_video.setEnabled(False)
                print(f"resume video")
        else:
            self.start_streaming = True
            self.cap = cv2.VideoCapture(self.cb_video.currentText())
            if self.cv2_version_major >=3:
                fps = self.cap.get(cv2.CAP_PROP_FPS)
            else:
                # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
                fps = self.cap.get(cv2.CV_CAP_PROP_FPS)
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps

            if (self.cap.isOpened() is False):
                print("Error opening video stream or file")
            self.total_frames = self.cap.get(7)
            print(f"total frames: {self.total_frames}")
            self.current_frame = 0
            self.frame_slider.set_max(self.total_frames)
            self.frame_slider.position(self.current_frame)
            # self.frame_update()
        apply_template_search = self.cb_apply_template_search_to_video.isChecked()

        # Read until video is completed
        frames = 0
        apply_deskewed_screen = self.cb_apply_deskewed_screen.isChecked()
        if apply_deskewed_screen is True:
            self.PerspectiveTransform = None
        start = time.time()
        while self.cap.isOpened() and self.start_streaming is True and (self.pause_video is False or self.fwd_one_frame is True):
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            if ret is True:
                self.frame = frame
                frames += 1
                self.current_frame += 1
                self.frame_slider.position(self.current_frame)
                if apply_deskewed_screen:
                    self.on_btn_deskew()
                else:
                    self.image_item_page.setImage(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
                if apply_template_search is True:
                    self.template_matching(self.cb_template.currentText())
                # Press Q on keyboard to exit
                # if cv2.waitKey(25) & 0xFF == ord('q'):
                #     break
            # Break the loop
            else:
                # break
                print(f"warning: frames {self.current_frame} is bad")
                self.current_frame += 1
                self.pause_video = True # pause video on bad frame or last frame
                if self.current_frame >= self.total_frames:
                    break
            QtGui.QGuiApplication.processEvents()
            if time.time() > start + 10:
                print(f"{frames / (time.time() - start)} fp/s")
                start = time.time()
                frames = 0
            if self.fwd_one_frame is True:
                return
        print(f"{frames / (time.time() - start)} fp/s")
        if self.pause_video is False:
            # When everything done, release the video capture object
            self.cap.release()
            # Closes all the frames
            cv2.destroyAllWindows()
            self.start_streaming = False

    ''' refresh frame window,
     called when new frame needs to be painted,
     e.g. triggers by slider widget  '''

    def frame_update(self):
        a = self.frame_slider.x
        # print ("frame: {}".format(a))
        self.new_frame = int(a)
        # jump to current frame

    def run_all(self):
        # visualize = self.cb_visual.isChecked()
        for template in self.templates:
            self.template_matching(template)

    def on_change_rect_roi(self):
        # pic = Image.open(self.cb_page.currentText())
        # pix = np.array(pic.getdata()).reshape(pic.size[1], pic.size[0], 4)
        dim = [int(self.rect_roi.pos()[0]), int(self.rect_roi.pos()[1]),
               int(self.rect_roi.pos()[0] + self.rect_roi.size()[0]),
               int(self.rect_roi.pos()[1] + self.rect_roi.size()[1])]
        # b = np.average(pix[dim[1]:dim[3],dim[0]:dim[2], 0])
        # g = np.average(pix[dim[1]:dim[3],dim[0]:dim[2], 1])
        # r = np.average(pix[dim[1]:dim[3],dim[0]:dim[2], 2])
        # print(f"on_change_rect_roi dim: {dim}")
        if dim[0] < 0:
            dim[0] = 0
        if dim[1] < 0:
            dim[1] = 0

        if dim[2] >= self.frame.shape[1]:
            dim[2] = self.frame.shape[1] - 1
        if dim[0] >= dim[2]:
            dim[0] = dim[2] - 1
        if dim[3] >= self.frame.shape[0]:
            dim[3] = self.frame.shape[0] - 1
        if dim[1] >= dim[3]:
            dim[1] = dim[3] - 1
        # print(f"on_change_rect_roi dim: {dim}")
        b = int(np.average(self.frame[dim[1]:dim[3], dim[0]:dim[2], 0]))
        g = int(np.average(self.frame[dim[1]:dim[3], dim[0]:dim[2], 1]))
        r = int(np.average(self.frame[dim[1]:dim[3], dim[0]:dim[2], 2]))
        roi_rgb = (r, g, b)

        # print(f"ROI pic size {pic.size}")
        # print(f"ROI pix shape: {pix.shape}, ROI pix size: {pix.size}")
        delta = comp_rgb(self.template_rgb, roi_rgb)
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
        r = int(np.average(pix[:, :, 0]))
        g = int(np.average(pix[:, :, 1]))
        b = int(np.average(pix[:, :, 2]))
        self.template_rgb = (r, g, b)

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
        fnames = QFileDialog.getOpenFileNames(self, 'Load pages', './', "Image files (*.png *.jpg)")
        print(f"load page: {fnames}")
        if fnames[0] != '':
            for fname in fnames[0]:
                self.cb_page.addItem(fname)
                self.pages.append(fname)
            # upload pages listbox
            self.cb_page.setCurrentIndex(len(self.pages) - 1)

    def on_load_templates(self):
        fnames = QFileDialog.getOpenFileNames(self, 'Load templates', './', "Image files (*.png *.jpg)") #Images (*.png *.xpm .jpg);;Text files (.txt);;XML files (*.xml)
        print(f"load template: {fnames}")
        if fnames[0] != '':
            for fname in fnames[0]:
                self.cb_template.addItem(fname)
                self.templates.append(fname)
            self.cb_template.setCurrentIndex(len(self.templates) - 1)

    def on_video_capture_change(self):
        pass

    def on_btn_ocr_roi(self):
        assert self.frame is not None
        # im = Image.open(self.cb_page.currentText())
        region = Region(int(self.rect_roi.pos()[0]), int(self.rect_roi.pos()[1]),
                        int(self.rect_roi.pos()[0]) + int(self.rect_roi.size()[0]),
                        int(self.rect_roi.pos()[1]) + int(self.rect_roi.size()[1]))
        # region = im.crop(dim)
        start = time.time()
        text = ocr(self.frame, region)
        print(f"ocr roi pos: {region}, result: '{text}'")
        self.console.write(f"ocr roi pos: {region}, result: '{text}', spent: "
                           f"{((time.time() - start) * 1000):.3f} ms")

    def on_btn_save_roi(self):
        print("roi pos: {}".format(self.rect_roi.pos()))
        print("roi size: {}".format(self.rect_roi.size()))

        # im = Image.open(self.cb_page.currentText())
        cv2_im = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(cv2_im)
        # im.show()
        dim = (
            int(self.rect_roi.pos()[0]), int(self.rect_roi.pos()[1]), int(self.rect_roi.pos()[0] + self.rect_roi.size()[0]),
            int(self.rect_roi.pos()[1] + self.rect_roi.size()[1]))
        region = im.crop(dim)

        name = "roi" # ntpath.basename(self.cb_page.currentText()).rstrip(".png")
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

    def on_btn_denoise_screen(self):
        start = time.clock()
        blurring_type = self.cb_image_blurring.currentIndex()
        if blurring_type == 0:
            self.denoised_frame = cv2.blur(self.frame, (3, 3))
        elif blurring_type == 1:
            self.denoised_frame = cv2.blur(self.frame, (60, 60))
        elif blurring_type == 2:
            self.denoised_frame = cv2.GaussianBlur(self.frame, (3, 3), 3)
        elif blurring_type == 3:
            self.denoised_frame = cv2.GaussianBlur(self.frame, (15 * 3, 15 * 3), 0)
        elif blurring_type == 4:
            self.denoised_frame = cv2.medianBlur(self.frame, 3)
        elif blurring_type == 5:
            self.denoised_frame = cv2.medianBlur(self.frame, 50)
        elif blurring_type == 6:
            self.denoised_frame = cv2.bilateralFilter(self.frame, 9, sigmaColor=75, sigmaSpace=75)
        self.console.write(
            f"denoise with '{self.cb_image_blurring.currentText()}' spent: {((time.clock() - start) * 1000):.3f} ms\n")

        # elif blurring_type == 7:
        #     self.denoised_frame = cv2.bilateralFilter(self.frame, 9, 100, 100)
        self.image_item_page.setImage(cv2.cvtColor(self.denoised_frame, cv2.COLOR_BGR2RGB))
        self.frame = self.denoised_frame

    def on_btn_color_calibration_search(self):
        self.template_matching(self.cb_color_calibration_templates.currentText())

    def on_btn_color_calibration_search_all(self):
        pass

    def on_btn_default_threshold(self):
        self.edit_rgb_diff_threshold.setText(self.DEF_RGB_DIFFERENCE_THRESHOLD)
        self.edit_color_space_threshold.setText(self.DEF_COLOR_DISTANCE_THRESHOLD)

    def on_btn_search_corners(self):
        # blur = cv2.pyrMeanShiftFiltering(self.frame, 21, 51)
        # gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        # threshold1 = 8
        # threshold2 = 255
        # ret, threshold = cv2.threshold(gray, threshold1, threshold2, cv2.THRESH_BINARY)
        # self.image_item_page.setImage(cv2.cvtColor(threshold, cv2.COLOR_GRAY2RGB))
        # return
        # load the image and compute the ratio of the old height
        # to the new height, clone it, and resize it
        threshold = 8
        start = time.time()
        tl, tr, bl, br, width, height = search_corners(self.frame, threshold)
        image = self.frame.copy()  # cv2.imread('cards/red8.jpg')
        if tl is not None:
            self.console.write(f"search corners succeeds, ")
            # cv2.drawContours(image, [[tl],[tr],[bl],[br]], -1, (0, 255, 0), 2)
            cv2.line(image, tuple(tl), tuple(tr), (0, 255, 0), 2)
            cv2.line(image, tuple(tr), tuple(br), (0, 255, 0), 2)
            cv2.line(image, tuple(br), tuple(bl), (0, 255, 0), 2)
            cv2.line(image, tuple(bl), tuple(tl), (0, 255, 0), 2)
            self.image_item_page.setImage(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            self.edit_deskew_top_left.setText(f"{tl[0]}, {tl[1]}")
            self.edit_deskew_bot_right.setText(f"{br[0]},{br[1]}")

            self.edit_deskew_top_right.setText(f"{tr[0]},{tr[1]}")
            self.edit_deskew_bot_left.setText(f"{bl[0]},{bl[1]}")

            self.edit_deskew_dim.setText(f"{width},{height}")
        else:
            self.console.write(f"search corners fails!!! ")
        self.console.write(f"search conners spent: {((time.clock() - start) * 1000):.3f} ms\n ")

    def on_btn_deskew(self):
        img = self.frame
        start = time.time()
        if self.PerspectiveTransform is None:
            rows, cols, ch = img.shape
            top_left = list(map(int, self.edit_deskew_top_left.text().split(',')))
            top_right = list(map(int, self.edit_deskew_top_right.text().split(',')))
            bot_left = list(map(int, self.edit_deskew_bot_left.text().split(',')))
            bot_right = list(map(int, self.edit_deskew_bot_right.text().split(',')))
            pts1 = np.float32([top_left, top_right, bot_left, bot_right])
            width, height = list(map(int, self.edit_deskew_dim.text().split(',')))
            pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
            self.PerspectiveTransform  = init_deskew(pts1, pts2)  # cv2.getPerspectiveTransform(pts1, pts2)
        self.deskewed_frame = run_deskew(img, self.PerspectiveTransform) # cv2.warpPerspective(img, self.PerspectiveTransform, (width, height))
        self.image_item_page.setImage(cv2.cvtColor(self.deskewed_frame, cv2.COLOR_BGR2RGB))
        self.frame = self.deskewed_frame
        # print(f"deskew spent {(time.time() - start)* 1000} ms")


    def on_btn_scale(self):
        img = self.frame
        (width, height) = list(map(int, self.edit_scale_dim.text().split(',')))

        self.scaled_frame = cv2.resize(img, (width, height))
        self.image_item_page.setImage(cv2.cvtColor(self.scaled_frame, cv2.COLOR_BGR2RGB))
        self.frame = self.scaled_frame

    def on_btn_save_scaled_screen(self):
        basename = ntpath.basename(self.cb_page.currentText()).rstrip(".png")
        scale_dim = list(map(int, self.edit_scale_dim.text().split(',')))
        name = "{}_scaled_{}x{}.png".format(basename, scale_dim[0], scale_dim[1])
        cv2.imwrite(name, self.scaled_frame)
        self.console.write(f"scaled screen saved as: {name}  \n")

    def on_btn_save_frame(self):
        name = f"_frame_{time.time()}.png"
        cv2.imwrite(name, self.frame)
        self.console.write(f"frame saved as: {name}  \n")

    def on_btn_save_denoised_screen(self):
        denoise_type = self.cb_image_blurring.currentText()
        basename = ntpath.basename(self.cb_page.currentText()).rstrip(".png")
        name = "{}_denoised_{}.png".format(basename, denoise_type)
        cv2.imwrite(name, self.denoised_frame)
        self.console.write(f"denoised screen saved as: {name}  \n")

    def on_btn_save_deskewed_screen(self):
        width, height = list(map(int, self.edit_deskew_dim.text().split(',')))
        print(f"{self.cb_page.currentText()}")
        print(f"{self.cb_page.currentText().rstrip('.png')}")
        basename = ntpath.basename(self.cb_page.currentText()).rstrip(".png")
        name = "{}_deskewed_{}x{}.png".format(basename, width, height)
        cv2.imwrite(name, self.deskewed_frame)
        self.console.write(f"deskewed screen saved as: {name}  \n")

    def multi_scale_template_matching(self, template_file=None, template_edge=None, frame=None, debug=True, paint=True):
        if template_edge is None:
            template = cv2.imread(template_file)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            template_edge = cv2.Canny(template_gray, 50, 200)
        (tH, tW) = template_edge.shape[:2]
        visual = True
        if paint and visual:
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
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # check to see if the iteration should be visualized
            if paint and visual is True:
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
            print(f"image size: {image.size}")
            print(f"image shape: {image.shape}")
            print(f"startX: {startX}, endX: {endX}, startY: {startY}, endY: {endY}")
            # cv2 use BGR order ! y-X axis
            b = int(np.average(image[startY:endY, startX:endX, 0]))
            g = int(np.average(image[startY:endY, startX:endX, 1]))
            r = int(np.average(image[startY:endY, startX:endX, 2]))
            self.console.write(f"color avg RGB: {r}, {g}, {b}\n")
            print(f"color avg RGB: {r}, {g}, {b}\n")

        if paint is True:
            # draw a bounding box around the detected result and display the image
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 10)

            self.image_item_page.setImage(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if visual:
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
        r = int(np.average(pix[startY:endY, startX:endX, 0]))
        g = int(np.average(pix[startY:endY, startX:endX, 1]))
        b = int(np.average(pix[startY:endY, startX:endX, 2]))

        self.console.write(f"color avg RGB: {r}, {g}, {b}\n")
        if debug:
            print(f"color avg RGB: {r}, {g}, {b}\n")

    def template_matching(self, template_file=None, frame=None, threshold=None, paint=True):
        if threshold is None:
            threshold = self.DEF_TEMP_MATCH_THRESHOLD
        COLOR_DISTANCE_THRESHOLD = float(self.edit_color_space_threshold.text())
        RGB_DIFFERENCE_THRESHOLD = int(self.edit_rgb_diff_threshold.text())
        search_region = list(map(int, self.edit_template_search_region.text().split(',')))
        # swap row and col
        # search_region[0], search_region[1], search_region[2], search_region[3], = search_region[1], search_region[0], \
        #                                                                           search_region[3], search_region[2]
        start = time.time()
        if frame is not None:
            # img = frame
            img = frame.copy()
        else:
            img = self.frame.copy()

        # handle default region
        if search_region[0] < 0:
            search_region[0] = 0
        if search_region[1] < 0:
            search_region[1] = 0
        if search_region[2] < 0:
            search_region[2] = img.shape[1]
        if search_region[3] < 0:
            search_region[3] = img.shape[0]
        if search_region[2] - search_region[0] > img.shape[1]:
            self.console.output(f"template search region: {search_region} > image size: {img.shape}\n")
            search_region[2] = img.shape[1]
        if search_region[3]  - search_region[1] > img.shape[0]:
            self.console.output(f"template search region: {search_region} > image size: {img.shape}\n")
            search_region[3] = img.shape[0]
        method = eval(self.cb_template_search_methods.currentText())
        template = cv2.imread(template_file)
        h, w, d = template.shape[::]
        if search_region[2] - search_region[0] < template.shape[1] or search_region[3] - search_region[1] < \
                template.shape[0]:
            self.console.write(f"error: search region < template size")
            print(f"error: search region < template size")
            return

        if self.cb_try_diff_temp_search_if_fail.isChecked() is True:
            match_method = -1
        else:
            match_method = method
        match_result = match(img, template, Region(search_region[0], search_region[1], search_region[2], search_region[3]), match_parameter=(match_method, threshold,
                                                                            COLOR_DISTANCE_THRESHOLD,
                                                                            RGB_DIFFERENCE_THRESHOLD))
        end = time.time()
        if match_result is None:
            pass
        else:
            print(f"match_result(found, method, region, result, color):\n"
                  f"{match_result[0]}, {match_result[4]},  ({match_result[1]}), {match_result[2]:.2f}, "
                  f"({match_result[3][0]:.2f}, {match_result[3][1]:.2f}, {match_result[3][2]:.2f}, "
                  f"{match_result[3][3]:.2f})")
            self.console.write(f"match_result(found, method, region, result, color):\n"
                  f"{match_result[0]}, {match_result[4]},  ({match_result[1]}), {match_result[2]:.2f}, "
                  f"({match_result[3][0]:.2f}, {match_result[3][1]:.2f}, {match_result[3][2]:.2f}, "
                  f"{match_result[3][3]:.2f})")
        if match_result is not None:
            if match_result[0] is True:
                if paint is True:
                    # draw a bounding box around the detected result and display the image
                    cv2.rectangle(img, (match_result[1].x, match_result[1].y), (match_result[1].right, match_result[1].bottom), (0, 128, 0), 5)
            else:
                if paint is True:
                    if match_result[2] < threshold:
                        # draw a bounding box around the detected result and display the image
                        cv2.rectangle(img, (match_result[1].x, match_result[1].y), (match_result[1].right, match_result[1].bottom),  (0, 0, 128), 5)
                    else:
                        if match_result[3][0] > COLOR_DISTANCE_THRESHOLD:
                            # draw a bounding box around the detected result and display the image
                            cv2.rectangle(img, (match_result[1].x, match_result[1].y), (match_result[1].right, match_result[1].bottom), (0, 0, 128), 5)
                        elif sum(match_result[3][1:]) > RGB_DIFFERENCE_THRESHOLD:
                            # draw a bounding box around the detected result and display the image
                            cv2.rectangle(img, (match_result[1].x, match_result[1].y), (match_result[1].right, match_result[1].bottom), (0, 0, 128), 5)

        if paint is True:
            self.image_item_page.setImage(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            QtGui.QGuiApplication.processEvents()
        print(f"match spent {(end - start) * 1000} ms")
        self.console.write(f", match spent {(end - start) * 1000} ms\n")
        return

    def on_btn_rc_alloc(self):
        url = self.edit_rc_remote_camera_url.text()
        self.remote_camera.allocate_camera(url)

    def on_btn_rc_free(self):
        self.remote_camera.free_camera()

    def on_btn_rc_current_frame(self):
        self.remote_camera._frame(self.DEF_RC_FRAME_PATH)
        img_bgr = asarray(cv2.imread(self.DEF_RC_FRAME_PATH))
        self.image_item_page.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        self.frame = img_bgr

    def on_btn_rc_get_frame(self):
        self.remote_camera.get_frame(self.DEF_RC_FRAME_PATH)
        img_bgr = asarray(cv2.imread(self.DEF_RC_FRAME_PATH))
        self.image_item_page.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        self.frame = img_bgr

    def on_btn_rc_start_video(self):
        if self.start_rc_streaming is True:
            print("remote camera video is already started")
            return
        port = self.edit_rc_stream_port.text()
        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)
        url = ip_addr + f':{port}'
        assert 200 == self.remote_camera.start_live(address=url, timestamp=self.cb_add_timestamp.isChecked(), frame_rate=self.edit_rc_stream_rate.text())
        time.sleep(5)
        self.cap = cv2.VideoCapture("udp://" +  url)
        if (self.cap.isOpened() is False):
            print("Error: opening video stream or file")
            self.console.write("Error: opening video stream or file")
            self.on_btn_rc_stop_video()
            return
        else:
            print("Success: opening video stream or file")
            self.console.write("Success: opening video stream or file")
        apply_deskewed_screen = self.cb_apply_deskewed_screen.isChecked()
        if apply_deskewed_screen is True:
            self.PerspectiveTransform = None
        start = time.time()
        frames = 0
        self.start_rc_streaming = True

        while self.start_rc_streaming is True:
            ret, self.frame = self.cap.read()
            if ret is True:
                frames += 1
                if apply_deskewed_screen:
                    self.on_btn_deskew()
                else:
                    self.image_item_page.setImage(cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB))
            # Break the loop
            else:
                debug("Error: reading video stream or file")
                self.console.write("Error: reading video stream or file")
                break
            QtGui.QGuiApplication.processEvents()
            if time.time() > start + 10:
                print(f"{frames / (time.time() - start)} fp/s")
                start = time.time()
                frames = 0
        if self.start_rc_streaming is True:
            debug("error: fail to open cap")
            self.on_btn_rc_stop_video()
        print(f"{frames / (time.time() - start)} fp/s")


    def on_btn_rc_stop_video(self):
        assert 200 == self.remote_camera.stop_live()
        self.start_rc_streaming = False


class Slider(QWidget):
    def __init__(self, minimum, maximum, orientation=Qt.Horizontal, parent=None):
        super(Slider, self).__init__(parent=parent)

        self.label = QLabel(self)
        self.horizontalLayout = QHBoxLayout(self)
        self.slider = QSlider(self)
        self.slider.setOrientation(orientation)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.horizontalLayout.addWidget(self.slider)
        self.horizontalLayout.addWidget(self.label)
        self.resize(self.sizeHint())

        self.slider.setTickInterval(maximum)
        self.slider.setSingleStep(1)
        self.slider.setMaximum(maximum)
        self.slider.setMinimum(minimum)
        self.minimum = minimum
        self.maximum = maximum
        self.orientatioin = orientation
        self.slider.valueChanged.connect(self.set_label_value)
        self.x = None
        self.set_label_value(self.slider.value())

    def position(self, pos):
        self.slider.setSliderPosition(pos)

    def set_max(self, maximum):
        self.slider.setMaximum(maximum)

    def set_label_value(self, value):
        if (self.slider.maximum() == self.slider.minimum()):
            self.x = 0.0
        else:
            self.x = self.minimum + (float(value) / (self.slider.maximum() - self.slider.minimum())) * (
                    self.maximum - self.minimum)
        self.x = int(self.x)
        # self.label.setText("frame: {0:.4g}".format(self.x))
        self.label.setText(f"no.:{value}/{self.x}%")
        # print ("set_label_value({}, frame x:{}/{}".format(value, self.x))


# Start Qt event loop unless running in interactive mode or using pyside.
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

    if page_file is None and template_file is None:
        print("warning:  page/template file(s) not found")
        usage()
        sys.exit(2)

    try:
        pages = []
        if page_file is not None:
            with open(page_file, "rt") as f:
                for line in f:
                    line = line.rstrip("\n")
                    line = line.rstrip()
                    if line == "" or line[0] == '#':
                        continue
                    print("read {}".format(line))
                    pages += glob.glob(line)
    except Exception as e:
        debug("error: fail to open {}. {} ".format(page_file, e))
        exit(2)
    if page_file is not None and len(pages) == 0:
        print("error: no page found in {}".format(page_file))
        exit(2)
    try:
        templates = []
        if template_file is not None:
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
    if template_file is not None and len(templates) == 0:
        print("error: no template found in {}".format(template_file))
        exit(2)

    # settings_file = "./settings.json"
    # with open(settings_file) as f:
    #     data = json.load(f)

    # print(f"device id: {data['device_id']}, user email:{data['user_email']}, user password:{data['user_password']} ")
    # for page, value in data["pages"].items():
    #     print(f"{page}:{value}")

    app = QtGui.QApplication([])

    view = CalibrationView(pages=pages, templates=templates,
                           title="Roku Screen Capture calibration ver.{}. All rights reserved.".format(VERSION),
                           verbose=verbose)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
