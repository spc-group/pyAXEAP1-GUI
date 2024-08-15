# :author: Alexander Berno

"""File Loading classes.

Includes base LoadFile class and all subclasses.

Each class has a fileDialog function and a loadData function.
fileDialog uses Qt dialog windows to get file names.
loadData loads and returns data in a readible form."""

from PyQt6.QtWidgets import QFileDialog
import pathlib
from calibFunctions import loadCalib
from openpyxl import load_workbook
from ErrorWindow import ErrorWindow
import axeap.core as core

desktop_directory = str(pathlib.Path.home() / "Desktop")


class LoadFile:
    """Base file loading class."""

    def fileDialog(parent: any): ...

    def loadData(directory: str | pathlib.Path): ...


class LoadCalibData(LoadFile):
    def fileDialog(parent: any, dtype="tif"):
        if dtype == "tif" or dtype == "tiff":
            direct = QFileDialog.getOpenFileNames(
                parent=parent,
                directory=desktop_directory,
                filter="TIF Files (*.tif *.tiff)",
            )
        else:
            raise TypeError(f"Unknown value '{dtype}' for dtype; try 'tif'")
        if direct[0] != [] and direct[1] != "":
            return direct[0]
        else:
            return None

    def loadData(directory: str):
        return loadCalib(directory)


class LoadInfoData(LoadFile):
    def fileDialog(parent: any):
        info_file = QFileDialog.getOpenFileName(
            parent=parent, directory=desktop_directory
        )
        return info_file

    def loadData(parent: any, directory: str):
        old = parent.info_file
        scans = parent.calibscans
        energies = parent.calib_energies
        if directory[0][-5:] == ".xlsx":
            wb = load_workbook(directory[0], read_only=True)
            ws = wb.worksheets[0]
            for i, scan in enumerate(scans.items):
                line = ws.cell(i + 1, 1).value
                scan.meta["IncidentEnergy"] = line
                energies[i].changeVal(line)
            wb.close()

        elif directory[1] != "":
            try:
                scans.addCalibRunInfo(core.CalibRunInfo(directory[0]))
                for i, e in enumerate(energies):
                    e.changeVal(scans.items[i].meta["IncidentEnergy"])

            except Exception or Warning:
                directory = old
                parent.error = ErrorWindow("badInfoFile")

        else:
            directory = old

        return directory


class LoadTifSpectraData(LoadFile):
    def fileDialog(parent: any):
        dialog = QFileDialog.getOpenFileNames(filter="TIF Files (*.tif *.tiff)")
        if dialog is None or len(dialog[0]) == 0:
            return None
        else:
            return dialog[0]

    def loadData(): ...
