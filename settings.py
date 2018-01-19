import os

LOG_FILENAME = 'debug.log'
LOG_TO_CONSOLE = False
LOG_AST_CHILDREN_COMPLETE = False

APP_DIR = os.path.dirname(os.path.realpath(__file__))

PRODUCTION = 'I_AM_ON_HEROKU' in os.environ
LOCAL = not PRODUCTION

if PRODUCTION:
    LOG_TO_CONSOLE = True

ADMIN = LOCAL
# ADMIN = False
# ADMIN = True

"""
A note on how I'm using flags and registers

Registers 00-NN - allocated as variables as needed
Uppercase Named Registers e.g. "FRED" - created when python code has uppercase variable names
Lowercase Named Registers - not used

Labels ABCDEFGHIJabcde - allocated for user python functions as needed
Labels 70, 71   - used in pyrpn template code library ISG
Labels 80-NN    - used as entry points for pyrpn library functions if deploying locally

Flags 00, 01    - used in pyrpn template code library
Flags 99, 98    - used in pyrpn template code library ISG
"""
LOCAL_LABEL_FOR_PyLIB = 80
LOCAL_LABEL_START_FOR_Py = 81