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



import time

VERSION = "0.0.1"


class CalibrationView(QMainWindow):
    def __init__(self, pages, templates, parent=None, title=None, verbose=False):
        super(QMainWindow, self).__init__(parent)
        if len(pages) == 0 or len(templates) == 0:
            print("error: no pages/templates loaded")
            return None
        self.videos = []
        self.pages = list(pages)
        self.templates = list(templates)
        self.verbose = verbose
        self.area = DockArea()
        self.setCentralWidget(self.area)
        self.resize(1024, 900)
        self.setWindowTitle(title)

        ## Create docks, place them into the window one at a time.
        ## Note that size arguments are only a suggestion; docks will still have to
        ## fill the entire dock self.area and obey the limits of their internal widgets.
        self.dk_page = Dock("page", size=(1024, 720))  ## give this dock the minimum possible size
        self.dk_template = Dock("template", size=(200, 280))
        self.dk_control = Dock("command", size=(200, 280))
        self.dk_info = Dock("info", size=(800, 280))

        self.area.addDock(self.dk_page, 'right')
        self.area.addDock(self.dk_template, 'bottom', self.dk_page)
        self.area.addDock(self.dk_control, 'right', self.dk_template)
        self.area.addDock(self.dk_info, 'right', self.dk_control)

        # page
        img_bgr = asarray(cv2.imread(pages[0]))
        self.image_item_page = pg.ImageItem(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), axisOrder='row-major')
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
        self.image_view = pg.ImageView(imageItem=self.image_item_template)
        self.dk_template.addWidget(self.image_view)

        # info
        self.widget_info = pg.LayoutWidget()
        self.console = ConsoleWidget()
        self.dk_info.addWidget(self.console)

        # control
        self.label_video = QLabel("Video:")
        self.cb_video = QComboBox()
        self.cb_video.currentIndexChanged.connect(self.video_change)

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

        self.btn_load_videos = QPushButton('Load videos...')
        self.btn_load_videos.clicked.connect(self.on_load_videos)
        self.btn_load_pages = QPushButton('Load pages...')
        self.btn_load_pages.clicked.connect(self.on_load_pages)
        self.btn_load_templates = QPushButton('Load templates...')
        self.btn_load_templates.clicked.connect(self.on_load_templates)

        self.btn_play_video = QPushButton('play video')
        self.btn_sim = QPushButton('Run video')
        self.btn_run = QPushButton('Run Page')
        self.btn_run_all = QPushButton('Run all templates')
        self.btn_play_video.clicked.connect(self.play_video)
        self.btn_sim.clicked.connect(self.sim)
        self.btn_run.clicked.connect(self.run)
        self.btn_run_all.clicked.connect(self.run_all)
        self.btn_export_roi = QPushButton('Save ROI')
        self.btn_export_roi.clicked.connect(self.on_export_rect_roi)

        self.cb_visual = QCheckBox('Visual', self)
        self.cb_export = QCheckBox('Export', self)

        self.dk_control.addWidget(self.label_page, row=0, col=0)
        self.dk_control.addWidget(self.cb_page, row=0, col=1, colspan=2)
        self.dk_control.addWidget(self.btn_load_pages, row=0, col=3)
        self.dk_control.addWidget(self.label_template, row=1, col=0)
        self.dk_control.addWidget(self.cb_template, row=1, col=1, colspan=2)
        self.dk_control.addWidget(self.btn_load_templates, row=1, col=3)

        self.dk_control.addWidget(self.btn_run, row=2, col=0)
        self.dk_control.addWidget(self.btn_run_all, row=2, col=1)
        self.dk_control.addWidget(self.btn_export_roi, row=2, col=2)
        self.dk_control.addWidget(self.cb_visual, row=3, col=0)
        self.dk_control.addWidget(self.cb_export, row=3, col=1)
        self.dk_control.addWidget(self.btn_save_dockstn, row=3, col=2)
        self.dk_control.addWidget(self.btn_restore_dock, row=3, col=3)

        self.dk_control.addWidget(self.label_video, row=4, col=0)
        self.dk_control.addWidget(self.cb_video, row=4, col=1, colspan=2)
        self.dk_control.addWidget(self.btn_load_videos, row=4, col=3)
        self.dk_control.addWidget(self.btn_play_video, row=5, col=0)
        self.dk_control.addWidget(self.btn_sim, row=5, col=1)


        self.show()

    def run(self):
        self.template_avg()
        visualize = self.cb_visual.isChecked()
        self.multi_scale_template_matching(self.cb_template.currentText(), debug=False)

    def play_video(self):
        self.sim(calculate=False)

    def sim(self, calculate=True):
        self.template_avg()
        visualize = self.cb_visual.isChecked()
        # self.multi_scale_template_matching(self.cb_template.currentText())
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


    def run_all(self):
        visualize = self.cb_visual.isChecked()
        for template in self.templates:
            self.multi_scale_template_matching( template)

    def on_change_rect_roi(self):
        pass

    def template_avg(self):
        pic = Image.open(self.cb_template.currentText())
        pix = np.array(pic.getdata()).reshape(pic.size[1], pic.size[0], 4)
        r = np.average(pix[:,:,0])
        g = np.average(pix[:,:,1])
        b = np.average(pix[:,:,2])

        print(f"pic size {pic.size}")
        print(f"pix shape: {pix.shape}, pix size: {pix.size}")
        print(f"Template color avg BGR: {r}, {g}, {b}")
        self.console.write(f"template color avg BGR: {r}, {g}, {b}\n")

    def on_load_videos(self):
        fnames = QFileDialog.getOpenFileNames(self, '=Load videos', './', "Video files (*.mov)")
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


    def on_load_templates(self):
        fnames = QFileDialog.getOpenFileNames(self, '=Load templates','./', "Image files (*.png)")
        print(f"load template: {fnames}")
        if fnames[0] !=  '':
            for fname in fnames[0]:
                self.cb_template.addItem(fname)
                self.templates.append(fname)


    def on_export_rect_roi(self):
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
        self.console.write("ROI image: {} is created \n".format(name))

    def save(self):
        self.state = self.area.saveState()
        self.btn_restore_dock.setEnabled(True)

    def load(self):
        self.area.restoreState(self.state)

    def template_change(self, i):
        img_bgr = asarray(cv2.imread(self.templates[i]))
        self.image_item_template.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

    def page_change(self, i):
        img_bgr = asarray(cv2.imread(self.pages[i]))
        self.image_item_page.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))


    def video_change(self, i):
        pass
        # img_bgr = asarray(cv2.imread(self.videos[i]))
        # self.image_item_page.setImage(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))

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
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
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
                self.console.write("{}: scale:{}, found: {}\n".format(page_file, scale, self.found))


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
            b = np.average(image[startY:endY,startX:endX,0])
            g = np.average(image[startY:endY,startX:endX,1])
            r = np.average(image[startY:endY,startX:endX,2])
            self.console.write(f"color avg BGR: {r}, {g}, {b}\n")
            print(f"color avg BGR: {r}, {g}, {b}\n")

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
        # self.console.write(f"color avg BGR: {r}, {g}, {b}\n")
        # print(f"color avg BGR: {r}, {g}, {b}\n")
        r = np.average(pix[startY:endY,startX:endX,0])
        g = np.average(pix[startY:endY,startX:endX,1])
        b = np.average(pix[startY:endY,startX:endX,2])

        self.console.write(f"color avg BGR: {r}, {g}, {b}\n")
        if debug:
            print(f"color avg BGR: {r}, {g}, {b}\n")

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



