from PyQt6 import QtWidgets
import axeap.core as core
import pathlib


class Window(QtWidgets.QMainWindow):
    desktop_directory = None

    def getDesk(self):
        self.desktop_directory = str(pathlib.Path.home() / "Desktop")

    def loadEmap(self):
        if self.desktop_directory is None:
            self.getDesk()
        text = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Energy Map",
            directory=str(self.desktop_directory),
            filter="Numpy Array (*.npy)",
        )
        if not len(text[0]):
            return
        emap = core.EnergyMap.loadFromPath(text[0])
        if len(self.emaps):
            self.emap_combo.insertSeparator(len(self.emaps))
        self.emaps.append(emap)
        self.emap_combo.addItem(emap.name)
