import logging
import settings
import os

os.remove(settings.LOG_FILENAME)

def config_log(log):
    log.setLevel(logging.DEBUG)

    # formatter = logging.Formatter('%(asctime)-15s %(levelname)s %(message)s')
    # formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    # formatter = logging.Formatter('%(name)10s %(message)s')
    formatter = logging.Formatter('%(message)s')

    # create the logging file handler
    fh = logging.FileHandler(settings.LOG_FILENAME)
    fh.setFormatter(formatter)

    # create console logging
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    # add them all
    log.addHandler(fh)  # add handler to logger object
    if settings.LOG_TO_CONSOLE:
        log.addHandler(ch)  # add handler to logger object
