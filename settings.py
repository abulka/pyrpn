import os

LOG_FILENAME = 'debug.log'
LOG_TO_CONSOLE = True
LOG_AST_CHILDREN_COMPLETE = False

PRODUCTION = 'I_AM_ON_HEROKU' in os.environ
if PRODUCTION:
    LOG_TO_CONSOLE = True
