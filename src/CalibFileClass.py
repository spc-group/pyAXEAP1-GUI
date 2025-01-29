# :author: Alexander Berno

from PyQt6 import QtWidgets, QtCore

AlignFlag = QtCore.Qt.AlignmentFlag


class CalibFile:
    """
    Class connected to each individual calibration file.
    Used to create box of all files, and add spinboxes per file.
    """

    def __init__(self, parent, data, name, row, dims, checked: bool = True):
        self.name = name
        self.parent = parent
        self.data = data
        self.enabled = checked
        self.disabled = not checked
        self.dims = dims

        self.name = self.name[self.name.rfind("/") + 1 :]
        if len(self.name) > 16:
            text = self.name[:16] + "..."
        else:
            text = self.name
        self.check = QtWidgets.QCheckBox(text)
        self.check.setToolTip(self.name)
        self.check.setChecked(checked)
        self.check.stateChanged.connect(self.switch)
        self.val = cSpinBox()
        self.val.setMaximum(1000000)
        self.val.setDecimals(4)
        self.val.setMinimumWidth(140)
        self.parent.calib_grid.addWidget(self.check, row, 0, AlignFlag.AlignLeft)
        self.parent.calib_grid.addWidget(self.val, row, 2, AlignFlag.AlignLeft)

    def changeVal(self, val):
        self.val.setValue(val)

    def getVal(self):
        return self.val.value()

    def switch(self):
        self.enabled = not self.enabled
        self.disabled = not self.disabled


class cSpinBox(QtWidgets.QDoubleSpinBox):
    """
    Used exclusively to ignore "wheel events", i.e. scrolling over spinboxes.
    """

    def __init__(self):
        super().__init__()

    def wheelEvent(self, event):
        event.ignore()
