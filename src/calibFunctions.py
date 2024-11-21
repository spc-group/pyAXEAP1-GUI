# :author: Alexander Berno

"""Calibration functions.

This file contains functions used for calibration.
It also contains the energy map calculation function.
"""

from pathlib import Path
from axeap import core
from axeap.core import conventions as cnv
from scipy import interpolate
import os
import numpy as np
import h5py


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
    scans: core.Scan | core.ScanSet | h5py.Dataset,
    reorder: bool = False,
    cuts: tuple = (5, 100),
):
    """Gets the coordinates and intensities of points from scan objects.

    Parameters
    ----------
    scans: :obj:`core.Scan` or :obj:`core.ScanSet`
        expects either a core.Scan object or a list of core.Scan objects.
        the order of the list is the order the coordinates and intensities
        will be returned in.
    reorder: :obj:`bool`
        default value is False.
        if False, the coordinates and intensities will be placed in their own
        arrays, to be used in matplot plotting.

        Example array:
            ((x1, x2, x3, ...), (y1, y2, y3, ...), (s1, s2, s3, ...))

        if True, they will be reordered so each point is separated, as below.

        Example array:
            ((x1, y1, s1), (x2, y2, s2), (x3, y3, s3),...)

    cuts: :obj:`tuple`, optional (Default is (5, 100))
        Pair of values (a,b) where any pixel values with
        'intensity < a' or 'intensity > b' are masked (ignored).


    Returns
    -------
    if 'scans' is a single scan (:obj:`core.Scan`):
        :obj:`np.ndarray` of coordinates and intensities from that scan.
    if 'scans' is a scanset (:obj:`core.ScanSet`):
        :obj:`list` of arrays (:obj:`np.ndarray`) of coordinates and intensities from scans.

    """
    mask = cuts
    if type(scans) is core.Scan:
        scan = scans
        img = scan.img.copy()
        img[np.logical_or(img < mask[0], img > mask[1])] = 0
        xval = []
        yval = []
        sval = []
        if reorder:
            for x, _ in enumerate(img):
                for y, _ in enumerate(img[x]):
                    if img[x][y]:
                        xval.append(x)
                        yval.append(y)
                        sval.append(img[x][y])
            points = [xval, yval, sval]
        else:
            points = [(a, b, c) for a, b, c in zip(xval, yval, sval)]

    elif type(scans) is core.ScanSet:
        points = []
        for scan in scans:
            img = scan.img.copy()
            img[np.logical_or(img < mask[0], img > mask[1])] = 0
            xval = []
            yval = []
            sval = []
            if reorder:
                for x, _ in enumerate(img):
                    for y, _ in enumerate(img[x]):
                        xval.append(x)
                        yval.append(y)
                        sval.append(img[x][y])
                points.append([xval, yval, sval])
            else:
                points.append([(a, b, c) for a, b, c in zip(xval, yval, sval)])

    elif type(scans) is h5py.Dataset:
        raise NotImplementedError("H5 calib files are a work in progress.")
    #     img = scans[0, 0]
    #     points = []
    #     img[np.logical_or(img < mask[0], img > mask[1])] = 0
    #     xval = []
    #     yval = []
    #     sval = []
    #     for x, _ in enumerate(img):
    #         for y, _ in enumerate(img[x]):
    #             if img[x][y]:
    #                 xval.append(x)
    #                 yval.append(y)
    #                 sval.append(img[x][y])

    #     if reorder:
    #         points = [xval, yval, sval]
    #     else:
    #         points = [(a, b, c) for a, b, c in zip(xval, yval, sval)]

    spots = []
    if reorder:
        if type(points[0][0]) is not list:
            for x, y, s in zip(points[0], points[1], points[2]):
                spots.append({"pos": (x, y), "size": s})
        else:
            for i in points:
                for x, y, s in zip(i[0], i[1], i[2]):
                    spots.append({"pos": (x, y), "size": s})
    else:
        pass
    return points, spots


# for each roi: roi = (lox, loy, hix, hiy)
def calcEnergyMap(scanset: core.ScanSet, points: tuple, rois: tuple):
    """Generates an energy map for a given scanset, in given regions.

    NOTE: It is assumed that the size of 'scanset' is the same as 'points'.

    Parameters
    ----------
    scanset: :obj:`core.ScanSet`
        Set of all scans. required for getting energy values and size of images.

        Could easily be replaced by 'energies' and 'img_size' parameters in the future.

    points: :obj:`tuple`
        Set of all points to be used from each scan.

        Expected format:
            data = (xvals, yvals, weights) for data in points

        So overall:
            points = ((s1_xvals, s1_yvals, s1_weights), (s2_xvals, s2_yvals, s2_weights), ...)

    rois: :obj:`tuple`
        All regions of interest (ROIs).

        Expected format:
            roi = (low_x, low_y, high_x, high_y) for roi in rois

        These regions are expected to be rectangles, thus these 4 values are all that is needed.

    returns
    -------
    :obj:`core.EnergyMap`
        This is the energy map created for the given points.
    """

    emap = np.full(scanset.dims, float(-1))
    energies = [s.meta["IncidentEnergy"] for s in scanset]
    for roi in rois:
        lox, loy, hix, hiy = roi
        linemodels = {}
        for i, _ in enumerate(scanset):
            scanpoints = zip(points[i][0], points[i][1], points[i][2])
            scanx, scany, scanw = [], [], []
            for x, y, w in scanpoints:
                if lox <= x <= hix and loy <= y <= hiy:
                    scanx.append(x)
                    scany.append(y)
                    scanw.append(w)
            if len(scanx):
                linemodels[energies[i]] = np.poly1d(
                    np.polyfit(scanx, scany, 4, w=scanw)
                )
            else:
                linemodels[energies[i]] = np.poly1d([-1])

        for xval in range(int(np.ceil(lox)), int(np.ceil(hix))):
            # Fit function to column with energy as a function of pixel height y
            # Based on Bragg's Angle formula, E=a/y for some a value
            known_yvals = tuple(
                (
                    linemodels[energy](xval)
                    if loy <= linemodels[energy](xval) <= hiy
                    else None
                )
                for energy in linemodels
            )
            known_evals = tuple(
                e for i, e in enumerate(energies) if known_yvals[i] is not None
            )
            known_yvals = tuple(y for y in known_yvals if y is not None)

            efunc = interpolate.interp1d(known_yvals, known_evals, kind="cubic")
            for yval in range(
                int(np.ceil(min(known_yvals))), int(max(known_yvals)) - 1
            ):
                emap[xval][yval] = efunc(yval)
        # print(f"roi {rois.index(roi)+1} has run of {len(rois)} rois.")
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
