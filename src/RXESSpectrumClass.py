# :author: Alexander Berno

from axeap.core import Spectra


class Spectrum:
    def __init__(self, parent, spectrum: Spectra, num: int):
        self.parent = parent
        self.spectrum = spectrum
        self.intensities = spectrum.intensities
        self.emission = spectrum.energies
        self.incident = tuple(num for _, _ in enumerate(spectrum.energies))
        self.em, self.inc, self.inte = (self.emission, self.incident, self.intensities)

        t = self.parent.filenames[num]
        self.name = t[t.rfind("/") + 1 :]

    def setColours(self, minn, maxx, rrange, colours):
        points = []
        for i, x in enumerate(self.inc):
            for j, y in enumerate(self.em):
                if minn <= self.inte[j] <= rrange[0]:
                    col = colours[0]
                for k, num in enumerate(rrange[1:]):
                    if k == len(rrange) - 2:
                        col = colours[-1]
                        break
                    elif num <= self.inte[j] <= rrange[k + 2]:
                        col = colours[k]
                        break
                points.append({"pos": (x, y), "brush": col})
                # points.append(((x, self.inc[i + 1]), (y, self.em[j + 1]), col))

        return points
