import os, sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from log import init_log
from ctypes import WinDLL
import config as global_config

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

    # Check for the camera drivers and set the camera_enabled flag.
    try:
        if (sys.version_info.major == 3 and sys.version_info.minor >= 8) or (sys.version_info.major > 3):
            dll = WinDLL('GxIAPI.dll', winmode=0)
            global_config.camera_enabled = True
        else:
            dll = WinDLL('GxIAPI.dll')
            global_config.camera_enabled = True
    except OSError as e:
        global_config.camera_enabled = False
        log.warning(f"Could not load GxIAPI.dll: {e}")

    # Import main window once the camera flag is set.
    from widgets.MainWindow import MainWindow

    # Execute main window.
    main = MainWindow()
    main.show()
    main.set_theme()
    log.info("Timer instantiated.")
    sys.exit(app.exec())

