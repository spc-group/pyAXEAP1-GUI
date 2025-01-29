# :author: Alexander Berno
"""RXES Window"""

from axeap.core import Scan
import numpy as np
import pyqtgraph as pg
import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    # NavigationToolbar2QT as NavigationToolbar,
)
import matplotlib

matplotlib.use("QtAgg")

from ExitDialogWindow import exitDialog
from RXESSpectrumClass import Dataset, Spectrum
from FileLoad import LoadTifSpectraData, LoadH5Data
from BaseWindow import Window
from ErrorWindow import ErrorWindow
from spectraFunctions import calcDataForSpectra, calcSpectra
from LoadingBarWindow import LoadingBarWindow
from FileLoad import LoadInfoData
from SettingsWindow import SettingsWindow


AlignFlag = QtCore.Qt.AlignmentFlag


# This is to remove Qt warning messages (for parts that are known to not be problems)
def handler(msg_type, msg_log, msg_string):
    pass


# see handler above
QtCore.qInstallMessageHandler(handler)


class Mpl3dCanvas(FigureCanvas):
    """canvas for 3d figure"""

    def __init__(self, parent=None, width=3, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(projection="3d")
        super(Mpl3dCanvas, self).__init__(fig)


class Mpl2dCanvas(FigureCanvas):
    """canvas for 2d figure"""

    def __init__(self, parent=None, width=3, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(Mpl2dCanvas, self).__init__(fig)


class RXESWindow(Window):
    """Window for viewing RXES data"""

    def __init__(self, parent: QtWidgets.QMainWindow | None, *args, **kwargs):
        super(RXESWindow, self).__init__(*args, **kwargs)

        # Default Values
        self.setWindowTitle("RXES (RIXS)")
        self.setFixedSize(780, 720)
        self.parent = parent
        if self.parent is None:
            self.no_close_dialog = True
        else:
            self.no_close_dialog = False
        self.emaps = []
        self.map_type = 0
        self.info_file = None
        self.i0 = None
        self.incident_energy = None
        self.normalize = False
        self.use_log = False
        self.transfer = False
        self.ela_remove = False
        self.scanset = []
        self.foldernames = []
        self.datasets = []

        # energy map assignment (if parent has an energy map)
        if self.parent is None:
            self.emap = None
        else:
            try:
                self.emap = self.parent.emap
                self.emaps.append(self.emap)
            except Exception:
                self.emap = None

        # 3D canvas init
        self.sc3d = Mpl3dCanvas(self)
        # toolbar = NavigationToolbar(self.sc3d, self)
        self.ax3d = self.sc3d.axes
        self.fixax3d()

        # 2D canvas init (contour map)
        self.sc2d = Mpl2dCanvas(self)
        self.ax2d = self.sc2d.axes
        self.ax2d.set_position((0.23, 0.16, 0.73, 0.8))
        self.fixax2d()
        # self.sc2d = pg.plot()
        # # self.sc2d.setBackground("w")
        # self.sc2d.plotItem.getAxis("left").setLabel(text="Emission", **label_style)
        # self.sc2d.plotItem.getAxis("bottom").setLabel(text="Incident", **label_style)
        # self.sc2d.setFixedSize(300, 300)
        # self.ax2d = pg.ScatterPlotItem()
        # self.sc2d.addItem(self.ax2d)

        # Emission canvas init
        label_style = {"color": "#444", "font-size": "14pt"}
        self.emsc = pg.plot()
        self.emsc.setBackground("w")
        self.emsc.plotItem.getAxis("left").setLabel(text="Intensity", **label_style)
        self.emsc.plotItem.getAxis("bottom").setLabel(text="Incident", **label_style)
        self.emsc.setFixedSize(300, 300)

        # Incident canvas init
        self.incsc = pg.plot()
        self.incsc.setBackground("w")
        self.incsc.plotItem.getAxis("left").setLabel(text="Intensity", **label_style)
        self.incsc.plotItem.getAxis("bottom").setLabel(text="Emission", **label_style)
        self.incsc.setFixedSize(300, 300)

        # RXES data button
        load_rxes_button = QtWidgets.QPushButton("Load RXES Data...")
        load_rxes_button.clicked.connect(self.loadRXES)
        load_rxes_button.setFixedSize(140, 30)

        # Refresh button
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.refresh_button.setDisabled(True)
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh_button.setFixedSize(100, 30)

        # Energy map selection box
        self.emap_combo = QtWidgets.QComboBox()
        self.emap_combo.setFixedSize(140, 30)
        if self.emap is not None:
            self.emap_combo.addItem(self.emap.name)

        # Load Energy Map button
        emap_load_button = QtWidgets.QPushButton("Load Energy Map...")
        emap_load_button.setFixedSize(140, 30)
        emap_load_button.clicked.connect(self.loadEmap)

        # "norm" grid, not only used for normalization
        norm_area = QtWidgets.QScrollArea()
        norm_widget = QtWidgets.QWidget()
        norm_grid = QtWidgets.QGridLayout(norm_widget)

        # Normalize checkbox
        norm_check = QtWidgets.QCheckBox("Normalize")
        norm_check.stateChanged.connect(self.normSwitch)

        # Load Info File button
        info_load_button = QtWidgets.QPushButton("Load Info File...")
        info_load_button.setFixedSize(120, 30)
        info_load_button.clicked.connect(self.loadInfoFile)

        # colour mode selection box and label
        try:
            cmap = SettingsWindow.getFileSettings()["cmap"]
        except Exception:
            cmap = "pcolor"
        self.colour_mode = QtWidgets.QComboBox()
        self.colour_mode.setFixedSize(72, 30)
        self.colour_mode.addItem("PColor", "pcolor")
        self.colour_mode.addItem("Contour", "contour")
        if cmap == "pcolor":
            self.colour_mode.setCurrentIndex(0)
        else:
            self.colour_mode.setCurrentIndex(1)
        colour_mode_label = QtWidgets.QLabel("2D Mode")

        # use log for intensity checkbox
        log_check = QtWidgets.QCheckBox("Log Intensity")
        log_check.stateChanged.connect(self.logSwitch)

        # "transfer energy" checkbox
        transfer_check = QtWidgets.QCheckBox("Transfer Energy")
        transfer_check.stateChanged.connect(self.transferSwitch)

        # "elastic removal" checkbox
        ela_check = QtWidgets.QCheckBox("Ela. Removal")
        ela_check.stateChanged.connect(self.elaSwitch)

        # add everything to norm_area
        norm_grid.addWidget(info_load_button, 0, 0, 1, 2)
        norm_grid.addWidget(colour_mode_label, 1, 0)
        norm_grid.addWidget(self.colour_mode, 1, 1)
        norm_grid.addWidget(norm_check, 2, 0, 1, 2)
        norm_grid.addWidget(log_check, 3, 0, 1, 2)
        norm_grid.addWidget(ela_check, 4, 0, 1, 2)
        norm_grid.addWidget(transfer_check, 5, 0, 1, 2)
        norm_area.setWidget(norm_widget)

        # Emission and Incident selection
        label_em = QtWidgets.QLabel("Emission")
        self.select_em = QtWidgets.QLineEdit()
        self.select_em.setDisabled(True)
        label_inc = QtWidgets.QLabel("Incident")
        self.select_inc = QtWidgets.QLineEdit()
        self.select_inc.setDisabled(True)
        self.em_inc_button = QtWidgets.QPushButton("Run")
        self.em_inc_button.clicked.connect(self.calcEmInc)
        self.em_inc_button.setDisabled(True)

        # Connects everything to the RXES window
        widget = QtWidgets.QWidget()
        self.mlayout = QtWidgets.QGridLayout(widget)
        self.mlayout.addWidget(load_rxes_button, 1, 0, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.emap_combo, 0, 5, AlignFlag.AlignRight)
        # self.mlayout.addWidget(toolbar, 1, 1, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.refresh_button, 1, 1, 1, 2, AlignFlag.AlignTop)
        self.mlayout.addWidget(emap_load_button, 1, 5, AlignFlag.AlignRight)
        self.mlayout.addWidget(norm_area, 2, 0)
        self.mlayout.addWidget(self.sc3d, 2, 1, 1, 4, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.sc2d, 2, 2, 1, 4, AlignFlag.AlignRight)
        self.mlayout.addWidget(label_em, 3, 1, AlignFlag.AlignRight)
        self.mlayout.addWidget(self.select_em, 3, 2)
        self.mlayout.addWidget(label_inc, 3, 3)
        self.mlayout.addWidget(self.select_inc, 3, 4)
        self.mlayout.addWidget(self.em_inc_button, 3, 5)
        self.mlayout.addWidget(self.emsc, 4, 1, 1, 4, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.incsc, 4, 2, 1, 4, AlignFlag.AlignRight)
        self.mlayout.setColumnMinimumWidth(0, 150)
        self.mlayout.setColumnMinimumWidth(2, 180)
        self.mlayout.setColumnMinimumWidth(4, 180)

        self.setCentralWidget(widget)

        self.show()

    # Sets labels and view angle for 3D graph
    def fixax3d(self):
        self.ax3d.set_xlabel("Incident")
        self.ax3d.set_ylabel("Emission")
        # self.ax3d.set_zlabel("Intensity")
        self.ax3d.view_init(25, 225, 0)

    # Sets labels for contour map
    def fixax2d(self):
        self.ax2d.set_xlabel("Incident")
        self.ax2d.set_ylabel("Emission")

    # flips whether or not to normalize
    def normSwitch(self):
        self.normalize = not self.normalize

    # flips whether or not to log intensities
    def logSwitch(self):
        self.use_log = not self.use_log

    # sets whether or not to use transfer energy
    def transferSwitch(self):
        self.transfer = not self.transfer

    # sets whether or not to use elastic removal
    def elaSwitch(self):
        self.ela_remove = not self.ela_remove

    # handles close event so a confirmation window can appear
    def closeEvent(self, event):
        # The no_close_dialog exists so the window can be closed by a MainWindow with no issue
        if not self.no_close_dialog:
            if hasattr(self.parent, "confirm_on_close"):
                if self.parent.confirm_on_close:
                    confirm = exitDialog(self)
                else:
                    confirm = True
            else:
                confirm = exitDialog(self)
            if confirm:
                if hasattr(self.parent, "childWindow"):
                    self.parent.childWindow = None
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # loads information file
    def loadInfoFile(self):
        directory = LoadInfoData.fileDialog(self)
        if directory[0] == "":
            return
        self.info_file, self.info_table = LoadInfoData.loadData(
            self, directory, rtype="rxes"
        )
        try:
            self.incident_energy = self.info_table["Energy"]
            self.i0 = self.info_table["I0"]
        except Exception:
            self.incident_energy = self.info_table[0]
            self.i0 = self.info_table[1]

    # Main function for loading RXES data
    def loadRXES(self):

        if len(self.emaps):
            self.emap = self.emaps[int(self.emap_combo.currentIndex() / 2)]
        elif self.emap is None:
            try:
                self.emap = self.parent.emap
            except Exception:
                self.error = ErrorWindow("XESemap")
                return

        emap = self.emap
        data = calcDataForSpectra(emap)
        dtype = self.loadType()
        if dtype == "tif":
            self.filenames = LoadTifSpectraData.fileDialog(self)
        elif dtype == "h5py":
            self.filenames = LoadH5Data.fileDialog(self)
        else:
            raise TypeError(f"Unknown dtype {dtype}")

        if not self.filenames:
            return

        LoadWindow = LoadingBarWindow(
            "Loading RXES (RIXS) data...", len(self.filenames)
        )
        scanset = []
        for i in self.filenames:
            if LoadWindow.wasCanceled():
                break
            spectra = calcSpectra(i, emap, data, dtype)
            if type(spectra) is list:
                scanset += spectra
            else:
                scanset.append(spectra)
            LoadWindow.add()
            QtWidgets.QApplication.processEvents()
        LoadWindow.deleteLater()

        if LoadWindow.wasCanceled():
            return

        self.scanset.append(scanset)
        # if multi:
        #     if self.scanset != []:
        #         if type(self.scanset[0]) is not list:
        #             self.scanset = []
        #     self.scanset.append(scanset)

        # else:
        #     self.scanset = scanset

        dname = self.filenames[0]
        dname = dname[: dname.rfind("/")]
        dname = dname[dname.rfind("/") + 1 :]
        self.foldernames.append(dname)
        dataset = Dataset(self, dname, scanset, len(self.datasets))
        self.datasets.append(dataset)
        self.addDataCheckbox()

        failed = self.setData(self.scanset)  # returns True if failed, otherwise None
        if failed:
            self.foldernames.remove(dname)
            self.datasets.remove(dataset)
            self.addDataCheckbox()
            return

        self.graph3dSpectra()
        self.graph2dSpectra()

    # sets spectra data, including creating Spectrum classes
    def setData(self, scanset):

        new_set = []
        for dataset in self.datasets:
            if dataset.enabled:
                new_set.append(dataset.data)

        scanset = new_set
        if not len(scanset):
            self.spectra = []
            return

        ul = self.use_log
        tr = self.transfer
        ela = self.ela_remove
        if not self.normalize and self.incident_energy is None:
            # if not multi:
            #     self.spectra = [
            #         Spectrum(self, s, i, ul=ul, tr=tr, ela=ela)
            #         for i, s in enumerate(scanset)
            #     ]
            # else:
            self.spectra = []
            for i, _ in enumerate(scanset[0]):
                s = [scanset[j][i] for j, _ in enumerate(scanset)]
                self.spectra.append(Spectrum(self, s, i, ul=ul, tr=tr, ela=ela))
        elif self.i0 is None or self.incident_energy is None:
            self.error = ErrorWindow("noInfoRXES")
            return True

        else:
            # if multi:
            slen = len(scanset[0])
            # else:
            #     slen = len(scanset)

            inc = self.incident_energy
            i0 = self.i0

            inclen = len(inc)
            i0len = len(i0)

            if self.normalize:
                if slen != i0len or slen != inclen or i0len != inclen:
                    self.error = ErrorWindow("NotEnoughData")
                    return True
                # if not multi:
                #     self.spectra = [
                #         Spectrum(self, s, i, inc[i], i0[i], ul=ul, tr=tr, ela=ela)
                #         for i, s in enumerate(scanset)
                #     ]
                # else:
                self.spectra = []
                for i, _ in enumerate(scanset[0]):
                    s = [scanset[j][i] for j, _ in enumerate(scanset)]
                    self.spectra.append(
                        Spectrum(self, s, i, inc[i], i0[i], ul=ul, tr=tr, ela=ela)
                    )

            else:
                # if not multi:
                #     self.spectra = [
                #         Spectrum(self, s, i, inc[i], ul=ul, tr=tr, ela=ela)
                #         for i, s in enumerate(scanset)
                #     ]
                # else:
                self.spectra = []
                for i, _ in enumerate(scanset[0]):
                    s = [scanset[j][i] for j, _ in enumerate(scanset)]
                    self.spectra.append(
                        Spectrum(self, s, i, inc[i], ul=ul, tr=tr, ela=ela)
                    )

    # creates the checkbox layout (and recreates it to fix formatting)
    def addDataCheckbox(self):

        try:
            self.mlayout.removeWidget(self.checks)
        except Exception:
            pass

        self.checks = QtWidgets.QScrollArea()
        self.checks_widget = QtWidgets.QWidget()
        self.checks_grid = QtWidgets.QGridLayout(self.checks_widget)

        self.datasets = [
            Dataset(self, d.name, d.data, d.num, d.enabled) for d in self.datasets
        ]
        for dataset in self.datasets:
            self.checks_grid.addWidget(dataset.box, dataset.num, 0)
            self.checks_grid.setRowMinimumHeight(dataset.num, 20)

        self.checks.setWidget(self.checks_widget)
        self.mlayout.addWidget(self.checks, 4, 0)

    # sets data and graphs data all in one (for simpler calling)
    def refresh(self):
        self.setData(self.scanset)
        self.graph3dSpectra()
        self.graph2dSpectra()

    # This is the 3d graph
    def graph3dSpectra(self):
        self.ax3d.clear()
        self.fixax3d()
        self.refresh_button.setDisabled(False)

        if not len(self.spectra):
            self.sc3d.draw_idle()
            return

        for _, s in enumerate(self.spectra):
            self.ax3d.plot3D(s.inc, s.em, s.inte, c=("b", 0.3))
        self.sc3d.draw_idle()

    # This is the contour map
    def graph2dSpectra(self):
        # min and max values used for analysis later
        # these values are used in RXESWindow.calcEmInc

        if not len(self.spectra):
            self.ax2d.cla()
            self.fixax2d()
            self.sc2d.draw_idle()
            return

        mininte = 1000
        maxinte = 0
        minem = 100000
        maxem = 0
        mininc = 1000
        maxinc = 0
        for s in self.spectra:
            if max(s.inte) > maxinte:
                maxinte = max(s.inte)
            if min(s.inte) < mininte:
                mininte = min(s.inte)
            if max(s.em) > maxem:
                maxem = max(s.em)
            if min(s.em) < minem:
                minem = min(s.em)
            if max(s.inc) > maxinc:
                maxinc = max(s.inc)
            if min(s.inc) < mininc:
                mininc = min(s.inc)
        self.select_em.setValidator(QtGui.QIntValidator(int(minem), int(maxem)))
        self.select_inc.setValidator(QtGui.QIntValidator(int(mininc), int(maxinc)))
        self.em_limits = (minem, maxem)
        self.inc_limits = (mininc, maxinc)
        self.select_em.setDisabled(False)
        self.select_inc.setDisabled(False)
        self.em_inc_button.setDisabled(False)

        # y_range = [100000, -100000]  #
        # for k, s in enumerate(self.spectra): #
        #     for i, c in enumerate(s.em): #
        #         if c < y_range[0]:  #
        #             y_range[0] = c  #
        #         elif c > y_range[1]:  #
        #             y_range[1] = c  #

        x, y, z = [], [], []
        change_y = True
        for k, s in enumerate(self.spectra):
            for i, c in enumerate(s.inc):
                if change_y:
                    y.append(s.em[i])
                try:
                    z[k].insert(i, s.inte[i])
                except IndexError:
                    z.insert(k, [s.inte[i]])
            x.append(c)
            change_y = False

        new_z = []
        for i, _ in enumerate(z):
            for j, _ in enumerate(z[i]):
                try:
                    new_z[j].append(z[i][j])
                except IndexError:
                    new_z.insert(j, [z[i][j]])

        self.ax2d.cla()
        self.fixax2d()
        self.map_type = self.colour_mode.currentData()
        if self.map_type == "contour":
            self.ax2d.contourf(x, y, new_z, levels=14, extend="both", cmap="viridis")
        elif self.map_type == "pcolor":
            self.ax2d.pcolor(x, y, new_z)

        self.sc2d.draw_idle()

        self.select_em.setText("")
        self.select_inc.setText("")
        self.emsc.plotItem.clear()
        self.incsc.plotItem.clear()

    # Get datapoints for Emission and Incident vs Intensity 2D graphs
    def calcEmInc(self):
        self.error = lambda: ErrorWindow("invalidEmIncRXES")

        try:
            em = int(self.select_em.text())
            inc = int(self.select_inc.text())
        except ValueError:
            self.error()
            return

        minem, maxem = self.em_limits
        mininc, maxinc = self.inc_limits
        if not (minem <= em <= maxem) or not (mininc <= inc <= maxinc):
            self.error()
            return

        # Emission Calc
        em_incident = []
        em_intensity = []
        for s in self.spectra:
            for i, e in enumerate(s.em):
                if em - 0.1 <= e <= em + 0.1:
                    break
            em_incident.append(s.inc[0])
            em_intensity.append(s.inte[i])
        em_data = (em_incident, em_intensity)

        # Incident Calc
        try:
            inc_spectrum = self.spectra[inc]
        except Exception:
            ls = None
            for s in self.spectra:
                if s.inc[0] > inc:
                    if ls is None:
                        ls = s
                    break
                ls = s

            if min(abs(ls.inc[0] - inc), abs(s.inc[0] - inc)) == abs(s.inc[0] - inc):
                inc_spectrum = s
            else:
                inc_spectrum = ls

        inc_emission = inc_spectrum.em
        inc_intensity = inc_spectrum.inte
        inc_data = (inc_emission, inc_intensity)

        self.graphEmInc(em_data, inc_data)

    # Graph Emission and Incident vs Intensity 2D graphs
    def graphEmInc(self, em, inc):
        self.emsc.plotItem.clear()
        self.emsc.plotItem.plot(em[0], em[1], pen=pg.mkPen(color="k", width=2))
        self.incsc.plotItem.clear()
        self.incsc.plotItem.plot(inc[0], inc[1], pen=pg.mkPen(color="k", width=2))


# creates an RXES window when file is run
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icons/spc-logo-nobg.png"))
    W = RXESWindow(None)
    # sys.exit(app.exec())
    app.exec()
