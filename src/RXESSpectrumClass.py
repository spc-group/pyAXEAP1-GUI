# :author: Alexander Berno

from axeap.core import Spectra
from numpy import log, array, average
from PyQt6 import QtWidgets


class Dataset:
    """RXES Dataset class to hold checkbox for each dataset."""

    def __init__(self, parent, name: str, data: tuple, num: int, enabled: bool = True):
        """
        Parameters
        ----------
        parent: obj:`RXESWindow`
            Parent is currently not used
        name: :obj:`str`
            Name of dataset (used for checkbox)
        data: :obj:`tuple`
            List or tuple of RXES Spectra (see Spectrum class) from dataset
        num: :obj:`int`
            numerical order of dataset (0, 1, 2, etc.) compared to other datasets (used for ordering)
        enabled: :obj:`bool` (optional)
            Dataset otherwise initiates as enabled, but can be initated as disabled by setting this false
        """

        self.parent = parent
        self.name = name
        self.data = data
        self.num = num
        self.enabled = enabled
        self.disabled = not enabled

        self.box = QtWidgets.QCheckBox(name)
        self.box.setChecked(True)
        self.box.stateChanged.connect(self.switch)

    def switch(self):
        """enables/disables the dataset (flips enabled to disabled and vice versa)"""
        self.enabled = not self.enabled
        self.disabled = not self.disabled


class Spectrum:
    """RXES Spectrum Class"""

    def __init__(
        self,
        parent,
        spectrum: Spectra | list,
        num: int,
        inc: float | None = None,
        i0: float | None = None,
        ul: bool = False,  # means "use log"
        tr: bool = False,  # means "transfer"
        ela: bool = False,  # means "elastic removal"
    ):
        """
        parameters
        ----------
        parent: :obj:`RXESWindow`
            Any RXES Window will work as a parent
        spectrum: :obj:`Spectra`
            source spectrum for which the class is made (has all point data)
        num: :obj:`int`
            The numerical order of the Spectrum
        inc, i0, ul, tr, ela:
            optional parameters for modifying data. inc and i0 are floats, ul tr and ela are booleans.

            inc modifies the incident energy of the spectrum.

            i0 modifies all intensities of the spectrum. This is normalization.

            Setting ul to True takes the log of all intensity values as new intensities. Done after normalization.

            Setting tr takes the transfer energy from the incident and emission.

            Setting ela enables elastic removal (removing peaks where incident = emission).
        """
        if type(spectrum) is list:
            sp = spectrum[0]
            multi = True
        else:
            sp = spectrum
            multi = False

        self.parent = parent
        self.spectrum = spectrum

        if multi:
            intense = average([s.intensities for s in spectrum], axis=0)
        else:
            intense = spectrum.intensities

        if i0 is not None:
            self.inte = array(intense) / i0
        else:
            self.inte = array(intense)

        if ul:
            self.inte = log(self.inte)

        self.em = sp.energies
        if inc is None:
            self.inc = tuple(num for _, _ in enumerate(sp.energies))
        else:
            self.inc = tuple(inc for _, _ in enumerate(sp.energies))

        if ela:
            x = self.inc[0]
            bad = []
            for i, e in enumerate(self.em):
                if x - 5 <= e <= x + 5:
                    bad.append(i)

            if len(bad):
                avgsum = sum(self.inte[: bad[0]]) + sum(self.inte[bad[-1] + 1 :])
                avg = avgsum / (len(self.em) - len(bad))
                for b in bad:
                    self.inte[b] = avg

        if tr:
            self.em = tuple(abs(x - y) for x, y in zip(self.inc, self.em))

        try:
            t = self.parent.filenames[num]
            self.name = t[t.rfind("/") + 1 :]
        except Exception:
            self.name = str(num)
