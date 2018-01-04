from textwrap import dedent

ISG_PREPARE = dedent("""
    RTN     // prevent any code above running into below inserted functions

    LBL i   // template function "calculate_ISG", takes two params
    CF 99
    1
    -
    X<>Y
    1
    -
    X>=0?
    GTO j
    ABS
    SF 99
    LBL j
    X<>Y
    1000
    /
    +
    FSC? 99
    +/-
    RTN  // returns ISG number in form a.bbb
    """)
