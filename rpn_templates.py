from textwrap import dedent

ISG_PREPARE = dedent("""
    RTN     // prevent any code above running into below inserted functions

    LBL d   // template function "calculate_ISG", takes two params
    CF 99
    1
    -
    X<>Y
    1
    -
    X>=0?
    GTO e
    ABS
    SF 99
    LBL e
    X<>Y
    1000
    /
    +
    FS?C 99
    +/-
    RTN  // returns ISG number in form a.bbb
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