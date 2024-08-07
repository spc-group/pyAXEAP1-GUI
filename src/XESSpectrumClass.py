# :author: Alexander Berno

from PyQt6 import QtWidgets, QtCore
from axeap.core import Spectra

AlignFlag = QtCore.Qt.AlignmentFlag


class Spectrum:
    """Spectrum class. Used to store all data related to each spectra."""

    def __init__(self, parent, spectrum: Spectra, colour: tuple, num: int):
        """
        Parameters
        ----------
        parent: :obj:`XESWindow`
            NOTE: Should be a fully initialized XES Window.
        spectrum: :obj:`Spectra`
            spectrum (or 'Spectra') that is the base of the :obj:`Spectrum`.
        colour: :obj:`tuple`
            colour used with the spectrum.
        num: :obj:`int`
            position of the spectrum on the checks_grid for the parent XES Window.
        """

        self.restack_now = True
        self.parent = parent
        self.energies = spectrum.energies
        self.intensities = spectrum.intensities
        self.spectrum = spectrum

        self.base = spectrum.intensities.copy()
        self.current = self.base.copy()

        self.colour = colour

        t = self.parent.filenames[num - 3]
        self.name = t[t.rfind("/") + 1 :]
        self.box = QtWidgets.QCheckBox()
        self.box.setChecked(True)
        self.box.stateChanged.connect(self.hide)
        self.box.setText(self.name + ", " + str(tuple(int(i) for i in self.colour)))

        self.parent.checks_grid.addWidget(self.box, num, 0, 1, 3, AlignFlag.AlignLeft)

    def increaseIntensity(self, inc, pos):
        self.current[pos] += inc

    def hide(self, s):
        if s != QtCore.Qt.CheckState.Checked.value:
            self.parent.removeSpectrum(self)
        else:
            self.parent.addSpectrum(self)

    def editBoxText(self, text: str | None = None):
        if text is None:
            self.box.setText(self.name + ", " + str(tuple(int(i) for i in self.colour)))
        else:
            self.box.setText(text)
