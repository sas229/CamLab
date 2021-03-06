from contextlib import contextmanager

from ..Qt import QtCore, QtGui, QtWidgets

__all__ = ["BusyCursor"]


@contextmanager
def BusyCursor():
    """
    Display a busy mouse cursor during long operations.
    Usage::

        with BusyCursor():
            doLongOperation()

    May be nested. If called from a non-gui thread, then the cursor will not be affected.
    """
    app = QtCore.QCoreApplication.instance()
    in_gui_thread = (app is not None) and (QtCore.QThread.currentThread() == app.thread())
    try:
        if in_gui_thread:
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CursorShape.WaitCursor))
        yield
    finally:
        if in_gui_thread:
            QtWidgets.QApplication.restoreOverrideCursor()
