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
CMDS_WHO_NEED_PARAM_SWAPPING = []  # ('PIXEL',)
RPN_UNSUPPORTED = ['NOT', 'OR', 'AND', 'CLST', 'CLX']
LIST_UNSUPPORTED = ('cmp', 'index', 'count', 'extend', 'insert', 'remove', 'reverse', 'sort')
DICT_UNSUPPORTED = ('clear', 'copy', 'fromkeys', 'get', 'items', 'setdefault', 'update', 'values')
MATRIX_UNSUPPORTED = ('INDEX', 'STOIJ', 'RCLIJ', 'PUTM', 'GETM', 'INSR', 'DELR', 'DIM', 'GROW', 'WRAP', 'SIMQ', 'GROW', 'WRAP')

"""
HP42S commands can be called by an equivalent Python function.  There are three scenarios
    - pure:     one to one mapping of the name e.g. PSE() to PSE
    - renamed:  renamed out of symbol necessity e.g. StatREG() to ΣREG
    - replaced: replaced due to conceptual change e.g. isFS() to pFS rather than FS?
"""

RPN_CMD_TO_PYTHON_RENAMED = {
    '%':        'Percent',          # renamed mappings to original HP42S commands
    '%CH':      'PercentCH',
    '1/X':      'Reciprocal',
    '10↑X':     'CommonExp',
    'ALLΣ':     'ALLStat',
    'BASE+':    'BASEplus',
    'BASE+/–':  'BASEplusMinus',
    'BASEx':    'BASEtimes',
    'BASE÷':    'BASEdivide',
    'BASE–':    'BASEminus',
    'E↑X':      'Eto',
    'E↑X-1':    'EtoMinus1',
    'HMS+':     'HMSplus',
    'HMS–':     'HMSminus',
    'LINΣ':     'LINStat',
    'LN1+X':    'LN1plus',
    'N!':       'Factorial',
    'RDX,':     'RDXcomma',
    'RDX.':     'RDXperiod',
    'Σ+':       'StatPlus',
    'Σ-':       'StatMinus',
    'ΣREG':     'StatREG',
    'ΣREG?':    'StatWhichREG',
    '→DEC':     'toDEC',
    '→DEG':     'toDEG',
    '→HMS':     'toHMS',
    '→HR':      'toHR',
    '→OCT':     'toOCT',
    '→POL':     'toPOL',
    '→RAD':     'toRAD',
    '→REC':     'toREC',

    'AVIEW':    'print',            # extras
    'EDITN':    'EDIT',
    'pMxLen':   'len',

    'pFS':      'isFS',             # mapped to replacement rpnlib functions
    'pFC':      'isFC',
    'pREAL':    'isREAL',
    'pBIT':     'testBIT',
    'pCPX':     'isCPX',
    'pMAT':     'isMAT',
    'pSTR':     'isSTR',
}
RPN_TO_RPNLIB_SPECIAL = {           # HP42S commands to Python replacement (only used by cmd list gen)
    'FS?':      'isFS',
    'FC?':      'isFC',
    'REAL?':    'isREAL',
    'BIT?':     'testBIT',
    'CPX?':     'isCPX',
    'MAT?':     'isMAT',
    'STR?':     'isSTR',
}
PYTHON_CMD_TO_RPN = {v: k for k, v in RPN_CMD_TO_PYTHON_RENAMED.items()}  # Handy backwards lookup
RPN_TO_RPNLIB_SPECIAL_REVERSE = {v: k for k, v in RPN_TO_RPNLIB_SPECIAL.items()}  # Handy backwards lookup
PYLIB_INSERTABLE_WHEN_ORIGINAL_REPLACED = {  # So that converter knows that these are not user functions - cos these don't exist in PYTHON_CMD_TO_RPN
    'pFS': {'description': 'is flag set?'},
    'pFC': {'description': 'is flag clear?'},
    'pREAL': {'description': 'is Real?'},
    'pBIT': {'description': 'test the xth bit of y.'},
    'pCPX': {'description': 'is complex number?'},
    'pMAT': {'description': 'is matrix?'},
    'pSTR': {'description': 'is string?'},

    'pMxLen': {'description': 'length of list or dict'},
}
NUM_PARAMS_UNSPECIFIED = -1

# Specifications of RPN limitations
MAX_RPN_LABEL_LENGTH = 7
MAX_RPN_ALPHA_STRING_LENGTH = 15
USER_DEF_LABELS = 'ABCDEFGHIJabcde'

"""
A note on how I'm using flags and registers

Registers 00-NN - allocated as variables as needed when lowercase variables are encountered
Uppercase Named Registers e.g. "FRED" - created when python code has uppercase variable names
Lowercase Named Registers - not used unless # rpn: named added to Python code as a comment.

Named register pSaveT          - used by pISG
Named register pISGvar         - used by p2MxIJ 
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
FLAG_PYTHON_RPNLIB_GENERAL_PURPOSE = '00'
FLAG_LIST_1D_2D_MODE = '01'
FLAG_LIST_AUTO_CREATE_IF_KEY_NOT_FOUND = '02'
FLAG_PYTHON_USE_1 = 99
FLAG_PYTHON_USE_2 = 98
