from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

AlignFlag = Qt.AlignmentFlag


class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent, settings: dict):
        super(SettingsWindow, self).__init__()

        self.parent = parent
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setFixedSize(260, 180)

        mincuts_label = QtWidgets.QLabel("Default Minimum Cuts:")
        mincuts = self.settings["default_min_cuts"]
        self.mincuts_box = QtWidgets.QSpinBox()
        self.mincuts_box.setFixedWidth(100)
        self.mincuts_box.setMaximum(1000000000)
        self.mincuts_box.setValue(int(mincuts))
        maxcuts_label = QtWidgets.QLabel("Default Maximum Cuts:")
        maxcuts = self.settings["default_max_cuts"]
        self.maxcuts_box = QtWidgets.QSpinBox()
        self.maxcuts_box.setFixedWidth(100)
        self.maxcuts_box.setMaximum(1000000000)
        self.maxcuts_box.setValue(int(maxcuts))

        save = QtWidgets.QDialogButtonBox.StandardButton.Save
        cancel = QtWidgets.QDialogButtonBox.StandardButton.Cancel
        buttons = QtWidgets.QDialogButtonBox(save | cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(mincuts_label, 0, 0, AlignFlag.AlignLeft)
        layout.addWidget(self.mincuts_box, 0, 1, AlignFlag.AlignLeft)
        layout.addWidget(maxcuts_label, 1, 0, AlignFlag.AlignLeft)
        layout.addWidget(self.maxcuts_box, 1, 1, AlignFlag.AlignLeft)
        layout.addWidget(buttons, 2, 0, 1, 2, AlignFlag.AlignHCenter)

        self.setLayout(layout)
        self.show()

    def accept(self):
        mincuts = self.mincuts_box.value()
        maxcuts = self.maxcuts_box.value()
        text = f"""#default is 3
default_min_cuts = {str(mincuts)}
#default is 10000
default_max_cuts = {str(maxcuts)}"""
        with open("settings.ini", "w") as f:
            f.seek(0)
            f.truncate()
            f.write(text)
            f.close()
        super().accept()
