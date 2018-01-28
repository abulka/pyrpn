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


# Parsing related
CMDS_WHO_NEED_LITERAL_NUM_ON_STACK_X = ('VIEW',)
CMDS_WHO_OPERATE_ON_STACK_SO_DISALLOW_NO_ARGS = ('AIP',)
CMDS_WHO_DISALLOW_STRINGS = ('AIP',)
CMDS_WHO_NEED_PARAM_SWAPPING = ('PIXEL',)

# Specifications of RPN limitations
MAX_RPN_LABEL_LENGTH = 7
MAX_RPN_ALPHA_STRING_LENGTH = 15
USER_DEF_LABELS = 'ABCDEFGHIJabcde'

"""
A note on how I'm using flags and registers

Registers 00-NN - allocated as variables as needed when lowercase variables are encountered
Uppercase Named Registers e.g. "FRED" - created when python code has uppercase variable names
Lowercase Named Registers - not used

Named register pSaveT          - used by pISG
Named register pISGvar         - used by p2mIJfi 
Named registers pX, Py, PZ, pT - used to store stack

Labels ABCDEFGHIJabcde - allocated for user python functions as needed

Rpn Support Function library labels and flags as follows:
"""

# for niceness
LOCAL_LABEL_FOR_PyLIB = 50

# skip labels are resuable, just ensure they will be found in a forward search
SKIP_LABEL1 = 51
SKIP_LABEL2 = 52
SKIP_LABEL3 = 53

# unique cos needs to go backwards in jump
LOCAL_LABEL_FOR_LIST_BACK_JUMP = 54
LOCAL_LABEL_FOR_LIST_BACK_JUMP2 = 55
LOCAL_LABEL_FOR_2D_MATRIX_FIND = 56

# Could be allocated but just easier to set these because they are within a larger code chunk
LIST_PLUS = 57
LIST_MINUS = 58
LIST_CLIST = 59

# all remaining p* functions get allocated from here, via _create_local_labels()
LOCAL_LABEL_START_FOR_Py = 60  # .. 99

# Flags
FLAG_PYTHON_USE_1 = 99
FLAG_PYTHON_USE_2 = 98
FLAG_LIST_1D_2D_MODE = '01'
FLAG_LIST_AUTO_CREATE_IF_KEY_NOT_FOUND = '02'
