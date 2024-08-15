from calibFunctions import loadCalib
from axeap.core import ScanSet


def test_load_calib(file_path, run_info, energies):
    """Tests that loadCalib returns the scanset and adds info.
    Expected that 'energies' is in the same file order as 'file_path'."""
    scans = loadCalib(file_path, run_info)
    assert type(scans) is ScanSet
    if run_info is not None:
        for i, s in enumerate(scans):
            if energies is not None:
                assert s.meta["IncidentEnergy"] == energies[i]
            else:
                assert s.meta["IncidentEnergy"] is not None
