# :author: Alexander Berno
"""RXES Window"""

from ExitDialogWindow import exitDialog
from RXESSpectrumClass import Spectrum
from FileLoad import LoadTifSpectraData
from BaseWindow import Window
from ErrorWindow import ErrorWindow
from spectraFunctions import calcDataForSpectra, calcSpectra
from LoadingBarWindow import LoadingBarWindow
from colourGenerator import contourMap
from math import sqrt

import pyqtgraph as pg
import sys
import numpy as np
import axeap.core as core
import pathlib
from PyQt6 import QtWidgets, QtCore, QtGui
import matplotlib
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

matplotlib.use("QtAgg")

AlignFlag = QtCore.Qt.AlignmentFlag


def handler(msg_type, msg_log, msg_string):
    pass


QtCore.qInstallMessageHandler(handler)


class Mpl3dCanvas(FigureCanvas):

    def __init__(self, parent=None, width=3, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(projection="3d")
        super(Mpl3dCanvas, self).__init__(fig)


class Mpl2dCanvas(FigureCanvas):

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
        self.no_close_dialog = False
        self.parent = parent
        self.emaps = []
        self.map_type = "pcolor"

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
        load_rxes_button = QtWidgets.QPushButton("RXES Data...")
        load_rxes_button.clicked.connect(self.loadRXES)
        load_rxes_button.setFixedSize(140, 30)

        # Energy map selection box
        self.emap_combo = QtWidgets.QComboBox()
        self.emap_combo.setFixedSize(140, 30)
        if self.emap is not None:
            self.emap_combo.addItem(self.emap.name)

        # Load Energy Map button
        emap_load_button = QtWidgets.QPushButton("Load Energy Map...")
        emap_load_button.setFixedSize(140, 30)
        emap_load_button.clicked.connect(self.loadEmap)

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
        self.mlayout.addWidget(load_rxes_button, 0, 0, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.emap_combo, 0, 5, AlignFlag.AlignRight)
        # self.mlayout.addWidget(toolbar, 1, 1, AlignFlag.AlignLeft)
        self.mlayout.addWidget(emap_load_button, 1, 5, AlignFlag.AlignRight)
        self.mlayout.addWidget(self.sc3d, 2, 1, 1, 4, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.sc2d, 2, 2, 1, 4, AlignFlag.AlignRight)
        self.mlayout.addWidget(label_em, 3, 1)
        self.mlayout.addWidget(self.select_em, 3, 2)
        self.mlayout.addWidget(label_inc, 3, 3)
        self.mlayout.addWidget(self.select_inc, 3, 4)
        self.mlayout.addWidget(self.em_inc_button, 3, 5)
        self.mlayout.addWidget(self.emsc, 4, 1, 1, 4, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.incsc, 4, 2, 1, 4, AlignFlag.AlignRight)
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

    # runs when the window is closed
    def closeEvent(self, event):
        # The no_close_dialog exists so the window can be closed by a MainWindow with no issue
        if not self.no_close_dialog:
            confirm = exitDialog(self)
            if confirm:
                self.parent.childWindow = None
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # Main function for loading RXES data
    def loadRXES(self):
        if len(self.emaps):
            self.emap = self.emaps[self.emap_combo.currentIndex()]
        elif self.emap is None:
            try:
                self.emap = self.parent.emap
            except Exception:
                self.error = ErrorWindow("XESemap")
                return

        self.filenames = LoadTifSpectraData.fileDialog(self)
        if not self.filenames:
            return

        emap = self.emap
        LoadWindow = LoadingBarWindow(
            "Loading RXES (RIXS) data...", len(self.filenames)
        )
        scanset = []
        data = calcDataForSpectra(emap)
        for i in self.filenames:
            if LoadWindow.wasCanceled():
                break
            scanset.append(calcSpectra(i, emap, data))
            LoadWindow.add()
            QtWidgets.QApplication.processEvents()
        LoadWindow.deleteLater()

        if LoadWindow.wasCanceled():
            return

        self.spectra = [Spectrum(self, s, i) for i, s in enumerate(scanset)]

        self.graph3dSpectra()
        self.graph2dSpectra()

    # This is the 3d graph
    def graph3dSpectra(self):
        self.ax3d.clear()
        self.fixax3d()

        for _, s in enumerate(self.spectra):
            self.ax3d.plot3D(s.inc, s.em, s.inte, c=("b", 0.3))
        self.sc3d.draw_idle()

    # This is the contour map
    def graph2dSpectra(self):
        # min and max values used for analysis later
        # these values are used in RXESWindow.calcEmInc
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

        x, y, z = [], [], []
        change_y = True
        for s in self.spectra:
            for i, c in enumerate(s.inc):
                if change_y:
                    y.append(s.em[i])
                try:
                    z[c].insert(i, s.inte[i])
                except IndexError:
                    z.insert(c, [s.inte[i]])
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

        if self.map_type == "pcolor":
            self.ax2d.pcolor(x, y, new_z)
        elif self.map_type == "contour" or self.map_type == "contourf":
            self.ax2d.contourf(x, y, new_z, extend="both", cmap="viridis")
        else:
            self.error = ErrorWindow()
            return
        self.sc2d.draw_idle()

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
        inc_spectrum = self.spectra[inc]
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icons/spc-logo-nobg.png"))
    W = RXESWindow(QtWidgets.QMainWindow())
    # sys.exit(app.exec())
    app.exec()
