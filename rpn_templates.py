from textwrap import dedent
import inspect
import logging
from logger import config_log
import settings

log = logging.getLogger(__name__)
config_log(log)

class RpnTemplates:
    """
    Houses the PyRPN Support Library

    Comparison expressions
    ----------------------
    For example, re PyGT:
    Python a > b ends up on stack as y:a, x:b so we test y > x
    which translates into operator X<Y? and quick else operator of X≥Y?
    Params (a,b) -> where y:a, x:b returns bool of a > b (params dropped)

    Flags
    -----
    Test any flag, except flag 00 which is reserved.
    Meant for testing system flags, not for Python programming use.
    Disallow FSC? because that is a flow of control command - not relevant in Python.

    These RPN commands are ok, use for setting and clearing system flags, not for Python programming use.
        CF      ok
        SF      ok
    These RPN commands are not allowed in Python because they are flow of control commands - not relevant
    in Python programming.  To test (typically system) flags use the library functions listed, which return a bool.
        FC?C    -
        FS?C    -
        FS?     - use isFS(flag) instead
        FC?     - use isFC(flag) instead
    """

    def __init__(self):
        self.needed_templates = []  # extra fragments that need to be emitted at the end
        self.local_alpha_labels = {}
        self.template_names = self._get_class_attrs()
        self._create_local_alpha_labels()

    PyIsgPr = dedent("""
        LBL "PyIsgPr"  // (z:from, y:to, x:step) -> (ccccccc.fffii)
        CF 99   // neg_case = False 
        CF 98   // have_step = False (other than 1)
        1
        X=Y?
        SF 98   // have_step = True
        RDN
        RCL ST Z
        RCL ST Z // stack now: z:step y:from x:to
        1
        -
        X<>Y     // stack now: z:step y:to-1 x:from 
        RCL ST Z // step
        -        // stack now: z:step y:to-1 x:from-step 
        X>=0?    // if from > 0
        GTO 70   //      easy (non negative)
        ABS      // else from = abs(from)
        SF 99    //      neg_case = True 
        LBL 70
        X<>Y     // stack now: z:step y:from x:to
        1000
        /
        +        // stack now: y:step x:a.bbb
        FS?C 98  // if not have_step
        GTO 71
        RCL ST Z // else step
        100000   //      step = step / 100,000
        /
        +        // stack now: a.bbbnn
        LBL 71
        FS?C 99  // if neg_case
        +/-
        RTN 
        // returns ISG number in form a.bbbnn
        """)

    PyList = dedent("""
        // p 176. HP42S programming manual
        
        LBL "LIST"
        
        CLMENU
        "LIST+"
        KEY 1 XEQ "LIST+"
        "LIST-"
        KEY 2 XEQ "LIST-"
        "CLIST"
        KEY 6 XEQ "CLIST"
        MENU
        STOP
        GTO "LIST"
        
        LBL "LIST+"
        SF 25
        XEQ I
        FC?C 25
        GTO 02
        GROW
        J-
        J+
        WRAP
        
        LBL 00
        STOEL
        FS? 01
        GTO 01
        J+
        X<>Y
        STOEL
        X<>Y
        
        LBL 01
        VIEW "ZLIST"
        RTN
        
        LBL 02
        1
        FS? 01
        1
        FC? 01
        2
        DIM "ZLIST"
        XEQ I
        RDN
        RDN
        GTO 00
        
        LBL "LIST-"
        SF 25
        XEQ I
        FC? 25
        RTN
        J-
        RCLEL
        FS? 01
        GTO 03
        J-
        RCLEL
        
        LBL 03
        DELR
        FS?C 25
        GTO 01
        
        LBL "CLIST"
        CLV "ZLIST"
        RTN
        
        LBL I
        INDEX "ZLIST"
        RTN
        """)

    # Comparison expressions

    PyGT = dedent("""
        LBL "PyGT"  // (y:a, x:b) -> (boolean) of a > b
        CF 00
        X<Y?
        SF 00  // true
        XEQ "_PyDFTB"  // get bool of flag 00
        RTN    
        """)

    PyLT = dedent("""
        LBL "PyLT"  // (y:a, x:b) -> (boolean) of a < b
        CF 00
        X>Y?
        SF 00  // true
        XEQ "_PyDFTB"  // get bool of flag 00
        RTN    
        """)

    PyEQ = dedent("""
        LBL "PyEQ"  // (y:a, x:b) -> boolean of a == b
        CF 00
        X=Y?
        SF 00  // true
        XEQ "_PyDFTB"  // get bool of flag 00
        RTN    
        """)

    PyGTE = dedent("""
        LBL "PyGTE"  // (y:a, x:b) -> (boolean) of a >= b
        CF 00
        X≤Y?
        SF 00  // true
        XEQ "_PyDFTB"  // get bool of flag 00
        RTN    
        """)

    PyLTE = dedent("""
        LBL "PyLT"  // (y:a, x:b) -> (boolean) of a <= b
        CF 00
        X≥Y?
        SF 00  // true
        XEQ "_PyDFTB"  // get bool of flag 00
        RTN    
        """)

    PyNEQ = dedent("""
        LBL "PyNEQ"  // (y:a, x:b) -> boolean of a != b
        CF 00
        X≠Y?
        SF 00  // true
        XEQ "_PyDFTB"  // get bool of flag 00
        RTN    
        """)

    # Logic

    PyBool = dedent("""
        LBL "PyBool"  // (a) -> (bool)
        CF 00
        X≠0?
        SF 00  // is non zero, thus true
        RDN    // drop parameter
        FS? 00
        1
        FC? 00
        0
        RTN
        """)

    Py2Bool = dedent("""
        LBL "Py2Bool"  // (a,b) -> (bool, bool)
        XEQ "PyBool"    
        X<>Y
        XEQ "PyBool"    
        X<>Y
        RTN
        """)

    PyNot = dedent("""
        LBL "PyNot"  // (a) -> boolean of not a
        X≠0?
        SF 00  // is a true value
        RDN
        FS? 00
        0      // false
        FC? 00
        1      // true
        RTN    
        """)

    # Flags

    PyFS = dedent("""
        LBL "PyFS"  // (flag) -> boolean of flag
        CF 00
        FS? IND X
        SF 00
        RDN    // drop parameter
        FS? 00
        1
        FC? 00
        0
        RTN    
        """)

    PyFC = dedent("""
        LBL "PyFS"  // (flag) -> boolean of flag
        CF 00
        FC? IND X
        SF 00
        RDN    // drop parameter
        FS? 00
        1
        FC? 00
        0
        RTN    
        """)

    # Util

    _PyDFTB = dedent("""
        LBL "_PyDFTB"  // (a,b) -> (boolean) of whether flag 00 is set
        RDN
        RDN    // params dropped 
        FS? 00
        1
        FC? 00
        0
        RTN    
        """)

    # Code

    @classmethod
    def _get_class_attrs(cls):
        _attrs_all = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        _attrs_public = [a for a in _attrs_all if not (a[0].startswith('__') and a[0].endswith('__'))]
        names = [tup[0] for tup in _attrs_public]  # we just want the names not the tuples of (name, value)
        return names

    def need_template(self, template):
        assert template in self.template_names
        if template not in self.needed_templates:
            self.needed_templates.append(template)

    def need_all_templates(self):
        self.needed_templates = self.template_names[:]  # copy
        self.needed_templates.remove('PyList')

    def get_user_insertable_pyrpn_cmds(self):
        """
        These are the commands that are exposed to the user and which can be inserted into.
        """
        return {
            'PyFS': {'description': 'is flag set?'},
            'PyFC': {'description': 'is flag clear?'},
        }

    def _create_local_alpha_labels(self):
        """
        Map to local labels, to avoid exposing py rpn library globally.
        Can't map to single letter alpha labels because they are used by user
        functions. Only 14 of them.
        :return:
        """
        next_label = settings.LOCAL_LABEL_START_FOR_Py
        for name in self.template_names:
            self.local_alpha_labels[name] = str(next_label)
            next_label += 1
        # print(self.local_alpha_labels)

# print(RpnTemplates._get_class_attrs())

