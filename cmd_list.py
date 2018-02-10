cmd_list = \
{'%': {'description': 'Percent. Returns (x × y) / 100. (Leaves the y value in '
                      'the y-register.)',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': 'being researched',
       'supported': ''},
 '%CH': {'description': 'Percent change. Returns (x – y)×(100 / y).',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'being researched',
         'supported': ''},
 '+': {'description': 'Addition. Returns y + x.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': '',
       'supported': '✓'},
 '+/–': {'description': 'Change the sign of the number in the x-register. '
                        'While entering an exponent, can also be used to '
                        'change the sign of the exponent.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'Not Applicable to Python or use built in Python '
                       'facility',
         'supported': 'N/A'},
 '1/x': {'description': 'Reciprocal. Returns 1/x.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'being researched',
         'supported': ''},
 '10↑X': {'description': 'Common exponential. Returns 10x.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'ABS': {'description': 'Absolute value. Returns |x|.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'ACOS': {'description': 'Arc cosine. Returns cos–1 x.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'ACOSH': {'description': 'Arc hyperbolic cosine. Returns cosh–1 x.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'ADV': {'description': 'Advance the printer paper one line',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'AGRAPH': {'description': 'Alpha graphics. Display a graphics image. Each '
                           'character in the Alpha register specifies an 8-dot '
                           'column pattern. The x- and y-registers specify the '
                           'pixel location of the image.',
            'indirect_allowed': False,
            'num_arg_fragments': 0,
            'suggestion': 'being researched',
            'supported': ''},
 'AIP': {'description': 'Append Integer part of x to the Alpha register.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'ALENG': {'description': 'Alpha length. Returns the number of characters in '
                          'the Alpha register.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'ALL': {'description': 'Select the All display format.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'ALLΣ': {'description': 'Select ALLΣ (All-statistics) mode, which uses 13 '
                         'summation coefficients.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'AND': {'description': 'Logical AND. Returns x AND y.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'Use built in Python boolean operators instead e.g. not '
                       'val or val2 and val3',
         'supported': 'No'},
 'AOFF': {'description': 'Alpha off. Exit from the ALPHA menu.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'AON': {'description': 'Alpha on. Select the ALPHA menu.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'ARCL': {'description': 'Alpha recall. Copy data into the Alpha register, '
                         'appending it to the current contents. Numbers are '
                         'formatted using the current display format.  '
                         'Parameter: register or variable.   (indirect '
                         'allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use the alpha() function to build up strings in the '
                        'alpha register, specifying literal strings of any '
                        'length, and multiple variables. See help for more '
                        'details',
          'supported': 'No'},
 'AROT': {'description': 'Alpha rotate. Rotate the Alpha register by the '
                         'number of characters specified in the x-register.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'ASHF': {'description': 'Alpha shift. Shifts the six left-most characters out '
                         'of the Alpha register.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'ASIN': {'description': 'Arc sine. Returns sin–1 x.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'ASINH': {'description': 'Arc hyperbolic sine. Returns sinh–1 x.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'ASSIGN': {'description': 'Assign a function, program, or variable to a menu '
                           'key in the CUSTOM menu. Parameter 1: function '
                           'name, alpha program label, or variable name. '
                           'Parameter 2: key number (01–18).',
            'indirect_allowed': False,
            'num_arg_fragments': 2,
            'suggestion': 'being researched',
            'supported': ''},
 'ASTO': {'description': 'Alpha store. Copy the first six characters in the '
                         'Alpha register into a register or variable. '
                         'Parameter: register or variable (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': '',
          'supported': 'Instead use alpha("this is my string") then '
                       'ASTO(myvar)'},
 'ATAN': {'description': 'Arc tangent. Returns tan–1 x.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'ATANH': {'description': 'Arc hyperbolic tangent. Returns tanh–1 x.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'ATOX': {'description': 'Alpha to X. Convert the left-most character in the '
                         'Alpha register to its character code (returned to '
                         'the x-register) and delete the character.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'AVIEW': {'description': 'Alpha view. Display the Alpha register.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': 'AVIEW(myvar) refers to variables and can take '
                        'multiple parameters incl. literal string - powerful!'},
 'BASE+': {'description': 'Base addition. Returns the 36-bit sum of y + x.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'BASE+/–': {'description': "Base change sign. Returns the 36-bit 2's "
                            'complement of x.',
             'indirect_allowed': False,
             'num_arg_fragments': 0,
             'suggestion': 'being researched',
             'supported': ''},
 'BASEx': {'description': 'Base multiplication. Returns the 36-bit product of '
                          'y x x.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'BASE÷': {'description': 'Base division. Returns the 36-bit quotient of y ÷ '
                          'x.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'BASE–': {'description': 'Base subtraction. Returns the 36-bit difference of '
                          'y – x.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'BEEP': {'description': 'Sound a sequence of four tones.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'BEST': {'description': 'Select the best curve-fitting model for the current '
                         'statistical data.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'BINM': {'description': 'Select Binary mode (base 2)',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'BIT?': {'description': 'Test the xth bit of y. If the bit is set (1), '
                         'execute the next program line; if the bit is clear '
                         '(0), skip the next program line.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'BST': {'description': 'Back step. Move the program pointer to the previous '
                        'program line. (Not programmable.)',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': 'Not programmable'},
 'CF': {'description': 'Clear flag nn (00 ≤  nn ≤ 35 or 81 ≤  nn ≤ 99). '
                       'Parameter: flag number (indirect allowed)',
        'indirect_allowed': True,
        'num_arg_fragments': 1,
        'suggestion': '',
        'supported': 'Use CF(nn)'},
 'CLA': {'description': 'Clear Alpha register. If Alpha mode is on and '
                        'character entry is terminated (no cursor displayed), '
                        'then  ◄  also executes the CLA function.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'CLALL': {'description': 'Clear all. Clear all stored programs and data.(Not '
                          'Programmable.)',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'Not Applicable to Python or use built in Python '
                         'facility',
           'supported': 'N/A'},
 'CLD': {'description': 'Clear display. Clear a message from the display.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'CLKEYS': {'description': 'Clear all CUSTOM menu key assignments.',
            'indirect_allowed': False,
            'num_arg_fragments': 0,
            'suggestion': '',
            'supported': '✓'},
 'CLLCD': {'description': 'Clear LCD (liquid crystal display). Blanks the '
                          'entire display.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'CLMENU': {'description': 'Clear MENU. Deletes all menu key definitions for '
                           'the programmable menu.',
            'indirect_allowed': False,
            'num_arg_fragments': 0,
            'suggestion': '',
            'supported': '✓'},
 'CLP': {'description': 'Clear a program from memory. Parameter: global label',
         'indirect_allowed': False,
         'num_arg_fragments': 1,
         'suggestion': 'being researched',
         'supported': ''},
 'CLRG': {'description': 'Clear Registers. Clear all of the numbered storage '
                         'registers to zero.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': 'yes'},
 'CLST': {'description': 'Clear Stack. Clear the stack registers to zero.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Not Applicable to Python or use built in Python '
                        'facility',
          'supported': 'N/A'},
 'CLV': {'description': 'Clear a variable from memory. Parameter: variable '
                        'name (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'being researched',
         'supported': ''},
 'CLX': {'description': 'Clear x-register to zero. If digit entry is '
                        'terminated (no cursor in the display), then  ◄  also '
                        'executes CLX.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'Not Applicable to Python or use built in Python '
                       'facility',
         'supported': 'N/A'},
 'CLZ': {'description': 'Clear statistics. Clear the accumulated statistical '
                        'data in the summation registers.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'being researched',
         'supported': ''},
 'COMB': {'description': 'Combinations of y items taken x at a time = y! / '
                         '[x!(y-x)!]',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'COMPLEX': {'description': 'Convert two real numbers (or matrices) into a '
                            'complex number (or matrix). Converts a complex '
                            'number (or matrix) into two real numbers (or '
                            'matrices).',
             'indirect_allowed': False,
             'num_arg_fragments': 0,
             'suggestion': '',
             'supported': '✓'},
 'CORR': {'description': 'Returns a correlation coefficient using the current '
                         'statistical data and curve-fitting model.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'COS': {'description': 'Cosine. Returns cos(x).',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'COSH': {'description': 'Hyperbolic cosine. Returns cosh(x).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'CPX?': {'description': 'If the x-register contains a complex number, execute '
                         'the next program line; if the x-register does not '
                         'contain a complex number, skip the next program '
                         'line.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'CPXRES': {'description': 'Complex-results. Enable the calculator to return a '
                           'complex result, even if the inputs are real '
                           'numbers.',
            'indirect_allowed': False,
            'num_arg_fragments': 0,
            'suggestion': '',
            'supported': '✓'},
 'CROSS': {'description': 'Returns the cross product of two vectors (matrices '
                          'or complex numbers).',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'DECM': {'description': 'Selects Decimal mode (base 10).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'DEG': {'description': 'Select the Degrees angular mode.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'DEL': {'description': 'Delete the specified number of lines from the current '
                        'program. Program-entry mode must be on. (Not '
                        'programmable.) Parameter: number of lines.',
         'indirect_allowed': False,
         'num_arg_fragments': 1,
         'suggestion': '',
         'supported': 'Not programmable'},
 'DELAY': {'description': 'Set the print delay time to x seconds.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'DELR': {'description': 'Delete row. Delete the current row from the indexed '
                         'matrix.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': 'Use mymatrix.delr(n) instead.'},
 'DET': {'description': 'Determinant. Returns the determinant of the matrix in '
                        'the x-register.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'DIM': {'description': 'Dimension a matrix to x columns and y rows. If the '
                        'matrix does not exist, DIM creates it. Parameter: '
                        'variable name (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': '',
         'supported': 'Use mymatrix.dim(rows'},
 'DIM?': {'description': 'Returns the dimensions of the matrix in the '
                         'x-register (rows to the y-register and columns to '
                         'the x-register).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': 'Use len(mymatrix) to get the length. TODO Still '
                       'working on mymatrix.shape()'},
 'DOT': {'description': 'Dot Product.  Returns the dot product of two vectors '
                        '(matrices or complex numbers).',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'DSE': {'description': 'Decrement, Skip if (less than or) Equal. Given '
                        'ccccccc.fflii in a variable or register, decrements '
                        'ccccccc by ii and skips the next program line if '
                        'ccccccc is now ≤  fff. Parameter: register or '
                        'variable (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'Use Python for...range() loops instead, or Python '
                       'while loops',
         'supported': 'No'},
 'EDIT': {'description': 'Edit a matrix in the x-register.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'EDITN': {'description': 'Edit a named matrix. Parameter: variable name '
                          '(indirect allowed)',
           'indirect_allowed': True,
           'num_arg_fragments': 1,
           'suggestion': 'being researched',
           'supported': ''},
 'END': {'description': 'End of a program.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'Not Applicable to Python or use built in Python '
                       'facility',
         'supported': 'N/A'},
 'ENG': {'description': 'Select Engineering display format. Parameter: number '
                        'of digits (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': '',
         'supported': '✓'},
 'ENTER': {'description': 'Separate two numbers keyed in sequentially; copies '
                          'x into the y-register, y into the z-register, and z '
                          'into the t-register, and loses t.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'Use Python variables',
           'supported': 'No'},
 'EXITALL': {'description': 'Exit all menus.',
             'indirect_allowed': False,
             'num_arg_fragments': 0,
             'suggestion': '',
             'supported': '✓'},
 'EXPF': {'description': 'Select the exponential curve-fitting model.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'E↑X': {'description': 'Natural exponential. Returns ex.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'Use EtoX() instead.',
         'supported': '✓ (renamed)'},
 'E↑X-1': {'description': 'Natural exponential for values of x which are close '
                          'to zero. Returns ex–1, which provides a much higher '
                          'accuracy in the fractional part of the result.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'FC?': {'description': 'Flag clear test. If the specified flag is clear, '
                        'executes the next program line; if the flag is set, '
                        'skips the next program line. Parameter: flag number '
                        '(indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': '',
         'supported': 'Use isFC(nn) instead'},
 'FC?C': {'description': 'Flag clear test and clear. If the specified flag is '
                         'clear, execute the next program line; if the flag is '
                         'set, skip the next program line. Cleared after the '
                         'test is complete. (This function can be used only '
                         'with flags 00 through 35 and 81 through 99.) '
                         'Parameter: flag number (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use any normal variable to store boolean values, test '
                        'with the Python "if" statements instead',
          'supported': 'No'},
 'FCSTX': {'description': 'Forecasts an x-value given a y-value.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'FCSTY': {'description': 'Forecasts a y-value given an x-value.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'FIX': {'description': 'Select Fixed-decimal display format. Parameter: '
                        'number of digits (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': '',
         'supported': '✓'},
 'FNRM': {'description': 'Returns the Frobenius norm of the matrix in the '
                         'x-register.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'FP': {'description': 'Returns the fractional part of x.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': '',
        'supported': '✓'},
 'FS?': {'description': 'Flag set test. If the specified flag is set, execute '
                        'the next program line; if the flag is clear, skip the '
                        'next program line. Parameter: flag number (indirect '
                        'allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': '',
         'supported': 'Use isFS() instead'},
 'FS?C': {'description': 'Flag set test and clear. If the specified flag is '
                         'set, execute the next program line; if the flag is '
                         'clear, skip the next program line. Clear the flag '
                         'after the test is complete. (This function can be '
                         'used only with flags 00 through 35 and 81 through '
                         '99.) Parameter: flag number (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use any normal variable to store boolean values, test '
                        'with the Python "if" statements instead',
          'supported': 'No'},
 'GAMMA': {'description': 'Gamma function. Returns Γ(x).',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'GETKEY': {'description': 'Get key. The calculator waits for you to press a '
                           'key. When you do, the key number is returned to '
                           'the x-register. Keys are numbered from 1 through '
                           '37 ( Σ+  through  ÷ )for normal keys and 38 '
                           'through 74 (■ Σ–   through ■CATALOG) for shifted '
                           'keys.',
            'indirect_allowed': False,
            'num_arg_fragments': 0,
            'suggestion': '',
            'supported': '✓'},
 'GETM': {'description': 'Get matrix. Copy a submatrix into the x-register '
                         'from the indexed matrix.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                        'instead - read help for more info',
          'supported': 'No'},
 'GRAD': {'description': 'Select Grads angular mode.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'GROW': {'description': 'Select Grow mode. Executing  →  or J+ causes the '
                         'matrix to grow by one new row if the index pointers '
                         'are at the last (lower-right) element in the matrix.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': 'No but new command mymatrix.appendr() added to '
                       'compensate.'},
 'GTO': {'description': 'Go to label. From the keyboard, move the program '
                        'pointer to the specified label. In a running program, '
                        'cause the program to branch to the specified label. '
                        'Parameter: local or global label (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'Not Applicable to Python or use built in Python '
                       'facility',
         'supported': 'N/A'},
 'HEXM': {'description': 'Select Hexadecimal mode (base 16).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'HMS+': {'description': 'Add x and y using H.MMSSss (hours-minutes-seconds) '
                         'format.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'HMS–': {'description': 'Subtract x from y using H.MMSSss format.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'I+': {'description': 'Increment the row pointer in the indexed matrix.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                      'instead - read help for more info',
        'supported': 'No'},
 'INDEX': {'description': 'Index a named matrix. Parameter: variable name '
                          '(indirect allowed)',
           'indirect_allowed': True,
           'num_arg_fragments': 1,
           'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                         'instead - read help for more info',
           'supported': 'No'},
 'INPUT': {'description': 'Recall a register or variable to the x-register, '
                          'display the name of the register or variable along '
                          'with the contents of the x-register, and halt '
                          'program execution. Pressing R/S (or ■SST) stores x '
                          'into the register or variable; pressing EXIT '
                          'cancels. (Used only in programs.) Parameter: '
                          'register or variable (indirect allowed)',
           'indirect_allowed': True,
           'num_arg_fragments': 1,
           'suggestion': 'being researched',
           'supported': ''},
 'INSR': {'description': 'Insert a row in the indexed matrix.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': 'Use your_matrix.insr() instead'},
 'INTEG': {'description': 'Integrate the selected integration program with '
                          'respect to the specified variable. Parameter: '
                          'variable name (indirect allowed)',
           'indirect_allowed': True,
           'num_arg_fragments': 1,
           'suggestion': 'being researched',
           'supported': ''},
 'INVRT': {'description': 'Returns the inverse of the matrix in the '
                          'x-register.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'IP': {'description': 'Returns the integer part of x',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': '',
        'supported': '✓'},
 'ISG': {'description': 'Increment, Skip if Greater. Given ccccccc.fffii in a '
                        'variable or register, increments ccccccc by ii and '
                        'skips the next program line if ccccccc is now > fff. '
                        'Parameter: register or variable (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'Use Python for...range() loops instead, or Python '
                       'while loops',
         'supported': 'No'},
 'I–': {'description': 'Decrement the row pointer in the indexed matrix.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                      'instead - read help for more info',
        'supported': 'No'},
 'J+': {'description': 'Increment the column pointer in the indexed matrix.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                      'instead - read help for more info',
        'supported': 'No'},
 'J–': {'description': 'Decrement the column pointer in the indexed matrix.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                      'instead - read help for more info',
        'supported': 'No'},
 'KEYASN': {'description': 'Selects key-assignments mode for the CUSTOM menu.',
            'indirect_allowed': False,
            'num_arg_fragments': 0,
            'suggestion': 'being researched',
            'supported': ''},
 'KEYG': {'description': 'On menu key, go to. Branch to specified label to '
                         'when a particular menu key is pressed.  Parameter '
                         '1:: Key number (1 through 9), Parameter 2: program '
                         'label (global or local)',
          'indirect_allowed': False,
          'num_arg_fragments': 2,
          'suggestion': 'being researched',
          'supported': ''},
 'KEYX': {'description': 'On menu key, execute. Execute (as a subroutine) '
                         'specified label when a particular menu key is '
                         'pressed. Parameter 1:: Key number (1 through 9), '
                         'Parameter 2: program label (global or local)',
          'indirect_allowed': False,
          'num_arg_fragments': 2,
          'suggestion': 'Use Python variables',
          'supported': 'No'},
 'LASTX': {'description': 'Last x. Recall the last value of x used in a '
                          'calculation.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'Use Python variables',
           'supported': 'No'},
 'LBL': {'description': 'Label. Identify programs and routines for execution '
                        'and branching. Parameter: local or global label.',
         'indirect_allowed': False,
         'num_arg_fragments': 1,
         'suggestion': 'Not Applicable to Python or use built in Python '
                       'facility',
         'supported': 'N/A'},
 'LCLBL': {'description': 'Select Local label mode for the CUSTOM menu (to use '
                          'CUSTOM menu assignments to execute local labels '
                          'within the current program).',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'LINF': {'description': 'Select the linear curve-fitting model.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'LINΣ': {'description': 'Select Linear statistics mode, which uses six '
                         'summation coefficients.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'LIST': {'description': 'Print a portion of a program listing. (Not '
                         'programmable.) Parameter: number of lines.',
          'indirect_allowed': False,
          'num_arg_fragments': 1,
          'suggestion': '',
          'supported': 'Not programmable'},
 'LN': {'description': 'Natural logarithm. Returns ln(x).',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': '',
        'supported': '✓'},
 'LN1+X': {'description': 'Natural logarithm for values close to zero. Returns '
                          'ln(1 + x), which provides a much higher accuracy in '
                          'the fractional part of the result.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'LOG': {'description': 'Common logarithm. Returns log10(x).',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'LOGF': {'description': 'Select the logarithmic curve-fitting model.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'MAN': {'description': 'Select Manual print mode.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'MAT?': {'description': 'If the x-register contains a matrix, execute the '
                         'next program line; if the X-register does not '
                         'contain a matrix, skip the next program line.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'MEAN': {'description': 'Mean. Returns the mean of x-values (Σx / n) and the '
                         'mean of y-values (Σy / n).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'MENU': {'description': 'Select the programmable menu.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'MOD': {'description': 'Modulo. Returns the remainder for y / x.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'being researched',
         'supported': ''},
 'MVAR': {'description': 'Declare a menu variable in a SOLVER program. '
                         'Parameter: variable name.',
          'indirect_allowed': False,
          'num_arg_fragments': 1,
          'suggestion': 'being researched',
          'supported': ''},
 'N!': {'description': 'Factorial. Returns x!.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'being researched',
        'supported': ''},
 'NEWMAT': {'description': 'New matrix. Creates a y × x matrix in the '
                           'x-register.',
            'indirect_allowed': False,
            'num_arg_fragments': 0,
            'suggestion': '',
            'supported': '✓'},
 'NORM': {'description': 'Select Normal print mode, which prints a record of '
                         'keystrokes.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'NOT': {'description': 'Logical NOT. Returns NOT(x).',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'Use built in Python boolean operators instead e.g. not '
                       'val or val2 and val3',
         'supported': 'No'},
 'OCTM': {'description': 'Select Octal mode',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'OFF': {'description': 'Turn the calculator off (programmable). (Pressing '
                        '■OFF does not execute the programmable OFF function.)',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'OLD': {'description': 'Recall the current element from the indexed matrix. '
                        '(Equivalent to RCLEL.)',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                       'instead - read help for more info',
         'supported': 'No'},
 'ON': {'description': 'Continuous on. Prevent the calculator from '
                       'automatically turning off after ten minutes of '
                       'inactivity.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': '',
        'supported': '✓'},
 'OR': {'description': 'Logical OR. Returns x OR y.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'Use built in Python boolean operators instead e.g. not '
                      'val or val2 and val3',
        'supported': 'No'},
 'PERM': {'description': 'Permutations of y items taken x at a time. Returns '
                         'y!/(y – x)!',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'PGMINT': {'description': 'Select a program to integrate. Parameter: global '
                           'label (indirect allowed)',
            'indirect_allowed': True,
            'num_arg_fragments': 1,
            'suggestion': 'being researched',
            'supported': ''},
 'PGMSLV': {'description': 'Select a program to solve. Parameter: global label '
                           '(indirect allowed) ,',
            'indirect_allowed': True,
            'num_arg_fragments': 1,
            'suggestion': 'being researched',
            'supported': ''},
 'PI': {'description': 'Put an approximation of π into the x-register '
                       '(3.14159265359).',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': '',
        'supported': '✓'},
 'PIXEL': {'description': 'Turn on a single pixel (dot) in the display y: row '
                          '(y axis) x: col (x axis)',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'POLAR': {'description': 'Select polar coordinate mode for displaying complex '
                          'numbers.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'POSA': {'description': 'Position in Alpha. Searches the Alpha register for '
                         'the target specified in the x-register. If found, '
                         'returns the character position; if not found, '
                         'returns -1.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'PRA': {'description': 'Print Alpha register.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'PRLCD': {'description': 'Print LCD (liquid crystal display). Prints the '
                          'entire display.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'PROFF': {'description': 'Printing off. Clears flags 21 and 55.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'PROMPT': {'description': 'Display the Alpha register and halt program '
                           'execution.',
            'indirect_allowed': False,
            'num_arg_fragments': 0,
            'suggestion': '',
            'supported': '✓'},
 'PRON': {'description': 'Printing on. Sets flags 21 and 55.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'PRP': {'description': 'Print program. If a label is not specified, print the '
                        'current program. (Not programmable.)  Parameter: '
                        'global label (optional)',
         'indirect_allowed': False,
         'num_arg_fragments': 1,
         'suggestion': '',
         'supported': 'Not programmable'},
 'PRSTK': {'description': 'Print stack. Print the contents of the stack '
                          'registers (x, y, z and t).',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'PRUSR': {'description': 'Print user variables and programs.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'PRV': {'description': 'Print variable. Parameter: variable name (indirect '
                        'allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'being researched',
         'supported': ''},
 'PRX': {'description': 'Print x-register.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'PRZ': {'description': 'Print statistics. Prints the contents of the '
                        'summation registers.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'being researched',
         'supported': ''},
 'PSE': {'description': 'Pause program execution for about 1 second.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'PUTM': {'description': 'Put matrix. Stores the matrix in the X-register into '
                         'the indexed matrix beginning at the current element.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                        'instead - read help for more info',
          'supported': 'No'},
 'PWRF': {'description': 'Select the power curve-fitting model.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'QUIET': {'description': 'Toggle flag 26 to disable or enable the beeper (Not '
                          'programmable )',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'Not Applicable to Python or use built in Python '
                         'facility',
           'supported': 'N/A'},
 'R/S': {'description': 'Run/stop. Runs a program (beginning at the current '
                        'program line) or stops a running program. In '
                        'program-entry mode, inserts a STOP instruction into '
                        'the program.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': 'STOP() is supported'},
 'R<>R': {'description': 'Row swap row. Swaps the elements in rows x and y in '
                         'the indexed matrix.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': 'Use mymatrix.row_swap(3'},
 'RAD': {'description': 'Select Radians angular mode',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'RAN': {'description': 'Returns a random number (0 ≤ x < 1)',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'RCL': {'description': 'Recall data into the x-register. Parameter: register '
                        'or variable (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                       '+= 1, var2 = myvar or even expressions like myvar *= '
                       'var3/(2-1)',
         'supported': 'No'},
 'RCL+': {'description': 'Recall addition. Recall data and add it to the '
                         'contents of the x-register. Parameter: register or '
                         'variable (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                        '+= 1, var2 = myvar or even expressions like myvar *= '
                        'var3/(2-1)',
          'supported': 'No'},
 'RCL-': {'description': 'Recall subtraction. Recall data and subtract it from '
                         'the contents of the x-register. Parameter: register '
                         'or variable (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                        '+= 1, var2 = myvar or even expressions like myvar *= '
                        'var3/(2-1)',
          'supported': 'No'},
 'RCLEL': {'description': 'Recall element. Recalls the current matrix element '
                          'from the indexed matrix.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                         'instead - read help for more info',
           'supported': 'No'},
 'RCLIJ': {'description': 'Recall the row- and column-pointer values (I and J) '
                          'for the indexed matrix.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                         'instead - read help for more info',
           'supported': 'No'},
 'RCL×': {'description': 'Recall multiplication. Recall data and multiply it '
                         'by the contents of the x-register. Parameter: '
                         'register or variable (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                        '+= 1, var2 = myvar or even expressions like myvar *= '
                        'var3/(2-1)',
          'supported': 'No'},
 'RCL÷': {'description': 'Recall division. Recall data and divide it into the '
                         'contents of the x-register. Parameter: register or '
                         'variable (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                        '+= 1, var2 = myvar or even expressions like myvar *= '
                        'var3/(2-1)',
          'supported': 'No'},
 'RDX,': {'description': 'Select a comma to be used as the radix mark (decimal '
                         'point).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'RDX.': {'description': 'Select a period to be used as the radix mark '
                         '(decimal point).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'REAL?': {'description': 'If the x-register contains a real number, execute '
                          'the next program line; if the x-register does not '
                          'contain a real number, skip the next program line.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'REALRES': {'description': "Real-results. Disables the calculator's ability "
                            'to return a complex result using real-number '
                            'inputs.',
             'indirect_allowed': False,
             'num_arg_fragments': 0,
             'suggestion': 'being researched',
             'supported': ''},
 'RECT': {'description': 'Select Rectangular coordinate mode for displaying '
                         'complex numbers.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'RND': {'description': 'Round the number in the x-register using the current '
                        'display format.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'being researched',
         'supported': ''},
 'RNRM': {'description': 'Return the row norm of the matrix in the x-register.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'ROTXY': {'description': 'Rotate the 36-bit number in the y-register by x '
                          'bits.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'RSUM': {'description': 'Return the row sum of each row of the matrix in the '
                         'x-register and returns the sums in a column matrix.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'RTN': {'description': 'Return. In a running program, branches the program '
                        'pointer back to the line following the most recent '
                        'XEQ instruction. If there is no matching XEQ '
                        'instruction, program execution halts. From the '
                        'keyboard, RTN moves the program pointer to line 00 of '
                        'the current program.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': 'Use the Python "return" statement instead'},
 'R↑': {'description': 'Roll up the contents of the four stack registers one '
                       'position.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'Use Python variables',
        'supported': 'No'},
 'R↓': {'description': 'Roll down the contents of the four stack registers one '
                       'position.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'Use Python variables',
        'supported': 'No'},
 'SCI': {'description': 'Select scientific notation display format. Parameter: '
                        'number of digits (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'being researched',
         'supported': ''},
 'SDEV': {'description': 'Standard deviation. Returns sx and sy using the '
                         'current statistical data.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'SEED': {'description': 'Store a seed for the random number generator.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'SF': {'description': 'Set flag nn (00 ≤ nn ≤ 35; 81 ≤ nn ≤ 99). Parameter: '
                       'flag number (indirect allowed)',
        'indirect_allowed': True,
        'num_arg_fragments': 1,
        'suggestion': '',
        'supported': '✓'},
 'SIGN': {'description': 'Sign. Return 1 for x ≥ 0, –1 for x < 0, and 0 for '
                         'non-numbers. Returns the unit vector of a complex '
                         'number.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'SIN': {'description': 'Sine. Returns sin(x).',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'SINH': {'description': 'Hyperbolic sine. Returns sinh(x).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'SIZE': {'description': 'Set the number of storage registers. Parameter: '
                         'number of registers.',
          'indirect_allowed': False,
          'num_arg_fragments': 1,
          'suggestion': 'being researched',
          'supported': ''},
 'SLOPE': {'description': 'Return the slope of the linear transformation of '
                          'the current curve-fitting model.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'SOLVE': {'description': 'Solve for an unknown variable. Parameter: variable '
                          'name (indirect allowed)',
           'indirect_allowed': True,
           'num_arg_fragments': 1,
           'suggestion': 'being researched',
           'supported': ''},
 'SQRT': {'description': 'Square root. Returns √x.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'SST': {'description': 'Single step. Moves the program pointer to the next '
                        'program line. (Not programmable.)',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': 'Not programmable'},
 'STO': {'description': 'Store a copy of x into a destination register or '
                        'variable. Parameter: register or variable (indirect '
                        'allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                       '+= 1, var2 = myvar or even expressions like myvar *= '
                       'var3/(2-1)',
         'supported': 'No'},
 'STO+': {'description': 'Store addition. Adds x to an existing register or '
                         'variable. Parameter: register or variable (indirect '
                         'allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                        '+= 1, var2 = myvar or even expressions like myvar *= '
                        'var3/(2-1)',
          'supported': 'No'},
 'STOEL': {'description': 'Store element. Stores a copy of x into the current '
                          'element of the indexed matrix.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                         'instead - read help for more info',
           'supported': 'No'},
 'STOIJ': {'description': 'Moves the row- and column-pointers to I = x and J = '
                          'y in the indexed matrix.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                         'instead - read help for more info',
           'supported': 'No'},
 'STOP': {'description': 'Stop program execution. (R/S in program entry mode).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'STO×': {'description': 'Store multiplication. Multiplies an existing '
                         'register or variable by x. Parameter: register or '
                         'variable (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                        '+= 1, var2 = myvar or even expressions like myvar *= '
                        'var3/(2-1)',
          'supported': 'No'},
 'STO÷': {'description': 'Store division. Divides an existing register or '
                         'variable by x. Parameter: register or variable '
                         '(indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                        '+= 1, var2 = myvar or even expressions like myvar *= '
                        'var3/(2-1)',
          'supported': 'No'},
 'STO–': {'description': 'Store subtraction. Subtracts x from an existing '
                         'register or variable. Parameter: register or '
                         'variable (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'Use Python variables instead, e.g. myar = 100, myvar '
                        '+= 1, var2 = myvar or even expressions like myvar *= '
                        'var3/(2-1)',
          'supported': 'No'},
 'STR?': {'description': 'If the x-register contains an Alpha string, execute '
                         'the next program line; if the x-register does not '
                         'contain an Alpha string, skip the next program line.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'SUM': {'description': 'Returns the sums Σx and Σy into the x- and '
                        'y-registers.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'being researched',
         'supported': ''},
 'TAN': {'description': 'Tangent. Returns tan(x).',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': '✓'},
 'TANH': {'description': 'Hyperbolic tangent. Returns tanh(x).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'TONE': {'description': 'Sounds a tone. Parameter: tone number (0–9) '
                         '(indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': '',
          'supported': '✓'},
 'TRACE': {'description': 'Select Trace printing mode, which prints a record '
                          'of keystrokes and results.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'TRANS': {'description': 'Return the transpose of the matrix in the '
                          'x-register.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': '',
           'supported': '✓'},
 'UVEC': {'description': 'Unit vector. Return the unit vector for the matrix '
                         'or complex number in the x-register.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': '',
          'supported': '✓'},
 'VARMENU': {'description': 'Create a variable menu using MVAR instructions '
                            'following the specified global label. Parameter: '
                            'global program label. (indirect allowed)',
             'indirect_allowed': True,
             'num_arg_fragments': 1,
             'suggestion': '',
             'supported': 'yes though also look at extra fancy varmenu() '
                          'command in help'},
 'VIEW': {'description': 'View the contents of a register or variable. '
                         'Parameter: register or variable (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': '',
          'supported': '✓'},
 'WMEAN': {'description': 'Weighted mean. Return the mean of x-values weighted '
                          'by the y-values  Σxy / Σ y',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'WRAP': {'description': 'Select Wrap mode, which prevents the indexed matrix '
                         'from growing.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                        'instead - read help for more info',
          'supported': 'No'},
 'X<0?': {'description': ' X less than zero test. If true, execute the next '
                         'program line; if false, skip the next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X<>': {'description': 'Swaps the contents of the x-register with another '
                        'register or variable. Parameter: register or variable '
                        '(indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': 'Use Python variables',
         'supported': 'No'},
 'X<>Y': {'description': 'Swaps the contents of the x- and y-registers.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python variables',
          'supported': 'No'},
 'X<Y?': {'description': ' X less than y test. If true, execute the next '
                         'program line; if false, skip the next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X=0?': {'description': ' X equal to zero test. If true, execute the next '
                         'program line; if false, skip the next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X=Y?': {'description': ' X equal to y test. If true, execute the next '
                         'program line; if false, skip the next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X>0?': {'description': 'X greater than zero test. If true, execute the next '
                         'program line; if false, skip the next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X>Y?': {'description': 'X greater than y test. If true, execute the next '
                         'program line; if false, skip the next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'XEQ': {'description': 'Execute a function or program. Parameter: function or '
                        'label (indirect allowed)',
         'indirect_allowed': True,
         'num_arg_fragments': 1,
         'suggestion': '',
         'supported': 'na Just call a function e.g. myfunc()'},
 'XOR': {'description': 'Logical XOR (exclusive OR). Returns x XOR y.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'Use built in Python boolean operators instead e.g. not '
                       'val or val2 and val3',
         'supported': 'No'},
 'XTOA': {'description': ' X to Alpha. Appends a character (specified by the '
                         'code in the x-register) to the Alpha register. If '
                         'the x-register contains an Alpha string, appends the '
                         'entire string.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'X↑2': {'description': 'Square. Returns x2.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': 'Use y**2 syntax instead'},
 'X≠0?': {'description': ' X not equal to zero test. If true, execute the next '
                         'program line; if false, skip the next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X≠Y?': {'description': 'X not equal to y test. If true, execute the next '
                         'program line; if false, skip the next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X≤0?': {'description': ' X less than or equal to zero test. If true, execute '
                         'the next program line; if false, skip the next '
                         'program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X≤Y?': {'description': ' X less than or equal to y test. If true, execute '
                         'the next program line; if false, skip the next '
                         'program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X≥0?': {'description': 'X greater than or equal to zero test. If true, '
                         'execute the next program line; if false, skip the '
                         'next program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'X≥Y?': {'description': 'X greater than or equal to y test. If true, execute '
                         'the next program line; if false, skip the next '
                         'program line',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'Use Python "if" statements instead',
          'supported': 'No'},
 'YINT': {'description': 'y-intercept. Returns the y-intercept of the curve '
                         'fitted to the current statistical data.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 'Y↑X': {'description': 'Power. Returns yx.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': '',
         'supported': 'Use y**x syntax instead'},
 '×': {'description': 'Multiplication. Returns x × y.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': '',
       'supported': '✓'},
 '÷': {'description': 'Division. Returns y / x.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': '',
       'supported': '✓'},
 'Σ+': {'description': 'Summation plus. Accumulate a pair of x- and y values '
                       'into the summation registers.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'being researched',
        'supported': ''},
 'ΣREG': {'description': 'Summation registers. Defines which storage register '
                         'begins the block of summation registers. Parameter: '
                         'register number (indirect allowed)',
          'indirect_allowed': True,
          'num_arg_fragments': 1,
          'suggestion': 'being researched',
          'supported': ''},
 'ΣREG?': {'description': 'Return the register number of the first summation '
                          'register.',
           'indirect_allowed': False,
           'num_arg_fragments': 0,
           'suggestion': 'being researched',
           'supported': ''},
 'Σ–': {'description': 'Summation minus. Subtract a pair of x- and y-values '
                       'from the summation registers.',
        'indirect_allowed': False,
        'num_arg_fragments': 0,
        'suggestion': 'being researched',
        'supported': ''},
 '–': {'description': 'Subtraction. Returns y – x.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': '',
       'supported': '✓'},
 '←': {'description': 'Move left one element in the indexed matrix.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                     'instead - read help for more info',
       'supported': 'No'},
 '↑': {'description': 'Move up one element in the indexed matrix.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                     'instead - read help for more info',
       'supported': 'No'},
 '→': {'description': 'Move right one element in the indexed matrix.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                     'instead - read help for more info',
       'supported': 'No'},
 '→DEC': {'description': 'To decimal. Converts the octal (base 8) '
                         'representation of a number to decimal (base 10). '
                         'Note: This function is included to provide program '
                         'compatibility with the HP-41 (which uses the '
                         'function name DEC).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 '→DEG': {'description': 'To degrees. Convert an angle-value from radians to '
                         'degrees. Returns x×(180/π).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 '→HMS': {'description': 'To hours, minutes, and seconds. Convert x from a '
                         'decimal fraction to a minutes-seconds format.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 '→HR': {'description': 'To hours. Converts x from a minutes-seconds format to '
                        'a decimal fraction.',
         'indirect_allowed': False,
         'num_arg_fragments': 0,
         'suggestion': 'being researched',
         'supported': ''},
 '→OCT': {'description': 'To octal. Converts a decimal number to the octal '
                         'representation. Note: This function is included to '
                         'provide program compatibility with the HP-41 (which '
                         'uses the function name OCT).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 '→POL': {'description': 'To polar. Converts x and y to the corresponding '
                         'polar coordinates r and θ. If the x-register '
                         'contains a complex number, converts the two parts of '
                         'the number to polar values.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 '→RAD': {'description': 'To radians. Converts a angle value in degrees to '
                         'radians. Returns x×(π/180).',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 '→REC': {'description': 'To rectangular. Converts r (in the x-register) and θ '
                         '(in the y-register) to the corresponding rectangular '
                         'coordinates, x and y. If the X-register contains a '
                         'complex number, converts the two parts of the number '
                         'to rectangular values.',
          'indirect_allowed': False,
          'num_arg_fragments': 0,
          'suggestion': 'being researched',
          'supported': ''},
 '↓': {'description': 'Move down one element in the indexed matrix.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': 'Use Python matrix/list indexing and slicing syntax '
                     'instead - read help for more info',
       'supported': 'No'},
 '◄': {'description': 'Backspace or clear x-register. In Program entry mode, '
                      'deletes the current program line.',
       'indirect_allowed': False,
       'num_arg_fragments': 0,
       'suggestion': '',
       'supported': 'not programmable'}}