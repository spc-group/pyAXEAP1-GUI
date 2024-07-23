from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

AlignFlag = Qt.AlignmentFlag


class ApproxWindow(QtWidgets.QDialog):
    """Window shown when ROIs are being approximated."""

    def __init__(self, *args, **kwargs):
        super(ApproxWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Number of Crystals")
        self.setMinimumSize(240, 120)
        buttons = (
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        label = QtWidgets.QLabel("Number of Crystals in Experiment:")
        self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setMaximum(100)
        self.spinbox.setMinimumSize(64, 20)
        self.spinbox.setValue(8)
        self.value = 8

        button_box = QtWidgets.QDialogButtonBox(buttons)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(label, 0, 0, alignment=AlignFlag.AlignRight)
        layout.addWidget(self.spinbox, 0, 1, alignment=AlignFlag.AlignLeft)
        layout.addWidget(button_box, 1, 0, 2, 1, alignment=AlignFlag.AlignRight)

        self.setLayout(layout)
        self.show()

    def accept(self):
        self.value = self.spinbox.value()
        super().accept()

    def reject(self):
        self.value = None
        super().reject()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.deleteLater()
