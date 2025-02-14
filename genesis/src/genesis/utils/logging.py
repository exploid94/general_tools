import logging
import os

import importlib
importlib.reload(logging)

LOGGERS = {}
FORMAT = "[%(asctime)s] - [%(name)s.%(funcName)s]:line[%(lineno)d]: - [%(levelname)s] - %(message)s"

def get_logger(name, folder=None, level=logging.WARNING, write_mode="w+"):
    """Gets the logger for with the given name.

    Args:
        name (str): The name of the logger to get.
        folder (str, optional): The folder to save the output file to.
        level (str, optional): The logger level. Default is logging.WARNING
        write_mode (str, optional): The write mode to set the file handler to. default is 'w+'
        """
    format = FORMAT
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if folder:
        if not os.path.exists(folder):
            os.mkdir(folder)
        file_path = os.path.join(folder, f"{name}.log")
        logging.basicConfig(filename=file_path, filemode=write_mode, level=level, format=format)
    else:
        logging.basicConfig(level=level, format=format)

    if logger not in LOGGERS:
        LOGGERS[name] = logger

    return logger

def debug_mode():
    """Sets all loggers under hh_publishers to debug mode."""
    for logger in LOGGERS:
        LOGGERS[logger].setLevel(logging.DEBUG)

def info_mode():
    """Sets all loggers under hh_publishers to info mode."""
    for logger in LOGGERS:
        LOGGERS[logger].setLevel(logging.INFO)

def warning_mode():
    """Sets all loggers under hh_publishers to warning mode."""
    for logger in LOGGERS:
        LOGGERS[logger].setLevel(logging.WARNING)

def error_mode():
    """Sets all loggers under hh_publishers to error mode."""
    for logger in LOGGERS:
        LOGGERS[logger].setLevel(logging.ERROR)

def set_output_folder(folder, write_mode="w+"):
    """Sets all the loggers to the same output location.

    Args:
        folder (str): The folder you want the output files to be saved to.
        write_mode (str, optional): The write mode to set the file handler to. default is 'w+'
        """
    for name in LOGGERS:
        logger = LOGGERS[name]
        if not os.path.exists(folder):
            os.mkdir(folder)
        file_name = os.path.join(folder, f"{name}.log")
        handler = logging.FileHandler(file_name, write_mode)
        handler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(handler)
