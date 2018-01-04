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
