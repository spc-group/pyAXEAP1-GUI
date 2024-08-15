from calibFunctions import approximateROIs
import numpy as np


def test_approx_rois(numcrystals, mincuts, maxcuts, scan, points):
    # min_s = 1000
    # max_s = 0
    # for p in points:
    #     if min(p[2]) < min_s:
    #         min_s = min(p[2])
    #     if max(p[2]) > max_s:
    #         max_s = max(p[2])

    hrois, vrois = approximateROIs(numcrystals, mincuts, maxcuts, scan, points)

    assert len(hrois) == numcrystals
    assert len(vrois) == numcrystals

    min_x = np.min(hrois)
    max_x = np.max(hrois)
    min_y = np.min(vrois)
    max_y = np.max(vrois)

    # The +10 and -10 are for "extra space" that might be added in approximation
    for p in points:
        assert min_x >= (min(p[0]) - 10)
        assert max_x <= (max(p[0]) + 10)
        assert min_y >= (min(p[1]) - 10)
        assert max_y <= (max(p[1]) + 10)
