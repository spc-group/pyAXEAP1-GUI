from GetPoints import GetPoints
from PyQt6.QtCore import pyqtBoundSignal
from PyQt6.QtCore import QThread


def test_get_points_init(scans):
    """Does the GetPoints class have every expected type saved."""
    gp = GetPoints(scans)

    # Check that each object is the correct type
    assert type(gp.finished) is pyqtBoundSignal
    assert type(gp.progress) is pyqtBoundSignal
    assert type(gp.scans) is type(scans)


def test_get_points_run(scans):
    """
    Does the class get points from scans properly.
    Does the class emit values and states correctly.
    Does the
    """

    def addpoints(p):
        global points
        points.append(p)

    def runisfalse():
        global run
        run = False

    global run
    run = True
    global points
    points = []
    gp = GetPoints(scans)
    thread = QThread()
    gp.moveToThread(thread)
    thread.started.connect(gp.run)
    gp.finished.connect(thread.quit)
    gp.finished.connect(gp.deleteLater)
    gp.finished.connect(runisfalse)
    thread.finished.connect(thread.deleteLater)
    gp.progress.connect(addpoints)

    thread.start()

    while run:
        continue
    assert points != [] if len(scans) != 0 else points == []
    assert not run
    assert thread is None
    assert gp is None
