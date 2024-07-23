from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

AlignFlag = Qt.AlignmentFlag


class ErrorWindow(QtWidgets.QDialog):
    """Window called when an "error" occurs, aka incorrect input or action within main GUI."""

    def __init__(self, error: str | None = None, *args, **kwargs):
        super(ErrorWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Error")
        self.setMinimumHeight(120)
        # error syntax is "[attempted calculation/execution] [reason for not working]"
        if error == "emapCalib":
            labeltext = "You must select calibration data to calculate the energy map."
        elif error == "XESemap":
            labeltext = "You must load an energy map to calculate XES spectra."
        elif error == "minmaxcuts":
            labeltext = "Minimum cuts must be lower than or equal to maximum cuts."
        elif error == "noInfo":
            labeltext = "No Information File has been loaded.\nPlease set the energy values or load a file."
        elif error == "badInfoFile":
            labeltext = "Info file is not correct.\nPlease try a different file."
        elif error == "nodispSpec":
            labeltext = "No spectra are selected. Select spectra to save them."
        elif error == "avgNoSelected":
            labeltext = (
                "No spectra are selected. Select spectra to calculate the average."
            )
        else:
            labeltext = "Unknown Error Occurred."

        button = QtWidgets.QDialogButtonBox.StandardButton.Ok
        label = QtWidgets.QLabel(text=labeltext)
        button_box = QtWidgets.QDialogButtonBox(button)
        button_box.accepted.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(button_box, alignment=AlignFlag.AlignCenter)

        self.setLayout(layout)
        self.show()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.deleteLater()
