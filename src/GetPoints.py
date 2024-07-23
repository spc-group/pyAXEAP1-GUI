# :author: Alex Berno

from PyQt6 import QtCore
from calibFunctions import getCoordsFromScans
from axeap.core import ScanSet


class GetPoints(QtCore.QObject):
    """
    Class used to retrieve points asynchronously from files.
    Works using Qt threads and emits points as they're calculated.
    """

    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(object)

    def __init__(self, scans: ScanSet, cuts=None):
        super(GetPoints, self).__init__()
        self.scans = scans
        self.cuts = cuts

    def run(self):
        if self.cuts is not None:
            cuts = self.cuts
        else:
            cuts = (3, 100)
        for i in self.scans:
            points = getCoordsFromScans(i, reorder=True, cuts=cuts)
            self.progress.emit(points)
        self.finished.emit()
