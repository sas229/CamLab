import logging
import colorlog
import os
import sys
import platform

def init_log():
    """Function to initialise the log file."""
    # Get platform and define destination for the logging file.
    operating_system = platform.system()
    home_dir = os.path.expanduser( '~' )
    if operating_system == "Windows":
        log_dir = os.path.abspath(os.path.join(home_dir,"AppData/CamLab"))
        isdir = os.path.isdir(log_dir) 
        if isdir == False:
            os.mkdir(log_dir)
        log_file = os.path.abspath(os.path.join(home_dir,"AppData/CamLab/CamLab.log"))
    elif operating_system == "Linux":
        log_dir = os.path.abspath(os.path.join(home_dir,".camlab"))
        isdir = os.path.isdir(log_dir) 
        if isdir == False:
            os.mkdir(log_dir)
        log_file = os.path.abspath(os.path.join(home_dir,".camlab/CamLab.log"))

    # Delete log file if already in existence.
    if os.path.exists(log_file):
        os.remove(log_file)

    # Log settings.
    log_format = (
        '%(asctime)s - '
        '%(name)s - '
        '%(funcName)s - '
        '%(levelname)s - '
        '%(message)s'
    )
    bold_seq = '\033[1m'
    colorlog_format = (
        f'{bold_seq} '
        '%(log_color)s '
        f'{log_format}'
    )
    colorlog.basicConfig(format=colorlog_format)
    log = logging.getLogger(__name__)

    logging.basicConfig(
        pathname=log_file,
        format="%(asctime)s | %(funcName)s | %(levelname)s: %(message)s",
        level=logging.DEBUG
    )

    # Output full log.
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(1)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(fh)

    return