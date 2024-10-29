# :author: Alexander Berno

from axeap.core import Spectra
from numpy import log, array


class Spectrum:
    def __init__(
        self,
        parent,
        spectrum: Spectra,
        num: int,
        inc: float | None = None,
        i0: float | None = None,
        ul: bool = False,  # means "use log"
        tr: bool = False,  # means "transfer"
        ela: bool = False,  # means "elastic removal"
    ):
        self.parent = parent
        self.spectrum = spectrum
        if i0 is not None:
            self.inte = array(spectrum.intensities) / i0
        else:
            self.inte = array(spectrum.intensities)

        if ul:
            self.inte = log(self.inte)

        self.em = spectrum.energies
        if inc is None:
            self.inc = tuple(num for _, _ in enumerate(spectrum.energies))
        else:
            self.inc = tuple(inc for _, _ in enumerate(spectrum.energies))

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
            self.em = tuple(abs(x - y) for x, y in zip(self.em, self.inc))

        t = self.parent.filenames[num]
        self.name = t[t.rfind("/") + 1 :]
