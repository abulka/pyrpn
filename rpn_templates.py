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
    For example, re pGT:
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
        self._create_local_labels()

    pISG = dedent("""
        LBL "pISG"  // (z:from, y:to, x:step) -> (ccccccc.fffii)
        CF 99   // neg_case = False 
        CF 98   // have_step = False (other than 1)
        1
        IP      // ensure step is an int
        X=Y?
        SF 98   // have_step = True
        RDN
        RCL ST Z
        IP      // ensure from is an int
        RCL ST Z // stack now: z:step y:from x:to
        IP      // ensure to is an int
        1
        -
        
        999      // check don't exceed max 'to' value of 999 (ISG ccccccc.fffii)
        X<Y?
        XEQ "p__1ErR"
        RDN
        
        X<>Y     // stack now: z:step y:to-1 x:from 
        RCL ST Z // step
        -        // stack now: z:step y:to-1 x:from-step 
        X>=0?    // if from > 0
        GTO {0}   //      easy (non negative)
        ABS      // else from = abs(from)
        SF 99    //      neg_case = True 
        LBL {0}
        X<>Y     // stack now: z:step y:from x:to
        1000
        /
        +        // stack now: y:step x:a.bbb
        FS?C 98  // if not have_step
        GTO {1}
        RCL ST Z // else step
        100000   //      step = step / 100,000
        /
        +        // stack now: a.bbbnn
        LBL {1}
        FS?C 99  // if neg_case
        +/-
        RTN 
        // returns ISG number in form a.bbbnn
        """.format(settings.LOCAL_LABEL1_FOR_ISG_PREP, settings.LOCAL_LABEL2_FOR_ISG_PREP))

    pList = dedent("""
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
        SF 25       // try: (ignore error) 
        XEQ I       
        FC?C 25     // if was error (flag cleared)
        GTO 02      //   init list then push
        GROW        // else
        J-          //   grow, j-, j+ wrap, push()
        J+
        WRAP
        
        LBL 00      // push (x[,y]) -> (x[,y])
        STOEL       // zlist[j] = x
        FS? 01      // if list
        GTO 01      //   finished
        J+          // else
        X<>Y        //   zlist[j+1] = y
        STOEL
        X<>Y
        
        LBL 01      // finished (), view zlist
        VIEW "ZLIST"
        RTN
        
        LBL 02      // Init list
        1
        FS? 01
        1
        FC? 01
        2           // stack is (y:1,x:1) if flag 1 
        DIM "ZLIST" // else stack is (y:1,x:2)
        XEQ I       // prepare list for access
        RDN
        RDN         // drop rubbish off the stack
        GTO 00      // push()
        
        LBL "LIST-" // pop () -> () 
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
        
        LBL "CLIST" // () -> ()
        CLV "ZLIST" // clear ZLIST from memory
        RTN
        
        LBL I       // prepare list "ZLIST" for access
        INDEX "ZLIST"
        RTN
        """)

    # Comparison expressions

    pGT = dedent("""
        LBL "pGT"  // (y:a, x:b) -> (boolean) of a > b
        CF 00
        X<Y?
        SF 00  // true
        XEQ "p0Bool"  // get bool of flag 00
        RTN    
        """)

    pLT = dedent("""
        LBL "pLT"  // (y:a, x:b) -> (boolean) of a < b
        CF 00
        X>Y?
        SF 00  // true
        XEQ "p0Bool"  // get bool of flag 00
        RTN    
        """)

    pEQ = dedent("""
        LBL "pEQ"  // (y:a, x:b) -> boolean of a == b
        CF 00
        X=Y?
        SF 00  // true
        XEQ "p0Bool"  // get bool of flag 00
        RTN    
        """)

    pGTE = dedent("""
        LBL "pGTE"  // (y:a, x:b) -> (boolean) of a >= b
        CF 00
        X≤Y?
        SF 00  // true
        XEQ "p0Bool"  // get bool of flag 00
        RTN    
        """)

    pLTE = dedent("""
        LBL "pLT"  // (y:a, x:b) -> (boolean) of a <= b
        CF 00
        X≥Y?
        SF 00  // true
        XEQ "p0Bool"  // get bool of flag 00
        RTN    
        """)

    pNEQ = dedent("""
        LBL "pNEQ"  // (y:a, x:b) -> boolean of a != b
        CF 00
        X≠Y?
        SF 00  // true
        XEQ "p0Bool"  // get bool of flag 00
        RTN    
        """)

    # Logic

    pBool = dedent("""
        LBL "pBool"  // (a) -> (bool)
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

    p2Bool = dedent("""
        LBL "p2Bool"  // (a,b) -> (bool, bool)
        XEQ "pBool"    
        X<>Y
        XEQ "pBool"    
        X<>Y
        RTN
        """)

    pNot = dedent("""
        LBL "pNot"  // (a) -> boolean of not a
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

    pFS = dedent("""
        LBL "pFS"  // (flag) -> boolean of flag
        CF 00
        FS? IND X
        SF 00
        RDN
        FS? 00
        1
        FC? 00
        0
        RTN    
        """)

    pFC = dedent("""
        LBL "pFS"  // (flag) -> boolean of flag
        CF 00
        FC? IND X
        SF 00
        RDN
        FS? 00
        1
        FC? 00
        0
        RTN    
        """)

    # Param reordering - needed cos users push args from left to right, which puts early params in the wrong order when parsing params for RDN, STO nn

    p2Param = dedent("""
        LBL "p2Param"  // reverse params (a,b) -> (b,a)
        X<>Y
        RTN    
        """)

    p3Param = dedent("""
        LBL "p3Param"  // reverse params (a,b,c) -> (c,b,a)
        X<>Y
        RDN
        RDN
        X<>Y
        RDN
        RTN    
        """)

    p4Param = dedent("""
        LBL "p4Param"  // reverse params (a,b,c,d) -> (d,c,b,a)
        X<>Y
        RDN
        RDN
        X<>Y
        RTN    
        """)

    # Util

    p0Bool = dedent("""
        LBL "p0Bool"  // (a,b) -> (boolean) of whether flag 00 is set
        RDN
        RDN    // params dropped 
        FS? 00
        1
        FC? 00
        0
        RTN    
        """)

    p__1ErR = dedent("""
        LBL "p__1ErR"  // (to,999) -> display error & stop.
        RDN
        "range() limited"
        ├" to 999: got "
        ARCL ST X
        AVIEW
        STOP
        RTN    
        """)

    p1DMtx = dedent("""
        LBL "p1DMtx"  // (x) -> stores x in ZLIST if matrix else deletes ZLIST to signify empty matrix
        SF 01   // 1D matrix for lists
        MAT?    // if is a matrix
        STO "ZLIST"
        MAT?
        RTN
        XEQ "CLIST" // else empty matrix
        RTN
        """)

    p2DMtx = dedent("""
        LBL "p1DMtx"  // (x) -> stores x in ZLIST if matrix else deletes ZLIST to signify empty matrix
        CF 01   // 2D matrix for dictionaries  <-- ONLY LINE THAT IS DIFFERENT TO p1DMtx hmmm
        MAT?    // if is a matrix
        STO "ZLIST"
        MAT?
        RTN
        XEQ "CLIST" // else empty matrix
        RTN
        """)

    pMlen = dedent(f"""
        LBL "pMlen"  // () -> length of ZLIST
        // please INDEX the ZLIST list first
        // or delete the ZLIST to get an empty list of 0

        SF 25       // try: (ignore error) 
        INDEX "ZLIST"      
        FC?C 25     // if was error (flag cleared)
        GTO {settings.SKIP_LABEL1}      //   error, list is empty
        1
        1
        STOIJ
        RDN
        RDN
        I-
        RCLIJ
        RDN
        RTN
        LBL {settings.SKIP_LABEL1}      // list is empty
        0
        RTN
        """)

    pMxPrep = dedent(f"""
        // Prepare matrix for access by storing in ZLIST var
        // ** You must set flag 01 yourself to indicate
        // 1D (list) vs 2D (dictionaries) operation
        //  
        LBL "pMxPrep"  // (matrix) -> ()
        MAT?        // if is a matrix
        GTO {settings.SKIP_LABEL1}      // yes
        XEQ "CLIST" // else empty matrix
        RDN
        RTN
        LBL {settings.SKIP_LABEL1}  // yes is a matrix
        STO "ZLIST"
        RDN
        INDEX "ZLIST"        
        RTN
        """)

    p1mIJ = dedent("""
        // Sets IJ for list access to 'index'.  
        // Assumes ZLIST is indexed.
        //
        LBL "p1mIJ"  // (index) -> () & sets IJ for list access
        1
        +       // adjust row from 0 based (python) to 1 based (RPN matrix)
        1       // col (always, in lists)
        STOIJ
        RDN
        RDN
        RTN
        """)

    p2mIJfi = dedent(f"""
        // Sets IJ for dict access for 'key' (search required)  
        // Assumes ZLIST is indexed.
        //
        LBL "p2mIJfi"  // (key) -> () & finds key and sets IJ accordingly
        XEQ "pSaveSt"  // save the stack
        1
        1
        STOIJ
        RDN
        RDN
        CF {settings.FLAG_2D_MATRIX_FIND}  // not found flag
        1  // from
        XEQ "pMlen"  // to
        1  // step
        XEQ "pISG"
        STO "p2mISG"
        RDN
        LBL {settings.LOCAL_LABEL_FOR_2D_MATRIX_FIND}
        ISG "p2mISG"
        GTO LBL {settings.SKIP_LABEL1} // resume
        // see if el matches
        RCLEL
        x=Y?
        GTO {settings.SKIP_LABEL2}  // found
        RDN // else
        I+
        GTO {settings.LOCAL_LABEL_FOR_2D_MATRIX_FIND}  // keep looking
        LBL {settings.SKIP_LABEL2} // found
        SF {settings.FLAG_2D_MATRIX_FIND}
        LBL {settings.SKIP_LABEL1} // resume
        FC? {settings.FLAG_2D_MATRIX_FIND} // was it found?
        GTO "NO_KEY?"  // error not found, do not define this label :-)
        RCL "p2mISG"
        IP // index where found
        2  // value col
        X<>Y
        STOIJ  // all set to store something
        XEQ "pRclSt"  // recall stack
        RDN  // drop key we were looking for
        RTN
        """)

    pSaveStack = dedent("""
        // Saves the stack  
        //
        LBL "pSaveSt"  // (t,z,y,x) -> (t,z,y,x) & saves to regs pT, pZ, pY, pX
        STO "pX"
        RDN
        STO "pY"
        RDN
        STO "pZ"
        RDN
        STO "pT"
        RDN
        RTN
        """)

    pRclStack = dedent("""
        // Recalls the stack  
        //
        LBL "pRclSt"  // (?,?,?,?) -> (t,z,y,x) & recalls from regs pT, pZ, pY, pX
        RCL "pT"
        RCL "pZ"
        RCL "pY"
        RCL "pX"
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
        assert template in self.template_names, f'template "{template}" missing from {self.template_names}'
        if template not in self.needed_templates:
            self.needed_templates.append(template)

    def need_all_templates(self):
        self.needed_templates = self.template_names[:]  # copy
        # self.needed_templates.remove('pList')

    def get_user_insertable_pyrpn_cmds(self):
        """
        These are the commands that are exposed to the user and which can be inserted into.
        """
        return {
            'pFS': {'description': 'is flag set?'},
            'pFC': {'description': 'is flag clear?'},
        }

    def _create_local_labels(self):
        """
        Map to local labels, to avoid exposing py rpn library globally.
        Can't map to single letter alpha labels because they are used by user
        functions. Only 14 of them.
        :return:
        """
        next_label = settings.LOCAL_LABEL_START_FOR_Py
        for name in self.template_names:
            if next_label > 99:
                raise RuntimeError(f'Not enough labels for rpn templates, max label is 99 got {next_label} mappings so far: {self.local_alpha_labels}')
            self.local_alpha_labels[name] = str(next_label)
            next_label += 1
        # print(self.local_alpha_labels)

# print(RpnTemplates._get_class_attrs())

