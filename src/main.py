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
    
    # Get directory.
    bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    icon_dir = os.path.abspath(os.path.join(bundle_dir,"assets"))   

    # Set app icon.   
    app_icon = QIcon()
    app_icon.addFile(os.path.abspath(os.path.join(icon_dir,"CamLab_16_16.png")), QSize(16,16))
    app_icon.addFile(os.path.abspath(os.path.join(icon_dir,"CamLab_24_24.png")), QSize(24,24))
    app_icon.addFile(os.path.abspath(os.path.join(icon_dir,"CamLab_32_32.png")), QSize(32,32))
    app_icon.addFile(os.path.abspath(os.path.join(icon_dir,"CamLab_48_48.png")), QSize(48,48))
    app_icon.addFile(os.path.abspath(os.path.join(icon_dir,"CamLab_256_256.png")), QSize(256,256))
    app_icon.addFile(os.path.abspath(os.path.join(icon_dir,"CamLab.png")), QSize(683,683))
    app.setWindowIcon(app_icon)

    # Execute main window.
    main = MainWindow()
    main.show()
    main.setTheme()
    log.info("Timer instantiated.")
    sys.exit(app.exec())

