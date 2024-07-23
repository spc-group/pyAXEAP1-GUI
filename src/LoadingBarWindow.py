from PyQt6.QtWidgets import QProgressDialog


class LoadingBarWindow(QProgressDialog):
    """Window to handle loading bars. any loading bar window is using this class."""

    def __init__(self, message: str, num: int, *args, **kwargs):
        super(LoadingBarWindow, self).__init__(*args, **kwargs)

        self.setLabelText(message)
        self.setAutoClose(True)
        self.canceled.connect(self.cancel)
        self.setValue(0)
        self.setMaximum(num)

        self.show()

    def add(self):
        self.setValue(self.value() + 1)

    def cancel(self):
        pass
