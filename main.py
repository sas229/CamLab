import os, sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.log import init_log
from src.widgets.MainWindow import MainWindow
import logging

if __name__ == '__main__':
    # Create log file instance.
    init_log()
    log = logging.getLogger(__name__)
    log.info('Log file created.')

    # Generate application instance.
    app = QApplication(sys.argv)
    app.setOrganizationName("CUED")
    app.setOrganizationDomain("Civil")
    app.setApplicationName("CamLab")
    app.setWindowIcon(QIcon("assets/NRFIS.svg"))

    # Execute main window.
    main = MainWindow()
    main.show()
    main.setTheme()
    log.info("Timer instantiated.")
    sys.exit(app.exec())

