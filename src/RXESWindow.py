# :author: Alexander Berno

import pyqtgraph as pg
import sys

from PyQt6 import QtWidgets, QtCore, QtGui
import matplotlib
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

matplotlib.use("QtAgg")

AlignFlag = QtCore.Qt.AlignmentFlag


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(projection="3d")
        super(MplCanvas, self).__init__(fig)


class RXESWindow(QtWidgets.QMainWindow):
    """Window for viewing RXES data"""

    def __init__(self, parent):
        super(RXESWindow, self).__init__()

        # Default Values
        self.parent = parent

        # 3D canvas
        self.sc3d = MplCanvas(self, width=4, height=3, dpi=100)
        toolbar = NavigationToolbar(self.sc3d, self)

        self.ax = self.sc3d.axes
        self.ax.scatter3D(
            (0, 0, 0, 0, 1, 1, 1, 1),
            (0, 0, 1, 1, 0, 0, 1, 1),
            (0, 1, 0, 1, 0, 1, 0, 1),
            color=("r", "g", "b", "r", "g", "b", "r", "g"),
        )
        self.ax.plot3D((0, 1), (1, 0), (0, 1), c="b")
        self.ax.set_xlabel("Incident")
        self.ax.set_ylabel("Emission")
        # self.ax.set_zlabel("Intensity")
        self.ax.view_init(25, 45, 0)
        self.sc3d.draw()

        # 2D canvas
        self.sc2d = pg.plot()
        self.sc2d.setBackground("w")
        label_style = {"color": "#444", "font-size": "14pt"}
        self.sc2d.plotItem.getAxis("left").setLabel(text="Emission", **label_style)
        self.sc2d.plotItem.getAxis("bottom").setLabel(text="Incident", **label_style)
        self.sc2d.setFixedSize(400, 300)

        widget = QtWidgets.QWidget()
        self.mlayout = QtWidgets.QGridLayout(widget)
        self.mlayout.addWidget(toolbar, 0, 0, AlignFlag.AlignLeft)
        self.mlayout.addWidget(self.sc3d, 1, 0, AlignFlag.AlignCenter)
        self.mlayout.addWidget(self.sc2d, 1, 1, 1, 2, AlignFlag.AlignCenter)
        # self.mlayout.setColumnMinimumWidth(2, 500)

        self.setCentralWidget(widget)
        self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icons/spc-logo-nobg.png"))
    W = RXESWindow(QtWidgets.QMainWindow())
    # sys.exit(app.exec())
    app.exec()
