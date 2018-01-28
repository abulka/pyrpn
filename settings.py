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

MAX_RPN_LABEL_LENGTH = 7
MAX_RPN_ALPHA_STRING_LENGTH = 15

"""
A note on how I'm using flags and registers

Registers 00-NN - allocated as variables as needed
Uppercase Named Registers e.g. "FRED" - created when python code has uppercase variable names
Lowercase Named Registers - not used

pSaveT          - used by pISG
pISGvar         - used by p2mIJfi 

Flags 00, 01    - used in pyrpn template code library
Flags 99, 98    - used in pyrpn template code library ISG

Labels ABCDEFGHIJabcde - allocated for user python functions as needed

Rpn template library labels as follows:
"""
SKIP_LABEL1 = 67        # skip labels are resuable, just ensure they will be found in a forward search
SKIP_LABEL2 = 68
SKIP_LABEL3 = 69
LOCAL_LABEL_FOR_PyLIB = 70
LOCAL_LABEL_FOR_LIST_BACK_JUMP = 71  # unique cos needs to go backwards in jump
LOCAL_LABEL_FOR_LIST_BACK_JUMP2 = 72  # unique cos needs to go backwards in jump
LOCAL_LABEL_FOR_2D_MATRIX_FIND = 73  # unique cos needs to go backwards in loop jump
LOCAL_LABEL_START_FOR_Py = 74  # .. 99
# Flags
FLAG_PYTHON_USE_1 = 99
FLAG_PYTHON_USE_2 = 98
# FLAG_2D_MATRIX_FIND = 97
FLAG_LIST_1D_2D_MODE = '01'
FLAG_LIST_AUTO_CREATE_IF_KEY_NOT_FOUND = '02'

# Parsing related
CMDS_WHO_NEED_LITERAL_NUM_ON_STACK_X = ('VIEW',)
CMDS_WHO_OPERATE_ON_STACK_SO_DISALLOW_NO_ARGS = ('AIP',)
CMDS_WHO_DISALLOW_STRINGS = ('AIP',)
CMDS_WHO_NEED_PARAM_SWAPPING = ('PIXEL',)
