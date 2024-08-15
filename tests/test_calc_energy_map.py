from calibFunctions import calcEnergyMap
import numpy as np
import axeap.core as core


def test_energy_map(scanset, points, rois):
    emap = calcEnergyMap(scanset, points, rois)
    assert type(emap) is core.EnergyMap
