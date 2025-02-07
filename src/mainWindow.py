# :author: Alexander Berno
"""Main Window"""

import axeap.core as core
import sys

from axeap.core.roi import HROI
import pathlib
import numpy as np

from LoadingBarWindow import LoadingBarWindow
from ApproxWindow import ApproxWindow
from ErrorWindow import ErrorWindow
from XESWindow import XESWindow
from RXESWindow import RXESWindow
from calibFunctions import approximateROIs, getCoordsFromScans, calcEnergyMap
from CalibFileClass import CalibFile
from SettingsWindow import SettingsWindow
from FileLoad import LoadTiffCalib, LoadInfoData, LoadH5Data
from ExitDialogWindow import exitDialog

from PyQt6 import QtCore, QtWidgets, QtGui
import pyqtgraph as pg

# ignores numpy warnings and errors (e.g. dividing by 0)
np.seterr(all="ignore")

# Alignment flags are used to place items in a window.
AlignFlag = QtCore.Qt.AlignmentFlag

# default directory for file selection menus (Desktop)
desktop_directory = str(pathlib.Path.home() / "Desktop")


# Main window
class MainWindow(QtWidgets.QMainWindow):
    """Main Window for application. Allows the viewing of data."""

    def __init__(self, *args, **kwargs):
        """initializes the main window"""
        super(MainWindow, self).__init__(*args, **kwargs)

        # Defaults
        self.sel_x1 = None
        self.sel_y1 = None
        self.sel_x2 = None
        self.sel_y2 = None
        self.sel_ax = None
        self.sel_rect = [None, []]
        self.rects = []
        self.drawn_calib = False
        self.left_button = False
        self.ax = None
        self.childWindow = None
        self.info_file = None
        self.emap_img = None
        self.calib_grid_scroll = None
        self.points = []
        self.spots = []

        # get settings from settings file, or load defaults
        settings = self.getSettings()
        if settings is None:
            settings = self.getDefaultSettings()

        SettingsWindow.saveSettings(None, settings)

        self.load_data_type = settings["data_load_type"]
        conf = settings["confirm_on_close"]
        if conf == "False" or not conf:
            self.confirm_on_close = False
        else:
            self.confirm_on_close = True

        self.setWindowTitle("pyAXEAP1")
        self.setFixedSize(960, 574)

        # Main scatter plot grid
        self.sc = pg.plot()
        self.sc.setBackground("w")
        self.ax = pg.ScatterPlotItem()
        self.sc.addItem(self.ax)

        # mouse movement label
        self.mouse_label = QtWidgets.QLabel()

        # mouse movement detector (for main graph)
        def mouseMoved(evt):
            pos = evt
            if self.sc.sceneRect().contains(pos):
                mouse_point = self.sc.plotItem.vb.mapSceneToView(pos)
                x = round(mouse_point.x(), 1)
                y = round(mouse_point.y(), 1)
                self.mouse_label.setText(f"x: {str(x)}, y: {str(y)}")

        self.sc.scene().sigMouseMoved.connect(mouseMoved)

        # button for opening calibration data
        cali_button = QtWidgets.QPushButton("Import Images...")
        cali_button.setFixedSize(120, 30)
        cali_button.clicked.connect(self.openPath)

        # button for opening XES menu
        xes_button = QtWidgets.QPushButton("XES")
        xes_button.clicked.connect(self.runXES)
        xes_button.setFixedSize(120, 30)

        # button for opening RXES menu
        rxes_button = QtWidgets.QPushButton("RXES")
        rxes_button.clicked.connect(self.runRXES)
        rxes_button.setFixedSize(120, 30)

        # button for loading an existing energy map
        emap_load_button = QtWidgets.QPushButton("Load Energy Map...")
        emap_load_button.setFixedSize(120, 30)
        emap_load_button.clicked.connect(self.loadEmap)

        # settings button
        self.set_button = QtWidgets.QPushButton("Settings")
        self.set_button.clicked.connect(lambda: self.openSettings(settings))
        self.set_button.setFixedSize(120, 30)

        # energy map buttons
        emap_area = QtWidgets.QScrollArea()
        emap_area.setFixedSize(286, 170)
        emap_widget = QtWidgets.QWidget()
        emap_grid = QtWidgets.QGridLayout(emap_widget)

        # minimum and maximum cut boxes and labels
        mincuts_label = QtWidgets.QLabel("Minimum Cuts")
        self.mincuts = QtWidgets.QSpinBox()
        self.mincuts.setMinimumSize(128, 20)
        self.mincuts.setMaximum(10000000)
        self.mincuts.setValue(int(settings["default_min_cuts"]))
        maxcuts_label = QtWidgets.QLabel("Maximum cuts")
        self.maxcuts = QtWidgets.QSpinBox()
        self.maxcuts.setMinimumSize(128, 20)
        self.maxcuts.setMaximum(10000000)
        self.maxcuts.setValue(int(settings["default_max_cuts"]))

        # Refresh (reload) button
        self.reload_calib = QtWidgets.QPushButton("Refresh")
        self.reload_calib.clicked.connect(lambda: self.getCalibPoints(False))
        self.reload_calib.setDisabled(True)

        # Set ROIs button
        self.approx_rois = QtWidgets.QPushButton("Set ROIs Automatically")
        self.approx_rois.setDisabled(True)
        self.approx_rois.clicked.connect(self.approxROIs)

        # Load info file button
        self.load_info_file_button = QtWidgets.QPushButton("Load Information File")
        self.load_info_file_button.setDisabled(True)
        self.load_info_file_button.clicked.connect(self.loadInfoFile)

        # calibrate button
        self.emap_calc_button = QtWidgets.QPushButton("Caibrate")
        self.emap_calc_button.clicked.connect(self.calcEmap)
        self.emap_calc_button.setDisabled(True)

        # save energy map button
        self.emap_save_button = QtWidgets.QPushButton("Save Energy Map As...")
        self.emap_save_button.clicked.connect(self.saveEmap)
        self.emap_save_button.setDisabled(True)

        # Add ROIs button
        self.add_roi = QtWidgets.QPushButton("Add ROI")
        self.add_roi.setDisabled(True)
        self.add_roi.clicked.connect(self.manualAddROI)

        # energy map grid layout connections (adding buttons etc.)
        emap_grid.addWidget(mincuts_label, 0, 0)
        emap_grid.addWidget(self.mincuts, 0, 1)
        emap_grid.addWidget(maxcuts_label, 1, 0)
        emap_grid.addWidget(self.maxcuts, 1, 1)
        emap_grid.addWidget(self.load_info_file_button, 2, 0)
        emap_grid.addWidget(self.reload_calib, 2, 1)
        emap_grid.addWidget(self.approx_rois, 3, 0)
        emap_grid.addWidget(self.add_roi, 3, 1)
        emap_grid.addWidget(self.emap_calc_button, 4, 0)
        emap_grid.addWidget(self.emap_save_button, 4, 1)
        emap_area.setWidget(emap_widget)

        # main "widget"; basically everything that is within the main window
        mwidget = QtWidgets.QWidget()

        # connects everything to the window with grid organization
        self.mlayout = QtWidgets.QGridLayout(mwidget)
        self.mlayout.addWidget(cali_button, 0, 0, AlignFlag.AlignCenter)
        self.mlayout.addWidget(emap_load_button, 0, 1, AlignFlag.AlignCenter)
        self.mlayout.addWidget(xes_button, 1, 0, AlignFlag.AlignCenter)
        self.mlayout.addWidget(rxes_button, 1, 1, AlignFlag.AlignCenter)
        self.mlayout.addWidget(self.set_button, 1, 2, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.mouse_label, 1, 2, AlignFlag.AlignRight)
        self.mlayout.addWidget(
            emap_area, 2, 0, 1, 2, AlignFlag.AlignLeft | AlignFlag.AlignTop
        )
        self.mlayout.addWidget(self.sc, 2, 2, 2, 1, AlignFlag.AlignCenter)
        self.mlayout.setColumnMinimumWidth(2, 500)

        # shows the menu
        self.setCentralWidget(mwidget)
        self.show()

    # occurs when window is closed
    def closeEvent(self, event):
        """modified close event to add confirmation on close"""
        if self.confirm_on_close:
            confirm = exitDialog(self)
        else:
            confirm = True
        if confirm:
            if self.childWindow is not None:
                # closes the child window without a dialog box
                self.childWindow.no_close_dialog = True
                self.childWindow.close()
            self.deleteLater()
            event.accept()
        else:
            event.ignore()

    # gets setting values from settings file
    def getSettings(self):
        settings = SettingsWindow.getFileSettings()
        return settings

    # gets the default values for the settings (for when settings file is missing, or resetting)
    def getDefaultSettings(self):
        settings = SettingsWindow.getDefaultSettings()
        return settings

    # gets settings if not given, and then opens settings window
    def openSettings(self, settings: dict | None = None):
        if settings is None:
            try:
                settings = self.getSettings()
            except Exception:
                settings = self.getDefaultSettings()

        self.SettingsWindow = SettingsWindow(self, settings)
        self.SettingsWindow.finished.connect(self.setSettings)

    # sets settings after getting them
    def setSettings(self):
        settings = self.SettingsWindow.getSettings()
        self.SettingsWindow = None
        self.set_button.clicked.disconnect()
        self.set_button.clicked.connect(lambda: self.openSettings(settings))
        self.load_data_type = settings["data_load_type"]
        conf = settings["confirm_on_close"]
        if conf == "False" or not conf:
            self.confirm_on_close = False
        else:
            self.confirm_on_close = True

    # opens calibration file dialog window, then loads data
    def openPath(self):

        if self.load_data_type == "tif":
            self.calibfiledir = LoadTiffCalib.fileDialog(self)

            if self.calibfiledir is not None:
                self.calibscans = LoadTiffCalib.loadData(self.calibfiledir)
            else:
                return
        elif self.load_data_type == "h5py":
            self.calibfiledir = LoadH5Data.fileDialog(self)
            if self.calibfiledir is not None:
                images = []
                energies = []
                for i in self.calibfiledir:
                    img, en, _ = LoadH5Data.loadData(i)
                    images.append(img)
                    energies += en

                self.calibscans = []
                for imgs in images:
                    for img in imgs:
                        self.calibscans.append(img)
            else:
                return

        # creates a new scrollable area
        if self.calib_grid_scroll is not None:
            self.mlayout.removeWidget(self.calib_grid_scroll)
        self.calib_grid_scroll = QtWidgets.QScrollArea()
        self.calib_grid_scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.calib_widget = QtWidgets.QWidget()
        self.calib_grid = QtWidgets.QGridLayout(self.calib_widget)
        self.calib_grid.setColumnMinimumWidth(1, 10)

        # adds a File Name label above file names
        filename = QtWidgets.QLabel("File Name")
        font = filename.font()
        font.setUnderline(True)
        filename.setFont(font)
        self.calib_grid.addWidget(filename, 0, 0, AlignFlag.AlignLeft)
        del font, filename

        # adds an Energy label above energies
        energy = QtWidgets.QLabel("Energy")
        font = energy.font()
        font.setUnderline(True)
        energy.setFont(font)
        self.calib_grid.addWidget(energy, 0, 2, AlignFlag.AlignLeft)
        del font, energy

        if self.load_data_type == "tif":
            self.calib_energies = [
                CalibFile(
                    self, self.calibscans.items[i], c, i + 1, self.calibscans.dims
                )
                for i, c in enumerate(self.calibfiledir)
            ]
        elif self.load_data_type == "h5py":
            self.calib_energies = [
                CalibFile(
                    self, c, str(i), i + 1, (len(c[0]), len(c)), energy=energies[i]
                )
                for i, c in enumerate(self.calibscans)
            ]

        # adds scrollable area to the main window
        self.calib_grid_scroll.setWidget(self.calib_widget)
        self.calib_grid_scroll.setFixedWidth(290)

        self.getCalibPoints(True)

    # loads information file
    def loadInfoFile(self):
        directory = LoadInfoData.fileDialog(self)
        self.info_file = LoadInfoData.loadData(self, directory)

    # gets points from calibration scans
    def getCalibPoints(self, runinit: bool = False):
        minc = self.mincuts.value()
        maxc = self.maxcuts.value()
        if minc > maxc:
            self.error = ErrorWindow("minmaxcuts")
            return
        enabled_energies = [i for i in self.calib_energies if i.enabled]
        self.LoadWindow = LoadingBarWindow(
            "Loading calibration data...", len(enabled_energies)
        )
        old_points = self.points
        self.points = []
        old_spots = self.spots
        self.spots = []
        for i in enabled_energies:
            if self.LoadWindow.wasCanceled():
                self.points = old_points
                self.spots = old_spots
                return
            points, spots = getCoordsFromScans(
                i.data, reorder=True, cuts=(minc, maxc), dtype=self.load_data_type
            )
            self.points.append(points)
            self.spots.append(spots)
            self.LoadWindow.add()
            QtWidgets.QApplication.processEvents()

        if runinit:
            self.initDrawCalibPoints()
        else:
            self.drawCalibPoints()

    # runs drawCalibPoints and places file names next to energy input boxes
    def initDrawCalibPoints(self):

        self.drawCalibPoints()
        self.mlayout.addWidget(self.calib_grid_scroll, 3, 0, 1, 2, AlignFlag.AlignLeft)

    # draws calibration points to the main scatter plot grid
    def drawCalibPoints(self):

        # deletes existing scatter plot grid
        if self.ax is not None:
            self.ax.clear()
        else:
            self.ax = pg.ScatterPlotItem()

        # removes old scatter plot and old ROIs, if any exist
        self.rects = []
        for item in self.sc.items():
            self.sc.removeItem(item)
        self.sc.addItem(self.ax)
        self.sc.setBackground("w")

        for i in self.points:
            self.ax.addPoints(i[0], i[1], size=1, brush=(0, 0, 0, 255))
        # self.ax.addPoints(spots=self.spots, brush=(0, 0, 0, 255)[0])

        # enables buttons
        self.drawn_calib = True
        self.reload_calib.setDisabled(False)
        self.approx_rois.setDisabled(False)
        self.add_roi.setDisabled(False)
        if self.add_roi.text() == "Cancel":
            self.add_roi.setText("Add ROI")
        self.load_info_file_button.setDisabled(False)

    # manually add an ROI
    def manualAddROI(self):
        self.emap_calc_button.setDisabled(False)
        xy = self.sc.visibleRange()
        x = xy.center().x()
        y = xy.center().y()
        w = xy.width() / 8
        h = xy.height() / 6
        rect = pg.RectROI(
            pos=(x - w / 2, y - h / 2),
            size=(w, h),
            pen=(255, 0, 0, 255),
            hoverPen=(255, 20, 20, 255),
            handlePen=(255, 0, 0, 255),
            handleHoverPen=(255, 0, 0, 255),
            resizable=True,
            removable=True,
        )
        rect.sigRemoveRequested.connect(self.removeROI)
        rect.addScaleHandle(pos=(0, 0), center=(1, 1))
        rect.addScaleHandle(pos=(0, 1), center=(1, 0))
        rect.addScaleHandle(pos=(1, 0), center=(0, 1))
        rect.addScaleHandle(pos=(0, 0.5), center=(1, 0.5))
        rect.addScaleHandle(pos=(1, 0.5), center=(0, 0.5))
        rect.addScaleHandle(pos=(0.5, 0), center=(0.5, 1))
        rect.addScaleHandle(pos=(0.5, 1), center=(0.5, 0))

        self.sc.addItem(rect)
        self.rects.append(rect)

    # asks for number of ROIs (see doApproxROIs)
    def approxROIs(self):
        self.ApproxWindow = ApproxWindow(self)
        self.ApproxWindow.finished.connect(self.doApproxROIs)

    # This is what approximates the ROIs
    def doApproxROIs(self):
        if self.ApproxWindow.value is None:
            return

        self.emap_calc_button.setDisabled(False)

        # approximates ROIs
        numcrystals = self.ApproxWindow.value
        lencalibs = len(self.calib_energies)
        hrois, vrois = approximateROIs(
            numcrystals,
            self.mincuts.value(),
            self.maxcuts.value(),
            self.calibscans.items[int(lencalibs / 2)],
            self.points,
        )

        # points are redrawn to clear old ROIs, etc. Takes virtually no time.
        self.drawCalibPoints()

        # creates rectangles and stores them
        self.rects = []
        for i, h in enumerate(hrois):
            v = vrois[i]
            rect = pg.RectROI(
                pos=(h[0], v[0]),
                size=(h[1] - h[0], v[1] - v[0]),
                pen=(255, 0, 0, 255),
                hoverPen=(255, 20, 20, 255),
                handlePen=(255, 0, 0, 255),
                handleHoverPen=(255, 0, 0, 255),
                resizable=True,
                removable=True,
            )
            # adds corner and edge moveability
            rect.sigRemoveRequested.connect(self.removeROI)
            rect.addScaleHandle(pos=(0, 0), center=(1, 1))
            rect.addScaleHandle(pos=(0, 1), center=(1, 0))
            rect.addScaleHandle(pos=(1, 0), center=(0, 1))
            rect.addScaleHandle(pos=(0, 0.5), center=(1, 0.5))
            rect.addScaleHandle(pos=(1, 0.5), center=(0, 0.5))
            rect.addScaleHandle(pos=(0.5, 0), center=(0.5, 1))
            rect.addScaleHandle(pos=(0.5, 1), center=(0.5, 0))

            self.sc.addItem(rect)
            self.rects.append(rect)

    # Removes ROI
    def removeROI(self, event):
        self.rects.remove(event)
        self.sc.removeItem(event)
        if not len(self.rects):
            self.emap_calc_button.setDisabled(True)

    # Calculates (makes) HROIs from rectangles.
    def calcHrois(self):
        # this section calculates the hrois
        self.hrois = []
        for i in self.rects:
            x = i.pos()[0]
            w = i.size()[0]
            self.hrois.append(HROI(x, x + w))
        # print("done")

    # Calculates (makes) ROIs from rectangles.
    def calcRois(self, dtype: str = "coords"):
        """dtype accepts 'coords' or 'xywh'"""
        rois = []
        for i in self.rects:
            x = i.pos()[0]
            w = i.size()[0]
            y = i.pos()[1]
            h = i.size()[1]
            if dtype == "coords":
                rois.append((x, y, x + w, y + h))
            elif dtype == "xywh":
                rois.append((x, y, w, h))
        return rois

    # organizes data and then calculates an energy map
    def calcEmap(self):
        # stops if any energy value is not given
        enabled = tuple(i for i in self.calib_energies if i.enabled)
        if self.info_file is None and any(e.getVal() == 0 for e in enabled):
            self.error = ErrorWindow("noInfo")
            return

        scans = [i.data for i in enabled]
        energies = [i.getVal() for i in enabled]

        # creates a dataset without the files that have no datapoints
        points = self.points.copy()
        indexes = []
        for i, _ in enumerate(scans):
            if len(points[i][0]) < 2:
                indexes.insert(0, i)
        for i in indexes:
            scans.pop(i)
            points.pop(i)
            energies.pop(i)
        del indexes
        self.approx_rois.setDisabled(True)
        self.add_roi.setDisabled(True)
        self.load_info_file_button.setDisabled(True)
        # self.emap_select_button.setDisabled(True)
        self.emap_calc_button.setDisabled(True)
        self.emap_save_button.setDisabled(False)

        # gets the HROIs from the rectangles
        self.calcHrois()

        # tries multiple energy map calculation methods
        rois = self.calcRois()
        dims = enabled[0].dims
        self.emap = calcEnergyMap(dims, energies, points, rois)

        self.drawEmap()  # draws the final energy map

    # draws the energy map to the main grid
    def drawEmap(self):
        if self.ax is None:
            self.ax = pg.ScatterPlotItem()
        self.ax.clear()
        for i in self.rects:
            self.sc.removeItem(i)

        if self.emap_img is not None:
            self.sc.removeItem(self.emap_img)
        self.sc.setBackground("k")  # 'k' is black ('b' is blue)
        self.emap_img = pg.ImageItem(np.log(self.emap.values))  # raises warning
        self.sc.addItem(self.emap_img)

    # Saves the energy map to a numpy file for easy future usage
    def saveEmap(self):
        if self.emap is None:
            return
        dialog = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Energy Map",
            filter="Numpy Array (*.npy)",
            directory=desktop_directory,
        )
        dir = dialog[0]
        if not len(dir):
            return
        self.emap.saveToPath(dir)
        name = dir[dir.rfind("/") + 1 :]
        self.emap.name = name[: name.rfind(".")]

    # loads an energy map from a numpy file, as created above
    def loadEmap(self):

        text = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Energy Map",
            directory=str(desktop_directory),
            filter="Numpy Array (*.npy)",
        )
        if not len(text[0]):
            return
        self.emap = core.EnergyMap.loadFromPath(text[0])
        self.emap_save_button.setDisabled(False)
        self.drawEmap()

    # manages the creation of an XES window
    def runXES(self):
        if type(self.childWindow) is XESWindow:
            self.childWindow.activateWindow()
        elif type(self.childWindow) is RXESWindow:
            self.childWindow.activateWindow()
            run = exitDialog(self.childWindow)
            if run:
                self.childWindow.no_close_dialog = True
                self.childWindow.close()
                self.childWindow = XESWindow(self)
        elif self.childWindow is None:
            self.childWindow = XESWindow(self)
        else:
            self.error = ErrorWindow()

    # manages the creation of an RXES window
    def runRXES(self):
        if type(self.childWindow) is RXESWindow:
            self.childWindow.activateWindow()
        elif type(self.childWindow) is XESWindow:
            self.childWindow.activateWindow()
            run = exitDialog(self.childWindow)
            if run:
                self.childWindow.no_close_dialog = True
                self.childWindow.close()
                self.childWindow = RXESWindow(self)
        elif self.childWindow is None:
            self.childWindow = RXESWindow(self)
        else:
            self.error = ErrorWindow()


# creates a MainWindow when file is execcuted
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icons/spc-logo-nobg.png"))
    W = MainWindow()
    # sys.exit(app.exec())
    app.exec()
