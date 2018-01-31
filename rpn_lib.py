from builtins import sorted
from textwrap import dedent
import inspect
import logging
from logger import config_log
import settings

log = logging.getLogger(__name__)
config_log(log)

# more meaningful labels
neg_case = ''
no_step = ''
easy = ''
have_step = ''
error = ''
yes = ''
found = ''
loop = ''
ok = ''
exit_loop = ''
auto_create = ''
done = ''
have_found = ''
was_found = ''
push = ''
finish = ''
init = ''
delete = ''
prepare = ''

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
    global neg_case, no_step, easy, have_step, error, yes, found
    global loop, ok, exit_loop, auto_create, done, have_found, was_found
    global push, finish, init, delete, prepare

    def __init__(self):
        # self.needed_templates = []  # extra fragments that need to be emitted at the end
        self.local_alpha_labels = {}
        self.template_names = self._get_class_attrs()
        self._create_local_labels()
        self.embedded = False
        self.need_all_templates = False

    neg_case = settings.FLAG_PYTHON_USE_1
    have_step = settings.FLAG_PYTHON_USE_2
    easy = settings.SKIP_LABEL1
    no_step = settings.SKIP_LABEL2

    pISG = dedent(f"""
        LBL "pISG"  // Prepare ISG (z:from, y:to, x:step) -> (ccccccc.fffii)
        RCL T
        STO "pSaveT"
        RDN
        CF {neg_case}    // neg_case = False 
        CF {have_step}   // have_step = False (other than 1)
        IP               // ensure step is an int
        1
        X=Y?
        SF {have_step}   // have_step = True
        RDN
        RCL ST Z
        IP               // ensure from is an int
        RCL ST Z         // stack now: z:step y:from x:to
        IP               // ensure to is an int
        1
        -

        999              // check don't exceed max 'to' value of 999 (ISG ccccccc.fffii)
        X<Y?
        XEQ "pErOutR"
        RDN

        X<>Y             // stack now: z:step y:to-1 x:from 
        RCL ST Z         // step
        -                // stack now: z:step y:to-1 x:from-step 
        X>=0?            // if from > 0
        GTO {easy}       //      easy (non negative)
        ABS              // else from = abs(from)
        SF {neg_case}    //      neg_case = True 
        LBL {easy}
        X<>Y             // stack now: z:step y:from x:to
        1000
        /
        +                // stack now: y:step x:a.bbb
        FS?C {have_step} // if not have_step
        GTO {no_step}    //      skip ahead
        RCL ST Z         // else calculate step for ISG
        100000           //      step = step / 100,000
        /
        +                // stack now: a.bbbnn
        LBL {no_step}
        FS?C {neg_case}  // if neg_case
        +/-
        
        // Restore T which is now in Y because original params 
        // are dropped and are returning the ISG number in X
        
        RCL "pSaveT" 
        X<>Y
        RTN              // returns ISG number in form a.bbbnn 
        """)

    push = settings.LOCAL_LABEL_FOR_LIST_BACK_JUMP
    finish = settings.LOCAL_LABEL_FOR_LIST_BACK_JUMP2
    init = settings.SKIP_LABEL1
    delete = settings.SKIP_LABEL2
    prepare = settings.SKIP_LABEL3

    @property
    def pList(self):
        """
        Intelligently create various version of the LIST program

        Version 1: global export version:
            - include the global menu LIST
            - all labels as global text labels

        Version 2: local embedded version
            - no global menu LIST
            - all labels as numbered local labels
        """

        LIST_MENU_CODE = """
            LBL "LIST"  // 1D and 2D List Operations. p 176. HP42S programming manual

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
        """

        if self.embedded:
            list_menu = ''
            list_plus = settings.LIST_PLUS
            list_minus = settings.LIST_MINUS
            list_clist = settings.LIST_CLIST
            view_list = ''
        else:
            list_menu = LIST_MENU_CODE
            list_plus =  '"LIST+"'
            list_minus = '"LIST-"'
            list_clist = '"CLIST"'
            view_list = 'VIEW "ZLIST"'

        LIST_BODY = dedent(f"""
            {list_menu}

            LBL {list_plus} // LIST+ (x:val) when 1D, (y:val, x:key) when 2D 
                            // I.e. (y:value to go into r:2, x:value to go into r:1) where r is the new row 
                            // This is OPPOSITE way to STOIJ (y:I, x:J) viz. (y:row, x:col) 
            SF 25           // try: (ignore error) 
            XEQ {prepare}       
            FC?C 25       // if was error (flag cleared)
            GTO {init}    //   init list then push
            GROW          // else
            J-            //   grow, j-, j+ wrap, push()
            J+
            WRAP

            LBL {push}    // push (x[,y]) -> (x[,y])
            STOEL         // zlist[j] = x
            FS? 01        // if list
            GTO {finish}  //   finished
            J+            // else
            X<>Y          //   zlist[j+1] = y
            STOEL
            X<>Y

            LBL {finish}  // finished (), view zlist
            {view_list}
            RTN

            LBL {init}    // Init list
            1
            FS? 01
            1
            FC? 01
            2             // stack is (y:1,x:1) if flag 1 
            DIM "ZLIST"   // else stack is (y:1,x:2)
            XEQ {prepare} // prepare list for access
            RDN
            RDN           // drop rubbish off the stack
            GTO {push}    // push()

            LBL {list_minus}  // LIST- pop () -> () 
            SF 25
            XEQ {prepare}
            FC? 25
            RTN
            J-
            RCLEL
            FS? 01
            GTO {delete}
            J-
            RCLEL

            LBL {delete}
            DELR
            FS?C 25
            GTO {finish}

            LBL {list_clist} // CLIST () -> ()
            CLV "ZLIST"      // clear ZLIST from memory
            RTN

            LBL {prepare} // prepare list "ZLIST" for access
            INDEX "ZLIST"
            RTN
            """)

        return LIST_BODY

    # Comparison expressions

    pGT = dedent("""
        LBL "pGT"     // > (y:a, x:b) -> (boolean) of a > b
        CF 00
        X<Y?
        SF 00         // true
        XEQ "p0Bool"  // get bool of flag 00
        RTN    
        """)

    pLT = dedent("""
        LBL "pLT"     // < (y:a, x:b) -> (boolean) of a < b
        CF 00
        X>Y?
        SF 00
        XEQ "p0Bool"
        RTN    
        """)

    pEQ = dedent("""
        LBL "pEQ"     // == (y:a, x:b) -> boolean of a == b
        CF 00
        X=Y?
        SF 00
        XEQ "p0Bool"
        RTN    
        """)

    pGTE = dedent("""
        LBL "pGTE"    // >= (y:a, x:b) -> (boolean) of a >= b
        CF 00
        X≤Y?
        SF 00
        XEQ "p0Bool"
        RTN    
        """)

    pLTE = dedent("""
        LBL "pLT"     // <= (y:a, x:b) -> (boolean) of a <= b
        CF 00
        X≥Y?
        SF 00
        XEQ "p0Bool"
        RTN    
        """)

    pNEQ = dedent("""
        LBL "pNEQ"    // != (y:a, x:b) -> boolean of a != b
        CF 00
        X≠Y?
        SF 00
        XEQ "p0Bool"
        RTN    
        """)

    # Logic

    pBool = dedent("""
        LBL "pBool"  // Convert to boolean. (a) -> (bool)
        CF 00
        X≠0?
        SF 00        // is non zero, thus true
        RDN          // drop parameter
        FS? 00
        1
        FC? 00
        0
        RTN
        """)

    p2Bool = dedent("""
        LBL "p2Bool"  // Convert to booleans. (a,b) -> (bool, bool)
        XEQ "pBool"    
        X<>Y
        XEQ "pBool"    
        X<>Y
        RTN
        """)

    pNot = dedent("""
        LBL "pNot"   // not (a) -> boolean of not a
        X≠0?
        SF 00        // is a true value
        RDN
        FS? 00
        0            // False
        FC? 00
        1            // True
        RTN    
        """)

    # Flags

    pFS = dedent("""
        LBL "pFS"    // Is Flag set? (flag) -> boolean of flag
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
        LBL "pFS"    // Is Flag clear? (flag) -> boolean of flag
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
        LBL "p2Param"  // Reverse params. (a,b) -> (b,a)
        X<>Y
        RTN    
        """)

    p3Param = dedent("""
        LBL "p3Param"  // Reverse params. (a,b,c) -> (c,b,a)
        X<>Y
        RDN
        RDN
        X<>Y
        RDN
        RTN    
        """)

    p4Param = dedent("""
        LBL "p4Param"  // Reverse params. (a,b,c,d) -> (d,c,b,a)
        X<>Y
        RDN
        RDN
        X<>Y
        RTN    
        """)

    # Util

    p0Bool = dedent("""
        LBL "p0Bool"  // Util used by comparison ops. (a,b) -> (boolean) - whether flag 00 is set, plus RDNs 
        RDN
        RDN    // params dropped 
        FS? 00
        1
        FC? 00
        0
        RTN    
        """)

    pErOutR = dedent("""
        LBL "pErOutR"  // Out of Range error. (to,999) -> display error & stop.
        RDN
        "range() limited"
        ├" to 999: got "
        ARCL ST X
        AVIEW
        STOP
        RTN    
        """)

    PErNkey = dedent("""
        LBL "PErNkey"  // Dictionary key not found error. () -> display error & stop.
        "Dictionary key "
        ARCL ST X
        ├" not found"
        PROMPT
        RTN    
        """)

    pAssert = dedent("""
        LBL "pAssert"  // Assert. (bool) -> if true, keep going, else stop & display error
        X≠0?
        RTN
        "Assertion Err "
        ARCL ST X
        ├" is not True"
        PROMPT
        RTN    
        """)

    error = settings.SKIP_LABEL1

    pMxLen = dedent(f"""
        LBL "pMxLen"    // Get matrix row length. () -> length of ZLIST
        
        // Please INDEX the ZLIST list first
        //  or delete the ZLIST to get an empty list of 0
        
        // WARNING - will mess with I J

        SF 25         // try: (ignore error) 
        INDEX "ZLIST"      
        FC?C 25       // if was error (flag cleared)
        GTO {error}      //   error, list is empty
        1
        1
        STOIJ
        RDN
        RDN
        I-
        RCLIJ
        RDN
        RTN
        LBL {error}      // list is empty
        0
        RTN
        """)

    yes = settings.SKIP_LABEL1

    pMxPrep = dedent(f"""
        LBL "pMxPrep"   // Prepare Matrix. (matrix) -> ()
        
        // Stores matrix in ZLIST var and indexes it, or clears ZLIST var if 0 is passed in.
        // Yes, its awkward, but a matrix that is an integer 0 means an empty matrix, and ZLIST is cleared from memory.
         
        // You must set flag 01 yourself to indicate 1D (list) vs 2D (dict) operation mode.
        // Do this setting either before or after the call to this subroutine - doesn't matter.
        // Of course, the setting/clearing of flag 01 should match the type of matrix you are passing in.
        //  

        MAT?            // if is a matrix
        GTO {yes}       // yes
        XEQ "CLIST"     // else empty matrix
        RDN
        RTN
        LBL {yes}       // yes is a matrix
        STO "ZLIST"
        RDN
        INDEX "ZLIST"        
        RTN
        """)

    p1MxIJ = dedent(f"""
        LBL "p1MxIJ"     // Set IJ for List. (index) -> () & sets IJ for list access

        // Sets IJ for list access to 'index'.  Now handles negative indexes.  
        // Assumes ZLIST is indexed.

        X≥0?
        GTO {easy}

        // Handle negative index, look up length of list
        XEQ "pMxLen"
        +              // add the negative index to length to get the wanted index
                
        LBL {easy}
        1
        +               // adjust row from 0 based (python) to 1 based (RPN matrix)
        1               // col (always, in lists)
        STOIJ
        RDN
        RDN
        RTN
        """)

    auto_create = settings.FLAG_LIST_AUTO_CREATE_IF_KEY_NOT_FOUND
    found = settings.FLAG_PYTHON_USE_1
    exit_loop = settings.SKIP_LABEL1
    was_found = settings.SKIP_LABEL1
    have_found = settings.SKIP_LABEL2
    done = settings.SKIP_LABEL2
    ok = settings.SKIP_LABEL3
    loop = settings.LOCAL_LABEL_FOR_2D_MATRIX_FIND

    p2MxIJ = dedent(f"""
        LBL "p2MxIJ"  // Set IJ for Dict. (key) -> () - finds key's value and sets IJ accordingly.
        XEQ "pStoStk"  // If flag {settings.FLAG_LIST_AUTO_CREATE_IF_KEY_NOT_FOUND} then auto creates new row.

        // Assumes ZLIST is indexed.
 
        1              // 'from' (search from row 1)
        XEQ "pMxLen"    // 'to' (get num rows in matrix)
        1
        +              // add 1 cos want 'to' to include last row
        1              // 'step'
        XEQ "pISG"
        STO "pISGvar"
        RDN
        
        // Start the search from row 1
        
        1
        1
        STOIJ
        RDN
        RDN
        CF {found}              // found = False
        
        LBL {loop}
        ISG "pISGvar"
        GTO {ok}                // ok, compare next element
        GTO {exit_loop}         // finished ISG search through the matrix row 'keys' (in col 1)
        LBL {ok}
        RCLEL
        X=Y?                    // see if element matches
        GTO {have_found}        //   found
        RDN                     // else
        I+                      //   increment row
        GTO {loop}              // keep looking
        
        LBL {have_found}        // have found
        SF {found}
        
        LBL {exit_loop}         // finished search
        FS? {found}             // was it found?
        GTO {was_found}         // perfectly found, nice
         
        // Else decide if we auto create a new row
        
        FC? {auto_create}       // if not auto create new row
        GTO "PErNkey"           // error key not found, auto create is off
        0                       // temp value 
        X<>Y                    // key (y:temp value, x:key)
        XEQ "LIST+"             // this will incidentally set IJ nicely to the 'value' element
        GTO {done}              // done
        
        LBL {was_found}         // ok found, nice
        RCL "pISGvar"
        IP                      // index where found y:(row / I)
        2                       // position of value x:(col / J)
        STOIJ                   // all set to store or recall something
        LBL {done}              // done
        XEQ "pRclStk"           // recall stack
        RDN                     // drop key we were looking for
        RTN
        """)

    pStoStk = dedent("""
        LBL "pStoStk"           // Saves the stack. (t,z,y,x) -> (t,z,y,x) & saves to regs pT, pZ, pY, pX
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

    pRclStk = dedent("""
        LBL "pRclStk"           // Recalls the stack. (?,?,?,?) -> (t,z,y,x) & recalls from regs pT, pZ, pY, pX
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

    def get_user_insertable_pyrpn_cmds(self):
        """
        These are the commands that are exposed to the user and which can be inserted into.
        """
        return {
            'pFS': {'description': 'is flag set?'},
            'pFC': {'description': 'is flag clear?'},
            'pAssert': {'description': 'is param True?'},
            'pMxLen': {'description': 'length of list or dict'},
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

