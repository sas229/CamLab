import os, sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from log import init_log
from widgets.MainWindow import MainWindow
import logging

if __name__ == '__main__':
    # Create log file instance.
    init_log()
    log = logging.getLogger(__name__)
    log.info('Log file created.')

    # Get directory.
    bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    path_to_icon = os.path.abspath(os.path.join(bundle_dir,"assets/NRFIS.svg"))

    # Generate application instance.
    app = QApplication(sys.argv)
    app.setOrganizationName("CUED")
    app.setOrganizationDomain("Civil")
    app.setApplicationName("CamLab")
    app.setWindowIcon(QIcon(path_to_icon))

    # Execute main window.
    main = MainWindow()
    main.show()
    main.setTheme()
    log.info("Timer instantiated.")
    sys.exit(app.exec())

