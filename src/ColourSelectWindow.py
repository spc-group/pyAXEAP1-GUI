from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt
import sys

AlignFlag = Qt.AlignmentFlag


class ColourSelect:
    def __init__(self, parent, col1: tuple | None = None, col2: tuple | None = None):
        self.parent = parent
        self.ogcol1 = col1
        self.ogcol2 = col2

        self.WindowOne = self.ColourWindow(self.ogcol1)
        self.WindowOne.setWindowTitle("Select Colour One")
        self.WindowOne.accepted.connect(self.startWindowTwo)
        self.WindowOne.rejected.connect(self.reject)

    def reject(self):
        self.parent.custom_colour_one = self.ogcol1
        self.parent.custom_colour_one = self.ogcol2

    def startWindowTwo(self):
        self.parent.custom_colour_one = self.WindowOne.selectedColor()
        self.WindowTwo = self.ColourWindow(self.ogcol2)
        self.WindowTwo.setWindowTitle("Select Colour Two")
        self.WindowTwo.accepted.connect(self.getColTwo)
        self.WindowTwo.rejected.connect(self.reject)

    def getColTwo(self):
        self.parent.custom_colour_two = self.WindowTwo.selectedColor()

    class ColourWindow(QtWidgets.QColorDialog):
        def __init__(self, colour):
            super(ColourSelect.ColourWindow, self).__init__(colour)
            self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icons/spc-logo-nobg.png"))
    W = ColourSelect(None, QtGui.QColor(0, 0, 0), QtGui.QColor(255, 255, 255))
    # sys.exit(app.exec())
    app.exec()
