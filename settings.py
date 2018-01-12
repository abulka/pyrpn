import os

LOG_FILENAME = 'debug.log'
LOG_TO_CONSOLE = False
LOG_AST_CHILDREN_COMPLETE = False

APP_DIR = os.path.dirname(os.path.realpath(__file__))

PRODUCTION = 'I_AM_ON_HEROKU' in os.environ
LOCAL = not PRODUCTION

if PRODUCTION:
    LOG_TO_CONSOLE = True
