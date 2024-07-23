# :author: Alexander Berno

"""
Calibration functions.

This file contains functions used for calibration.
"""

from pathlib import Path
from axeap import core
from axeap.core import conventions as cnv
from scipy import interpolate
import os
import numpy as np


def loadCalib(file_dir: Path | tuple, run_info: str | None = None):
    """Loads scans from each scan file.
    Assumed that this is only used to load calibration scans.

    Parameters
    ----------
    file_dir: directory, or tuple
        should be a path to a folder containing the calibration files
        or a list of paths to each individual calibration file.
    run_info: directory, optional
        this should be a path to the calibration run info file, the file
        titled the same as the calibration folder.
    validate: boolean, optional
        default value is True.
        choose whether or not to validate the scans before returning them.
        validation requires a run_info file, either contained in the file_dir
        or given explicitly.

    NOTE: run_info should be given when file_dir is list_like or if the
        run info file is not contained in the file_dir directory.

    Returns
    -------
    :obj:`core.ScanSet`
        set of all scans from calibration run.
    """

    inst = (str, os.PathLike)
    if isinstance(file_dir, inst):
        # creates a ScanSet of all scans from the file directory (currently only .tif files)
        calib_scans = core.ScanSet.loadFromPath(file_dir)

    else:
        calib_scans = []
        for i in file_dir:
            calib_scans.append(core.Scan.loadFromPath(i))
        calib_scans = core.ScanSet(calib_scans)

    # adds run info if directory is given
    if run_info is not None:
        calib_scans.addCalibRunInfo(core.CalibRunInfo(run_info))

    return calib_scans


def getCoordsFromScans(
    scans: core.Scan | core.ScanSet,
    reorder: bool = False,
    cuts: tuple = (3, 100),
):
    """Gets the coordinates and intensities of points from scan objects.
    Centralizes image loading since image loading is generally done
    with the intention of then getting coordinates afterward.

    Parameters
    ----------
    scans: :obj:`core.Scan` or :obj:`core.ScanSet`
        expects either a core.Scan object or a list of core.Scan objects.
        the order of the list is the order the coordinates and intensities
        will be returned in.
    reorder: :obj:`bool`
        NOTE: currently, setting to True does nothing.
        default value is False.
        if False, the coordinates and intensities will be placed in their own
        arrays, to be used in matplot plotting.
        Example array:
            ((x1, x2, x3, ...), (x1, y2, y3, ...), (s1, s2, s3, ...))
        if True, they will be reordered as below (NOTE: NOT YET IMPLEMENTED).
        Example tuple:
            ((x1, y1, s1),(x2, y2, s2),(x3, y3, s3),...)
    cuts : :obj:`tuple`, optional
        Pair of values (a,b) where any pixel values with intensity < a
        or intensity > b are masked (ignored).


    Returns
    -------
    if 'scans' is a single scan (:obj:`core.Scan`):
        :obj:`np.ndarray` of coordinates and intensities from that scan.
    if 'scans' is a scanset (:obj:`core.ScanSet`):
        :obj:`tuple` of arrays (:obj:`np.ndarray`) of coordinates and intensities from scans.

    """

    if type(scans) is core.Scan:
        mask = cuts
        scan = scans
        img = scan.img.copy()
        img[np.logical_or(img < mask[0], img > mask[1])] = 0
        xval = []
        yval = []
        sval = []
        for x, _ in enumerate(img):
            for y, _ in enumerate(img[x]):
                if img[x][y]:
                    xval.append(x)
                    yval.append(y)
                    sval.append(img[x][y])
        points = [xval, yval, sval]
        # image = scans.getImg(*args, **kwargs)
        # points = np.array(utils.getCoordsFromImage(image))
        # if reorder:
        #     x = [i[0] for i in points]
        #     y = [i[1] for i in points]
        #     s = [i[2] for i in points]
        #     points = np.array([x, y, s])

    else:
        points = []
        mask = cuts
        for scan in scans:
            img = scan.img.copy()
            img[np.logical_or(img < mask[0], img > mask[1])] = 0
            xval = []
            yval = []
            sval = []
            for x, _ in enumerate(img):
                for y, _ in enumerate(img[x]):
                    xval.append(x)
                    yval.append(y)
                    sval.append(img[x][y])
            points.append([xval, yval, sval])
            # image = scan.getImg(*args, **kwargs)
            # p = np.array(utils.getCoordsFromImage(image))
            # if reorder:
            #     x = [i[0] for i in p]
            #     y = [i[1] for i in p]
            #     s = [i[2] for i in p]
            #     points.append(np.array([x, y, s]))
            # else:
            #     points.append(p)

    return points


