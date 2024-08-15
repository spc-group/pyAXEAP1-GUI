# :author: Alexander Berno

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

        # default minimum cuts section
        mincuts_label = QtWidgets.QLabel("Default Minimum Cuts:")
        mincuts = self.settings["default_min_cuts"]
        self.mincuts_box = QtWidgets.QSpinBox()
        self.mincuts_box.setFixedWidth(100)
        self.mincuts_box.setMaximum(1000000000)
        self.mincuts_box.setValue(int(mincuts))

        # default maximum cuts section
        maxcuts_label = QtWidgets.QLabel("Default Maximum Cuts:")
        maxcuts = self.settings["default_max_cuts"]
        self.maxcuts_box = QtWidgets.QSpinBox()
        self.maxcuts_box.setFixedWidth(100)
        self.maxcuts_box.setMaximum(1000000000)
        self.maxcuts_box.setValue(int(maxcuts))

        # save and cancel buttons
        save = QtWidgets.QDialogButtonBox.StandardButton.Save
        reset = QtWidgets.QDialogButtonBox.StandardButton.Reset
        cancel = QtWidgets.QDialogButtonBox.StandardButton.Cancel
        buttons = QtWidgets.QDialogButtonBox(save | reset | cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(reset).clicked.connect(self.resetSettings)

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
        settings = {"default_min_cuts": mincuts, "default_max_cuts": maxcuts}
        self.saveSettings(settings)
        super().accept()

    def saveSettings(self, settings):
        mincuts = settings["default_min_cuts"]
        maxcuts = settings["default_max_cuts"]
        text = (
            "#default is 3"
            + f"\ndefault_min_cuts = {str(mincuts)}"
            + "\n#default is 10000"
            + f"\ndefault_max_cuts = {str(maxcuts)}"
        )
        with open("settings.ini", "w") as f:
            f.seek(0)
            f.truncate()
            f.write(text)
            f.close()

    def resetSettings(self):
        defaults = self.getDefaultSettings()
        self.mincuts_box.setValue(int(defaults["default_min_cuts"]))
        self.maxcuts_box.setValue(int(defaults["default_max_cuts"]))

    def getDefaultSettings(self):
        settings = {"default_min_cuts": "3", "default_max_cuts": "10000"}
        return settings
