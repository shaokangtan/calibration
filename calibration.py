import sys
import cv2
import pyqtgraph as pg
from numpy import asarray
from pyqtgraph.dockarea import *
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.Qt import *
import pyqtgraph.console
import numpy as np
import imutils
import getopt
import glob



import time

VERSION = "0.0.1"


class CalibrationView(QMainWindow):
    def __init__(self, pages, templates, parent=None, title=None, verbose=False):
        super(QMainWindow, self).__init__(parent)
        if len(pages) == 0 or len(templates) == 0:
            print("error: no pages/templates loaded")
            return None
        self.pages = pages
        self.templates = templates
        self.verbose = verbose
        self.area = DockArea()
        self.setCentralWidget(self.area)
        self.resize(1280, 900)
        self.setWindowTitle(title)

        ## Create docks, place them into the window one at a time.
        ## Note that size arguments are only a suggestion; docks will still have to
        ## fill the entire dock self.area and obey the limits of their internal widgets.
        self.dk_page = Dock("page", size=(1024, 720))  ## give this dock the minimum possible size
        self.dk_template = Dock("template", size=(280, 280))
        self.dk_info = Dock("info", size=(280, 280))
        self.dk_control = Dock("command", size=(280, 280))

        self.area.addDock(self.dk_page, 'right')
        self.area.addDock(self.dk_template, 'bottom', self.dk_page)
        self.area.addDock(self.dk_info, 'right', self.dk_template)
        self.area.addDock(self.dk_control, 'right', self.dk_info)

        # self.widget_frame = pg.PlotWidget()
        # self.widget_frame.setAspectLocked("xy")
        # self.dk_page.addWidget(self.widget_frame)
        # img_rgb = asarray(cv2.imread(pages[0]))
        # self.image = pg.ImageItem(img_rgb, axisOrder='row-major')
        #
        # self.widget_frame.addItem(self.image )
        # self.image.getViewBox().invertY(True)
        # self.widget_frame.removeItem(self.image )
        # self.widget_frame.addItem(self.image)

        # page
        img_rgb = asarray(cv2.imread(pages[0]))
        self.image_item_page = pg.ImageItem(img_rgb, axisOrder='row-major')
        self.image_view = pg.ImageView(imageItem=self.image_item_page)
        self.dk_page.addWidget(self.image_view)
        # template
        img_rgb = asarray(cv2.imread(templates[0]))
        self.image_item_template = pg.ImageItem(img_rgb, axisOrder='row-major')
        self.image_view = pg.ImageView(imageItem=self.image_item_template)
        self.dk_template.addWidget(self.image_view)
        # info
        self.widget_info = pg.LayoutWidget()
        self.label_info = QLabel("""Frame meta data""")
        self.label_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.scroll_area = QScrollArea(parent)
        self.scroll_area.setWidget(self.label_info)
        self.scroll_area.setWidgetResizable(True)
        self.dk_info.addWidget(self.scroll_area, row=0, col=0)

        # control
        self.label_page = QLabel("Page:")
        self.cb_page = QComboBox()
        for page in self.pages:
            self.cb_page.addItem(page)
        self.cb_page.currentIndexChanged.connect(self.page_change)

        self.label_template = QLabel("Template:")
        self.cb_template = QComboBox()
        for template in self.templates:
            self.cb_template.addItem(template)
        self.cb_template.currentIndexChanged.connect(self.template_change)

        self.btn_save_dockstn = QPushButton('Save dock state')
        self.btn_restore_dock = QPushButton('Restore dock state')
        self.btn_restore_dock.setEnabled(False)
        self.btn_save_dockstn.clicked.connect(self.save)
        self.btn_restore_dock.clicked.connect(self.load)

        self.btn_run = QPushButton('Run')
        self.btn_run_all = QPushButton('Run all')
        self.btn_run.clicked.connect(self.run)

        self.cb_visual = QCheckBox('Visual', self)
        self.cb_export = QCheckBox('Export', self)

        self.dk_control.addWidget(self.label_page, row=0, col=0)
        self.dk_control.addWidget(self.cb_page, row=0, col=1, colspan=16)
        self.dk_control.addWidget(self.label_template, row=1, col=0)
        self.dk_control.addWidget(self.cb_template, row=1, col=1, colspan=16)

        self.dk_control.addWidget(self.btn_run, row=2, col=0)
        self.dk_control.addWidget(self.btn_run_all, row=2, col=1)

        self.dk_control.addWidget(self.btn_save_dockstn, row=2, col=2)
        self.dk_control.addWidget(self.btn_restore_dock, row=2, col=3)
        self.dk_control.addWidget(self.cb_visual, row=3, col=0)
        self.dk_control.addWidget(self.cb_export, row=3, col=1)

        self.show()

    def run(self):
        multi_scale_template_matching(self.image_item_page, self.image_item_template, self.cb_page.currentText(), self.cb_template.currentText(), True)

    def save(self):
        self.state = self.area.saveState()
        self.btn_restore_dock.setEnabled(True)

    def load(self):
        self.area.restoreState(self.state)

    def template_change(self, i):
        img_rgb = asarray(cv2.imread(self.templates[i]))
        self.image_item_template.setImage(img_rgb)

    def page_change(self, i):
        img_rgb = asarray(cv2.imread(self.pages[i]))
        self.image_item_page.setImage(img_rgb)

def multi_scale_template_matching(image_item_page, image_tiem_template, page_file, template_file, visual=False):
    template = cv2.imread(template_file)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template_edge = cv2.Canny(template_gray, 50, 200)
    (tH, tW) = template_edge.shape[:2]
    image_tiem_template.setImage(template_edge)
    # page = cv2.imread(page)
    # image_item_page.setImage(page)

    # load the image, convert it to grayscale, and initialize the
    # bookkeeping variable to keep track of the matched region
    image = cv2.imread(page_file)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found = None

    # loop over the scales of the image
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
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
        if visual is True:
            # draw a bounding box around the detected region
            clone = np.dstack([edged, edged, edged])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                          (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            image_item_page.setImage(clone)
            print("=== visual ===")
            # cv2.waitKey(0)

        # if we have found a new maximum correlation value, then update
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
            print("image: {}, scale:{}, found: {}".format(page_file, scale, found))


    # unpack the bookkeeping variable and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
    print("image: {}, found: {}".format(page_file, found))

    # draw a bounding box around the detected result and display the image
    cv2.rectangle(image, (startX, startY), (endX, endY), (255, 0, 0), 4)

    image_item_page.setImage(image)
    image_tiem_template.setImage(template)


    # cv2.namedWindow("Image", CV_WINDOW_NORMAL)
    #cv2.waitKey(0)




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

    app = QtGui.QApplication([])

    view = CalibrationView(pages= pages, templates=templates, title="Vudu Screen Capture calibration ver.{}. All rights reserved.".format(VERSION),
                     verbose=verbose)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()



