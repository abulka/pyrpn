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

Flags 00, 01    - used in pyrpn template code library
Flags 99, 98    - used in pyrpn template code library ISG

Labels ABCDEFGHIJabcde - allocated for user python functions as needed

Rpn template library labels as follows:
"""
SKIP_LABEL1 = 68        # skip labels are resuable, just ensure they will be found in a forward search
SKIP_LABEL2 = 69
LOCAL_LABEL_FOR_PyLIB = 70
LOCAL_LABEL1_FOR_ISG_PREP = 71
LOCAL_LABEL2_FOR_ISG_PREP = 72
LOCAL_LABEL_FOR_2D_MATRIX_FIND = 73
LOCAL_LABEL_START_FOR_Py = 74  # .. 99
# Flags
FLAG_PISG_1 = 99
FLAG_PISG_2 = 98
FLAG_2D_MATRIX_FIND = 97

# Parsing related
CMDS_WHO_NEED_LITERAL_NUM_ON_STACK_X = ('VIEW',)
CMDS_WHO_OPERATE_ON_STACK_SO_DISALLOW_NO_ARGS = ('AIP',)
CMDS_WHO_DISALLOW_STRINGS = ('AIP',)
CMDS_WHO_NEED_PARAM_SWAPPING = ('PIXEL',)
