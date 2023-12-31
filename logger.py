import logging
import settings
import os

try:
    os.remove(settings.LOG_FILENAME)
except:
    pass

def config_log(log):
    log.setLevel(logging.DEBUG)

    # formatter = logging.Formatter('%(asctime)-15s %(levelname)s %(message)s')
    formatter = logging.Formatter('%(name)-10s %(levelname)5s %(message)s')
    # formatter = logging.Formatter('%(name)10s %(message)s')
    # formatter = logging.Formatter('%(message)s')   # <----- TRADITIONAL ONE I USED but doesn't work well with ideolog colour highlighter
    # formatter = logging.Formatter('%(levelname)5s %(message)s')

    # create the logging file handler
    fh = logging.FileHandler(settings.LOG_FILENAME)
    fh.setFormatter(formatter)

    # create console logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # add them all
    log.addHandler(fh)  # add handler to logger object
    if settings.LOG_TO_CONSOLE:
        log.addHandler(ch)  # add handler to logger object
