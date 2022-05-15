import os, sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from log import init_log
from widgets.MainWindow import MainWindow
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
    
    # Get directory of icon.
    bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    icon_path = os.path.abspath(os.path.join(bundle_dir,"assets/NRFIS.png"))   
    app.setWindowIcon(QIcon(icon_path))

    # Execute main window.
    main = MainWindow()
    main.show()
    main.setTheme()
    log.info("Timer instantiated.")
    sys.exit(app.exec())

