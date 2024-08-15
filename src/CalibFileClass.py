# :author: Alexander Berno

from PyQt6 import QtWidgets, QtCore

AlignFlag = QtCore.Qt.AlignmentFlag


class CalibFile:
    """
    Class connected to each individual calibration file.
    Used to create box of all files, and add spinboxes per file.
    """

    def __init__(self, parent, name, row):
        self.name = name
        self.parent = parent

        self.name = self.name[self.name.rfind("/") + 1 :]
        if len(self.name) > 16:
            text = self.name[:16] + "..."
        else:
            text = self.name
        self.label = QtWidgets.QLabel(text)
        self.val = cSpinBox()
        self.val.setMaximum(1000000)
        self.val.setDecimals(4)
        self.val.setMinimumWidth(140)
        self.parent.calib_grid.addWidget(self.label, row, 0, AlignFlag.AlignLeft)
        self.parent.calib_grid.addWidget(self.val, row, 2, AlignFlag.AlignLeft)

    def changeVal(self, val):
        self.val.setValue(val)

    def getVal(self):
        return self.val.value()


class cSpinBox(QtWidgets.QDoubleSpinBox):
    """
    Used exclusively to ignore "wheel events", i.e. scrolling over spinboxes.
    """

    def __init__(self):
        super().__init__()

    def wheelEvent(self, event):
        event.ignore()
