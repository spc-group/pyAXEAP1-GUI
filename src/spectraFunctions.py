# :author: Alexander Berno

"""
Spectra functions.

This file contains functions used for calculating XES and RXES spectra.
XES and RXES spectra are calculated using the same functions.
"""

from pathlib import Path
from axeap import core
import numpy as np
from FileLoad import LoadH5Data


def calcDataForSpectra(emap: core.EnergyMap):
    """
    Simple function for calculating data used in calculating Spectra.
    Useful to have as stand-alone in case these calculations would otherwise
    be done MANY times.
    This function can be skipped when calculating Spectra.

    Returns
    -------
    :obj:`dict`
        Contains 'evals','evres','minenergy','maxenergy', 'energies', and 'emap_energies'.
        Designed to be used with 'calcXESSpectra'."""

    evals = emap.values
    evres = emap.eres
    minenergy = np.min(evals, initial=1000000, where=evals > 0)
    maxenergy = np.max(evals, initial=0, where=evals > 0)
    energies = np.arange(minenergy, maxenergy + evres, evres)
    emap_energies = []
    for x in range(evals.shape[0]):
        for y in range(evals.shape[1]):
            energy = evals[x, y]
            if energy > 0:
                emap_energies.append(energy)
    return {
        "evals": evals,
        "evres": evres,
        "minenergy": minenergy,
        "maxenergy": maxenergy,
        "energies": energies,
        "emap_energies": emap_energies,
    }


def calcSpectra(
    file_dir: Path | tuple,
    emap: core.EnergyMap,
    data: dict | None,
    dtype: str | None = None,
):
    """
    Calculates spectra for XES and RXES scans using a given energy map.

    Parameters
    ----------
    file_dir: directory, or :obj:`tuple`
        accepts a file directory, list of file directories, or folder directory.
        this is the directory of the scan files to be the base of the spectra calculation.
    emap: :obj:`core.emap.EnergyMap`
        energy map for calculating spectra. should be made using calibration data.
        NOTE: is no longer explicitly required, can be :obj:`None` or anything else.
    data: :obj:`tuple`
        has evals, evres, minenergy, maxenergy, energies, and emap_energies.
        created from 'calcDataForSpectra' function.

    Returns
    -------
    :obj:`core.spectra.Spectra`
    or list of :obj:`core.spectra.Spectra`
    """
    energy = []
    i0 = []
    if dtype == "tif" or dtype == "tiff" or dtype is None:
        try:
            scans = core.ScanSet.loadFromPath(file_dir)
            if len(scans.items) == 0:
                scans = core.Scan.loadFromPath(file_dir)
        except Exception:
            scans = []
            for i in file_dir:
                scans.append(core.Scan.loadFromPath(i))
            scans = core.ScanSet(scans)
    elif dtype == "h5py":
        images, energy, i0 = LoadH5Data.loadData(file_dir)
        scans = []
        for img in images:
            scans.append(core.Scan(np.swapaxes(img, 0, 1)))
        scans = core.ScanSet(scans)
    else:
        raise TypeError(f"unknown dtype {dtype}, only accepts tif or h5py")

    if data is None:
        data = calcDataForSpectra(emap)

    evals = data["evals"]
    evres = data["evres"]  # not currently needed
    minenergy = data["minenergy"]
    maxenergy = data["maxenergy"]
    energies = data["energies"]
    emap_energies = data["emap_energies"]

    if type(scans) is core.ScanSet:
        spectra = []
        for i in scans:
            img = i.getImg()
            emap_energy_weights = []
            for x in range(evals.shape[0]):
                for y in range(evals.shape[1]):
                    if evals[x, y] > 0:
                        try:
                            emap_energy_weights.append(img[x, y])
                        except IndexError:
                            emap_energy_weights.append(0)
            hist_intensities, _ = np.histogram(
                emap_energies,
                bins=len(energies),
                range=(minenergy, maxenergy),
                weights=emap_energy_weights,
            )
            spectvals = np.stack((energies, hist_intensities)).T
            spectra.append(core.Spectra(spectvals[:, 0], spectvals[:, 1]))
            # The below functions are kept here as reference
            # spectvals = core.spectra.calcSpectra(evals, img, evres)
            # emap.calcSpectra

    else:
        img = scans.getImg()
        emap_energy_weights = []
        for x in range(evals.shape[0]):
            for y in range(evals.shape[1]):
                if evals[x, y] > 0:
                    try:
                        emap_energy_weights.append(img[x, y])
                    except IndexError:
                        emap_energy_weights.append(0)
        hist_intensities, _ = np.histogram(
            emap_energies,
            bins=len(energies),
            range=(minenergy, maxenergy),
            weights=emap_energy_weights,
        )
        spectvals = np.stack((energies, hist_intensities)).T
        spectra = core.Spectra(spectvals[:, 0], spectvals[:, 1])

    return spectra, energy, i0
