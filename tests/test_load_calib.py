from functions import loadCalib
from axeap.core import ScanSet


def test_load_calib(path, info):
    """Tests that loadCalib returns the scanset and adds info."""
    scans = loadCalib(path, info)
    assert type(scans) is ScanSet
    if info is not None:
        for s in scans:
            assert s.meta["IncidentEnergy"] is not None
