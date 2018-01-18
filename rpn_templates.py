from textwrap import dedent

ISG_PREPARE = dedent("""
    RTN     // prevent any code above running into below inserted functions
    
    LBL d   // def calculate_ISG(z:from, y:to, x:step)
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
    GTO e    //      easy (non negative)
    ABS      // else from = abs(from)
    SF 99    //      neg_case = True 
    LBL e
    X<>Y     // stack now: z:step y:from x:to
    1000
    /
    +        // stack now: y:step x:a.bbb
    FS?C 98  // if not have_step
    GTO c
    RCL ST Z // else step
    100000   //      step = step / 100,000
    /
    +        // stack now: a.bbbnn
    LBL c
    FS?C 99  // if neg_case
    +/-
    RTN 
    // returns ISG number in form a.bbbnn
    """)

LIST_PUSH_POP = dedent("""
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

PRE_LOGIC_NORMALISE = dedent("""
    // takes two params, which will be both converted to either 1 or 0

    LBL "LGICNM"
    CF 00  // represents that x is true
    CF 01  // represents that y is true
    X≠0?
    SF 00
    X<>Y
    X≠0?
    SF 01
    RDN
    RDN    // have gotten rid of args
    FS? 01
    1
    FC? 01
    0
    FS? 00
    1
    FC? 00
    0
    RTN
    """)

