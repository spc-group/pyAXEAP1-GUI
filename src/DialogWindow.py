from PyQt6 import QtWidgets


class DialogWindow(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(DialogWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Dialog")

        buttons = (
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonbox = QtWidgets.QDialogButtonBox(buttons)
        self.buttonbox.accepted.connect(self.accept)
        self.buttonbox.rejected.connect(self.reject)

    def accept(self):
        super().accept()

    def reject(self):
        super().reject()