def calcEnergyMap(scanset: core.ScanSet, points: list, hrois: list):
    """
    Calculates energy map for a scanset, given the points from the scanset.
    It is assumed that the points are pre-cut (using getCoordsFromScans).

    Parameters
    ----------
    scanset: :obj:`core.ScanSet`
        Scanset where all scans are from. If you wish a scan not to be included,
        remove it from the scanset before running through this function.
    points: :obj:`list`
        List of all points, in format gotten from getCoordsFromScans.
        NOTE: Currently, it is assumed that the points HAVE BEEN REORDERED
        (i.e. reorder was set to True when getCoordsFromScans was run).
    hrois: :obj:`list`
        List of all horizontal regions. Currently only HROIs are used,
        however in future versions, the entire ROI will be used.

    Returns
    -------
    :obj:`core.EnergyMap`
        Energy map for current dataset as a core.EnergyMap object."""

    emap = np.full(scanset.dims, float(-1))
    energies = [s.meta["IncidentEnergy"] for s in scanset]

    for hroi in hrois:
        lox, hix = hroi
        linemodels = {}
        for i, _ in enumerate(scanset):
            linemodels[energies[i]] = np.poly1d(
                np.polyfit(points[i][0], points[i][1], 4, w=points[i][2])
            )
        for xval in range(int(np.ceil(lox)), int(np.ceil(hix))):
            # Fit function to column with energy as a function of pixel height y
            # Based on Bragg's Angle formula, E=a/y for some a value
            known_yvals = [linemodels[energy](xval) for energy in linemodels]
            known_evals = energies
            efunc = interpolate.interp1d(known_yvals, known_evals, kind="cubic")
            for yval in range(
                int(np.ceil(min(known_yvals))), int(max(known_yvals)) - 1
            ):
                emap[xval][yval] = efunc(yval)

        print(f"hroi {hrois.index(hroi)+1} has run of {len(hrois)} hrois.")
    return core.EnergyMap(emap)


def approximateROIs(numcrystals, mincuts, maxcuts, scan, points):
    """
    Approximates the regions of interest (ROIs) for a given scanset.

    Parameters
    ----------
    numcrystals: :obj:`int`
        The number of crystals used in callibration.
    mincuts: :obj:`int`
        the minimum cuts (lowest value to accept). Generally, 3 is alright for this.
    maxcuts: :obj:`int`
        the maximum cuts (highest value to accept). Generally, anything above 100 is alright for this.
    scan: :obj:`Scan`
        Reference scan used to approximate horizontal regions of interest.
        NOTE: Any scan can be used from a set of callibration scans.
    points: :obj:`tuple`
        Array of all points, organized as ((x values), (y values), (brightness values)).

    Returns
    -------
    Horizontal regions of interest (HROIs) and vertical regions of interest (VROIs), as arrays.
    The combination of these regions gives rectangular regions of interest.
    """
    s = scan
    minwidth = s.dims[cnv.X] / 8 / 3
    hrois = core.calcHROIs(
        s.mod(cuts=(mincuts, maxcuts)),
        min_width=minwidth,
        group_buffer=10,
    )
    hrois = list((h.lo, h.hi) for h in hrois)

    to_split = [h for h in hrois if abs(h[1] - h[0]) >= 200]

    for h in to_split:
        index = hrois.index(h)
        hrois.remove(h)
        hrois.insert(index, (h[0], int((h[0] + h[1]) / 2) - 5))
        hrois.insert(index + 1, (int((h[0] + h[1]) / 2) + 5, h[1]))
    del to_split

    while len(hrois) < numcrystals:
        maxhroi = 0
        for i, h in enumerate(hrois):
            if maxhroi < abs(h[1] - h[0]):
                maxhroi = abs(h[1] - h[0])
                maxh = (i, h)
        h = maxh[1]
        hrois.remove(h)
        hrois.insert(maxh[0], (h[0], int((h[0] + h[1]) / 2) - 5))
        hrois.insert(maxh[0] + 1, (int((h[0] + h[1]) / 2) + 5, h[1]))

    maxval = hrois[-1][1]
    minval = hrois[0][0]

    while len(hrois) > numcrystals:
        if (hrois[0][0] - minval) > (maxval - hrois[-1][1]):
            hrois.pop(-1)
        else:
            hrois.pop(0)

    vrois = []
    for h in hrois:
        ymin = 100000
        ymax = 0
        for i in points:
            xs = tuple(
                (i[1][val], u) for val, u in enumerate(i[2]) if h[0] < i[0][val] < h[1]
            )
            ys = tuple(
                y[0]
                for y in xs
                if y[0] > 0 and y[0] < s.dims[cnv.Y] and y[1] >= mincuts
            )
            if len(ys) == 0:
                continue

            imin = min(ys) - 10
            imax = max(ys) + 10
            if ymin > imin:
                ymin = imin
            if ymax < imax:
                ymax = imax

        vrois.append((ymin, ymax))

    return hrois, vrois
