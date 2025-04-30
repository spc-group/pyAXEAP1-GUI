# :author: Alexander Berno

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt
import sys

AlignFlag = Qt.AlignmentFlag


class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent, settings: dict | None):
        super(SettingsWindow, self).__init__()

        self.parent = parent
        if settings is not None:
            self.settings = settings
        else:
            self.settings = self.getDefaultSettings()
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)

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

        # data load type section
        datatype_label = QtWidgets.QLabel("Data Type:")
        datatype = self.settings["data_load_type"]
        self.datatype_box = QtWidgets.QComboBox()
        self.datatype_box.addItem("TIF (*.tif)", "tif")
        self.datatype_box.addItem("h5py/Nexus (*.nx)", "h5py")
        if datatype == "tif":
            self.datatype_box.setCurrentIndex(0)
        elif datatype == "h5py":
            self.datatype_box.setCurrentIndex(1)

        # cmap box
        cmap = self.settings["cmap"]
        cmap_label = QtWidgets.QLabel("Default RXES Contour Map:")
        self.cmap_box = QtWidgets.QComboBox()
        self.cmap_box.addItem("PColor", "pcolor")
        self.cmap_box.addItem("Contour", "contour")
        if cmap == "pcolor":
            self.cmap_box.setCurrentIndex(0)
        elif cmap == "contour":
            self.cmap_box.setCurrentIndex(1)

        # ROI box
        roitype = self.settings["roi_type"]
        roi_label = QtWidgets.QLabel("Method to approximate ROIs:")
        self.roitype_box = QtWidgets.QComboBox()
        self.roitype_box.addItem("Standard", "standard")
        self.roitype_box.addItem("KMeans", "kmeans")
        if roitype == "standard":
            self.roitype_box.setCurrentIndex(0)
        elif roitype == "kmeans":
            self.roitype_box.setCurrentIndex(1)

        # confirm on close box
        confirm = self.settings["confirm_on_close"]
        if confirm == "False" or not confirm:
            confirm = False
        else:
            confirm = True
        self.confirm_box = QtWidgets.QCheckBox("Confirm on close")
        self.confirm_box.setChecked(confirm)

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
        layout.addWidget(self.mincuts_box, 0, 1, AlignFlag.AlignRight)
        layout.addWidget(maxcuts_label, 1, 0, AlignFlag.AlignLeft)
        layout.addWidget(self.maxcuts_box, 1, 1, AlignFlag.AlignRight)
        layout.addWidget(datatype_label, 2, 0, AlignFlag.AlignLeft)
        layout.addWidget(self.datatype_box, 2, 1, AlignFlag.AlignRight)
        layout.addWidget(cmap_label, 3, 0, AlignFlag.AlignLeft)
        layout.addWidget(self.cmap_box, 3, 1, AlignFlag.AlignRight)
        layout.addWidget(roi_label, 4, 0, AlignFlag.AlignLeft)
        layout.addWidget(self.roitype_box, 4, 1, AlignFlag.AlignRight)
        layout.addWidget(self.confirm_box, 5, 0, AlignFlag.AlignLeft)
        layout.addWidget(buttons, 6, 0, 1, 2, AlignFlag.AlignHCenter)

        self.setLayout(layout)
        self.show()

    def accept(self):
        settings = self.getSettings()
        self.saveSettings(settings)
        super().accept()

    def saveSettings(self, settings):
        mincuts = settings["default_min_cuts"]
        maxcuts = settings["default_max_cuts"]
        datatype = settings["data_load_type"]
        confirm = settings["confirm_on_close"]
        cmap = settings["cmap"]
        roitype = settings["roi_type"]

        text = (
            "#default is 3"
            + f"\ndefault_min_cuts = {str(mincuts)}"
            + "\n#default is 10000"
            + f"\ndefault_max_cuts = {str(maxcuts)}"
            + "\n#default is tif"
            + f"\ndata_load_type = {str(datatype)}"
            + "\n#default is False"
            + f"\nconfirm_on_close = {str(confirm)}"
            + "\n#default is pcolor"
            + f"\ncmap = {str(cmap)}"
            + f"\n#default is standard"
            + f"\nroi_type = {str(roitype)}"
        )
        with open("settings.ini", "w") as f:
            f.seek(0)
            f.truncate()
            f.write(text)
            f.close()

    def getSettings(self):
        mincuts = self.mincuts_box.value()
        maxcuts = self.maxcuts_box.value()
        datatype = self.datatype_box.currentData()
        cmap = self.cmap_box.currentData()
        confirm = self.confirm_box.isChecked()
        roitype = self.roitype_box.currentData()

        settings = {
            "default_min_cuts": mincuts,
            "default_max_cuts": maxcuts,
            "data_load_type": datatype,
            "confirm_on_close": confirm,
            "cmap": cmap,
            "roi_type": roitype,
        }
        return settings

    def resetSettings(self):
        defaults = self.getDefaultSettings()
        self.mincuts_box.setValue(int(defaults["default_min_cuts"]))
        self.maxcuts_box.setValue(int(defaults["default_max_cuts"]))
        self.datatype_box.setCurrentIndex(0)
        self.cmap_box.setCurrentIndex(0)
        self.confirm_box.setChecked(False)
        self.roitype_box.setCurrentIndex(0)

    def getFileSettings(self=None):
        try:
            with open("settings.ini", "r") as s:
                lines = s.readlines()
                s.close()
        except Exception:
            return
        settings = {}
        for line in lines:
            if not len(line) or line[0] == "#":
                continue
            if "\n" in line:
                line = line[: line.find("\n")]
            settings[line[: line.find(" =")]] = line[line.find("= ") + 2 :]

        defaults = {
            "default_min_cuts": "3",
            "default_max_cuts": "10000",
            "data_load_type": "tif",
            "confirm_on_close": "True",
            "cmap": "pcolor",
            "roi_type": "standard",
        }

        for setting in defaults:
            if setting not in settings:
                settings[setting] = defaults[setting]
        return settings

    def getDefaultSettings(self=None):
        settings = {
            "default_min_cuts": "3",
            "default_max_cuts": "10000",
            "data_load_type": "tif",
            "confirm_on_close": "True",
            "cmap": "pcolor",
            "roi_type": "standard",
        }
        return settings


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icons/spc-logo-nobg.png"))
    settings = SettingsWindow.getDefaultSettings()
    W = SettingsWindow(None, settings=settings)
    # sys.exit(app.exec())
    app.exec()
