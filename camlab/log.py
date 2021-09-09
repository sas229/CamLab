import logging
import colorlog
import os
import sys

def init_log():
    # Delete log file if already in existence.
    if os.path.exists("CamLab.log"):
        os.remove("CamLab.log")

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
        filename="CamLab.log",
        format="%(asctime)s | %(funcName)s | %(levelname)s: %(message)s",
        level=logging.DEBUG
    )

    # Output full log.
    fh = logging.FileHandler("CamLab.log")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(1)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(fh)

    return