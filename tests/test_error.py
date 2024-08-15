from ErrorWindow import ErrorWindow
from PyQt6.QtWidgets import QApplication


def test_error():

    error = "emapCalib"
    window = ErrorWindow(error)
    assert (
        window.tlabel.text()
        == "You must select calibration data to calculate the energy map."
    )
    window.close()
    QApplication.processEvents()

    error = "XESemap"
    window = ErrorWindow(error)
    assert (
        window.tlabel.text() == "You must load an energy map to calculate XES spectra."
    )
    window.close()
    QApplication.processEvents()

    error = "minmaxcuts"
    window = ErrorWindow(error)
    assert (
        window.tlabel.text()
        == "Minimum cuts must be lower than or equal to maximum cuts."
    )
    window.close()
    QApplication.processEvents()

    error = "noInfo"
    window = ErrorWindow(error)
    assert (
        window.tlabel.text()
        == "No Information File has been loaded.\nPlease set the energy values or load a file."
    )
    window.close()
    QApplication.processEvents()

    error = "badInfoFile"
    window = ErrorWindow(error)
    assert (
        window.tlabel.text()
        == "Info file is not correct.\nPlease try a different file."
    )
    window.close()
    QApplication.processEvents()

    error = "nodispSpec"
    window = ErrorWindow(error)
    assert (
        window.tlabel.text() == "No spectra are selected. Select spectra to save them."
    )
    window.close()
    QApplication.processEvents()

    error = "avgNoSelected"
    window = ErrorWindow(error)
    assert (
        window.tlabel.text()
        == "No spectra are selected. Select spectra to calculate the average."
    )
    window.close()
    QApplication.processEvents()

    error = "invalidEmIncRXES"
    window = ErrorWindow(error)
    assert window.tlabel.text() == "No Emission or no Incident energy selected."
    window.close()
    QApplication.processEvents()

    window = ErrorWindow()
    assert window.tlabel.text() == "Unknown Error Occurred."
    window.close()
    QApplication.processEvents()
