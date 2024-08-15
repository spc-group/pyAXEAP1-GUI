import numpy as np
from calibFunctions import getCoordsFromScans as gCFS


def single_scan(scan, cuts):
    no_cut = gCFS(scan, reorder=False)
    # default cuts should be (5,100)
    assert np.min(no_cut) >= 5
    assert np.max(no_cut) <= 100

    cut = gCFS(scan, reorder=False, cuts=cuts)
    assert np.min(cut) >= cuts[0]
    assert np.max(cut) <= cuts[1]


def single_scan_reorder(scan, cuts):
    # On reorder, laout becomes [[x1,...],[y1,...],[s1,...]]

    no_cut = gCFS(scan, reorder=True)
    # default cuts should be (5,100)
    assert min(no_cut[2]) >= 5
    assert max(no_cut[2]) <= 100

    cut = gCFS(scan, reorder=True, cuts=cuts)
    assert min(cut[2]) >= cuts[0]
    assert max(cut[2]) <= cuts[1]


def multi_scan(scans, cuts):
    no_cut = gCFS(scans, reorder=False)
    # default cuts should be (5,100)
    assert np.min(no_cut) >= 5
    assert np.max(no_cut) <= 100

    cut = gCFS(scans, reorder=False, cuts=cuts)
    assert np.min(cut) >= cuts[0]
    assert np.max(cut) <= cuts[1]

    assert len(no_cut) == len(scans)
    assert len(cut) == len(scans)


def multi_scan_reorder(scans, cuts):
    no_cut = gCFS(scans, reorder=True)
    # default cuts should be (5,100)
    for scan in no_cut:
        assert min(scan[2]) >= 5
        assert max(scan[2]) <= 100

    cut = gCFS(scans, reorder=True, cuts=cuts)
    for scan in cut:
        assert min(scan[2]) >= cuts[0]
        assert max(scan[2]) <= cuts[1]

    assert len(no_cut) == len(scans)
    assert len(cut) == len(scans)
