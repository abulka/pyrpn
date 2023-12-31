import unittest
from test_base import BaseTest
from de_comment import de_comment
from textwrap import dedent
import logging
from logger import config_log
from rpn import RpnError
from parse import parse
import settings

log = logging.getLogger(__name__)
config_log(log)

class RpnTests3Cmds(BaseTest):

    def parse(self, text):
        self.program = parse(text, debug_options={'dump_ast': True, 'emit_pyrpn_lib': False})
        self.program.dump()

    def compare(self, expected, keep_comments=False):
        self.assertEqual(expected.strip(), self.program.lines_to_str(comments=keep_comments).strip())

    # TESTS

    # Matrices

    """
    np.zeros((5,8), np.int)
    
    """

    # Radical idea for avoiding the need for
    # INDEX, STOIJ, RCLIJ       replaced with slicing
    # I+, I-, J+, J-            syntaxtically not allowed in python, use python indexing and slicing
    # PUTM, GETM                replaced with slicing
    # INSR and DELR             replaced with m.insr(1) and m.delr(1)

    def test_matrices_newmat(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            """)
        self.compare(de_comment(expected))

    def test_matrices_index_numpy_literal(self):
        """
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            y = x[0,2]
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            INDEX "x"
            1
            3
            STOIJ
            RDN
            RDN
            RCLEL
            STO 00
            """)
        self.compare(de_comment(expected))

    def test_matrices_index_numpy_dynamic(self):
        """
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            row = 0
            y = x[row,2]
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            0
            STO 00      // y

            INDEX "x"
            RCL 00
            1
            +           // adjust from 0 based python to 1 based hp42s
            3
            STOIJ
            RDN
            RDN
            RCLEL
            STO 01
            """)
        self.compare(de_comment(expected))

    def test_matrices_index_numpy_for_loop(self):
        """
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            for col in range(4):
                x[0, col]
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            -1.003
            STO 00  // i =
                        
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            
            INDEX "x"
            1           // row, +1 adjusted
            RCL 00      // col
            IP          //<--- needs to happen before the adjust cos might be -0.003 which needs to be IP into 0
            1
            +           // adjust from 0 based python to 1 based hp42s
            STOIJ
            RDN
            RDN
            RCLEL

            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected))

    def test_matrices_index_numpy_store_literal(self):
        """
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x[0,2] = 100
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            100
            INDEX "x"
            1
            3
            STOIJ
            RDN
            RDN
            STOEL
            """)
        self.compare(de_comment(expected))

    def test_matrices_index_numpy_store_dynamic(self):
        """
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            row = 0
            x[row,2] = 100
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            0
            STO 00      // y

            100
            INDEX "x"
            RCL 00
            1           // adjust from 0 based python to 1 based hp42s
            +
            3
            STOIJ
            RDN
            RDN
            STOEL
            """)
        self.compare(de_comment(expected))

    def test_matrices_getm(self):
        """
        Radical idea for avoiding the need for GETM

        GETM recalls the submatrix to the X-register.
            1. Move the index pointers to the first element of the submatrix.
            2. Enter the dimensions of the submatrix: number of rows in the Y-
                register and number of columns in the X-register.
            3. Execute the GETM (get matrix) function (. 1MATRIX 1  .U l)·
                GETM recalls the submatrix to the X-register.
        """
        self.parse(dedent("""
            x = NEWMAT(10,11)   # 10x11 matrix (ten rows, eleven columns) viz. np.zeros((10,11), np.int) zero based thus 0..9 rows 0..10 cols
            n = x[0:5, 1:6]     # alternative to GETM - uses pythonic numpy syntax, no messing with IJ
            """))
        expected = dedent("""
            10
            11
            NEWMAT
            STO "x"

            INDEX "x"
            1              // from
            2
            STOIJ
            5              // size of sub-matrix to extract
            6
            XEQ "pMxSubm"  // (row_from, row_to, col_from, col_to) -> (row_size, col_size) - Converts from 0 based 
                           // Python slice into 1 based size values for GETM
            GETM
            STO "n"
            """)
        self.compare(de_comment(expected))

    def test_matrices_putm(self):
        """
        Radical idea for avoiding the need for PUTM

        PUTM copies the matrix in the X-register, element for element, into the indexed matrix beginning at the current element.
            1. Move the index pointers to the element where you want the first element of the submatrix to go.
            2. Execute the PUTM (put matrix) function. PUTM copies the matrix in the X-register,
            element for element, into the indexed matrix beginning at the current element.

        Numpy version:
            import numpy as np

            zeros = np.zeros((270,270))
            ones = np.ones((150,150))
            zeros[60:210,60:210] = ones

            x = np.zeros((10,11), np.int)
            z = np.ones((2,3), np.int)
            x[2:4, 5:8] = z    # cannot use [2,5]. the trick is to just add the size to the 'to' values 2 and 5 e.g. 2+2=4, 5+3=8
                               # aha, but could use [2:,5:] since HP42S doesn't check or care.
        """
        self.parse(dedent("""
            x = NEWMAT(10,11)   # 10x11 matrix
            z = NEWMAT(2,3)     # 2x3 matrix
            x[2:4, 5:8] = z     # alternative to PUTM - uses pythonic numpy syntax, no messing with IJ
            """))
        expected = dedent("""
            10
            11
            NEWMAT
            STO "x"

            2
            3
            NEWMAT
            STO "z"

            RCL "z"
            
            INDEX "x"
            3              // from
            6
            STOIJ
            RDN
            RDN
            PUTM
            """)
        self.compare(de_comment(expected))

    def test_matrices_putm_simpler(self):
        """
        aha, allow [2:,5:] since HP42S doesn't check or care about the upper 'to'.  This is actually not allowed in numpy - but hey!
        don't allow [2,5] since that is single element assignment syntax.

        import numpy as np
        x = np.zeros((10,11), np.int)
        z = np.ones((2,3), np.int)
        x[2:4, 5:8] = z

        # x[2, 5] = z  FAILS
        # x[2:, 5:] = z  FAILS
        """
        self.parse(dedent("""
            x = NEWMAT(10,11)   # 10x11 matrix
            z = NEWMAT(2,3)     # 2x3 matrix
            x[2:, 5:] = z         # alternative to PUTM - uses pythonic numpy syntax, no messing with IJ
            """))
        expected = dedent("""
            10
            11
            NEWMAT
            STO "x"

            2
            3
            NEWMAT
            STO "z"

            RCL "z"
            
            INDEX "x"
            3              // from
            6
            STOIJ
            RDN
            RDN
            PUTM
            """)
        self.compare(de_comment(expected))

    def test_matrices_insert_row(self):
        """
        Inserting and deleting rows
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x.insr(1)
            x.delr(2)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            INDEX "x"
            1
            1           // always the same, col is irrelevant to insertion of rows
            STOIJ
            RDN
            RDN
            INSR

            INDEX "x"
            2
            1           // always the same, col is irrelevant to deletion of rows
            STOIJ
            RDN
            RDN
            DELR
            """)
        self.compare(de_comment(expected))

    def test_matrices_insr_non_existing(self):
        src = dedent("""
            x.insr()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_matrices_insr_needs_args(self):
        src = dedent("""
            x = NEWMAT(1,4)
            x.insr()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_matrices_dim_existing(self):
        # redimension a matrix
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x.dim(12,15)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            12
            15
            DIM "x"
            """)
        self.compare(de_comment(expected))

    def test_matrices_dim_non_existing(self):
        # redimension a matrix that doesn't exist - should be an error
        src = dedent("""
            x.dim(12,15)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_matrices_dim_needs_args(self):
        src = dedent("""
            x = NEWMAT(1,4)
            x.dim()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_matrices_dim_needs_args_more(self):
        src = dedent("""
            x = NEWMAT(1,4)
            x.dim(1)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_matrices_not_supported(self):
        # various unsupported matrix related commands - use pythonic and numpy alternatives !
        for func in settings.MATRIX_UNSUPPORTED:
            src = dedent(f"""
                {func}(1)
                """)
            # self.assertRaises(RpnError, self.parse, dedent(src))
            with self.assertRaises(RpnError, msg=f'no exception raised for {func}'):
                self.parse(dedent(src))

    # more matrix operations

    def test_matrices_multiply_scalar(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x *= 3.5
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            3.5
            STO* "x"
            """)
        self.compare(de_comment(expected))

    def test_matrices_multiply_scalar_more(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x -= 3
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            3
            STO- "x"
            """)
        self.compare(de_comment(expected))

    def test_matrices_sin(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            SIN(x)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            RCL "x"
            SIN
            """)
        self.compare(de_comment(expected))

    def test_matrices_sin_and_store(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x = SIN(x)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            RCL "x"
            SIN
            STO "x"
            """)
        self.compare(de_comment(expected))

    # Matrix manipulation

    def test_matrices_invert_trans_det(self):
        """
        These all act on the matrix in x, thus operate
        like any other command
            INVRT
            TRANS
            DET
            FNRM
            RSUM
            UVEC
            DOT(m1, m2) - returns matrix
            CROSS(m1, m2) - returns matrix
            RNRM - returns a number
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            INVRT(x)
            TRANS(x)
            DET(x)
            FNRM(x)
            RSUM(x)
            UVEC(x)
            RNRM(x)
            DOT(x, x)
            CROSS(x, x)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            RCL "x"
            INVRT
            RCL "x"
            TRANS
            RCL "x"
            DET
            RCL "x"
            FNRM
            RCL "x"
            RSUM
            RCL "x"
            UVEC
            RCL "x"
            RNRM
            RCL "x"
            RCL "x"
            DOT
            RCL "x"
            RCL "x"
            CROSS
            """)
        self.compare(de_comment(expected))

        """
        Actually grow and wrap and -> and <- navigation
        together with STOEL and RCLEL could be handy.
        But don't want to get into supporting INDEX and the
        idea of a current matrix. Could perhaps support
            GROW(x)
            WRAP(x)
            x.row_I_plus
            x.row_I_minus
            x.col_J_plus
            x.col_J_minus
            x.stoel(val)
            RCLEL(x)
        but what if we do things like
            x.stoel( m[1,2] )
        where accessing matrix 'm' wrecks IJ on matrix 'x'.

        Might be simpler to ban all the above, and if you
        want to grow by one row, this is really append, so offer
            x.appendr()
        and if want to incrementally set values into the matrix
        then bad luck.  Or just
            for row in range(10):
                for col in range(5):
                    m[row,col] = val
        If you know how much data there is, as you would
        when programmatically doing stuff, then you can redim
        the matrix before looping, or add or insert extra rows.
        """

    def test_matrices_row_swap(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x.row_swap(1,2)     # 0 based
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            INDEX "x"
            1
            2
            R<>R
            """)
        self.compare(de_comment(expected))

    def test_matrices_appendr(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x.appendr()
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            INDEX "x"
            GROW
            J-
            J+
            WRAP
            """)
        self.compare(de_comment(expected))

    # Complex numbers

    def test_complex_create(self):
        self.parse(dedent("""
            c = COMPLEX(1, 0)
            """))
        expected = dedent("""
            1
            0
            COMPLEX        
            STO "c"
            """)
        self.compare(de_comment(expected))

    def test_complex_create_pythonic(self):
        self.parse(dedent("""
            x = 1 + 0j
            """))
        expected = dedent("""
            1
            0
            COMPLEX        
            STO "x"
            """)
        self.compare(de_comment(expected))

    def test_complex_create_pythonic_minus(self):
        self.parse(dedent("""
            x = 7 - 9j
            """))
        expected = dedent("""
            7
            9
            +/-
            COMPLEX        
            STO "x"
            """)
        self.compare(de_comment(expected))

    def test_complex_create_letter_j_varname(self):
        # Don't get tricked by the last letter of a variable being 'j'
        self.parse(dedent("""
            x = 7 - blahj
            """))
        expected = dedent("""
            7
            RCL 00
            -
            STO 01
            """)
        self.compare(de_comment(expected))

    def test_complex_add(self):
        # Don't get tricked by the last letter of a variable being 'j'
        self.parse(dedent("""
            c = (5 + 3j) + (7 - 9j)
            """))
        expected = dedent("""
            5
            3
            COMPLEX
            7
            9
            +/-
            COMPLEX
            +
            STO "c"
            """)
        self.compare(de_comment(expected))

    def test_complex_one_param(self):
        self.parse(dedent("""
            c = COMPLEX(0,1)
            real, imag = COMPLEX(c)  # if one param and its complex, then return real and imag 
            """))
        expected = dedent("""
            0
            1
            COMPLEX        
            STO "c"
            RCL "c"
            COMPLEX
            STO 00  // imaginary
            RDN
            STO 01  // real
            """)
        self.compare(de_comment(expected))

    def test_complex_matrix(self):
        self.parse(dedent("""
            a = NEWMAT(1,4)
            b = NEWMAT(1,4)
            x = COMPLEX(a, b)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "a"
            1
            4
            NEWMAT
            STO "b"
            RCL "a"
            RCL "b"
            COMPLEX        
            STO "x"
            """)
        self.compare(de_comment(expected))

    def test_complex_matrix_to_real(self):
        # Converting a Complex Matrix to Real again
        self.parse(dedent("""
            a = NEWMAT(1,4)
            b = NEWMAT(1,4)
            x = COMPLEX(a, b)
            a, b = COMPLEX(x)  # converts into two matrices
            
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "a"
            1
            4
            NEWMAT
            STO "b"
            RCL "a"
            RCL "b"
            COMPLEX        
            STO "x"
            
            RCL "x"
            COMPLEX        
            STO "b"
            RDN
            STO "a"
            """)
        self.compare(de_comment(expected))

    def test_complex_matrix_subscript(self):
        # Accessing a complex matrix cell should store the value into a named variable
        self.parse(dedent("""
            a = NEWMAT(1,4)
            b = NEWMAT(1,4)
            cm = COMPLEX(a, b)
            val = cm[0,0]
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "a"
            1
            4
            NEWMAT
            STO "b"
            RCL "a"
            RCL "b"
            COMPLEX        
            STO "cm"
            
            INDEX "cm"
            1
            1
            STOIJ
            RDN
            RDN
            RCLEL
            STO "val"   // <--- this is the trick, to make this named
            """)
        self.compare(de_comment(expected))

    def test_complex_matrix_subscript_store(self):
        # Storing complex number into a complex matrix cell
        self.parse(dedent("""
            a = NEWMAT(1,4)
            b = NEWMAT(1,4)
            cm = COMPLEX(a, b)
            cm[0,0] = (5 + 3j)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "a"
            1
            4
            NEWMAT
            STO "b"
            RCL "a"
            RCL "b"
            COMPLEX        
            STO "cm"
            
            5
            3
            COMPLEX
            INDEX "cm"
            1
            1
            STOIJ
            RDN
            RDN
            STOEL
            """)
        self.compare(de_comment(expected))

    def test_matrix_mulitiply(self):
        # multiply two matrices
        self.parse(dedent("""
            m1 = NEWMAT(2,2)
            m2 = NEWMAT(2,2)
            mresult = m1 * m2
            """))
        expected = dedent("""
            2
            2
            NEWMAT
            STO "m1"
            2
            2
            NEWMAT
            STO "m2"
            RCL "m1"
            RCL "m2"
            *
            STO "mresult"
            """)
        self.compare(de_comment(expected))

    def test_matrix_sine(self):
        # multiply two matrices
        self.parse(dedent("""
            m1 = NEWMAT(2,2)
            mresult = SIN(m1)
            """))
        expected = dedent("""
            2
            2
            NEWMAT
            STO "m1"
            RCL "m1"
            SIN
            STO "mresult"
            """)
        self.compare(de_comment(expected))

    def test_matrix_len(self):
        # multiply two matrices
        self.parse(dedent("""
            m1 = NEWMAT(2,2)
            mresult = len(m1)
            """))
        expected = dedent("""
            2
            2
            NEWMAT
            STO "m1"
            RCL "m1"
            XEQ "pMxLen"
            STO "mresult"
            """)
        self.compare(de_comment(expected))

    # Cmd mapping

    def test_cmd_cmd_e_to_x(self):
        # Converting a Complex Matrix to Real again
        self.parse(dedent("""
            Eto(10)
            """))
        expected = dedent("""
            10
            E↑X
            """)
        self.compare(de_comment(expected))

    # command num args enforcement

    def test_cmd_agraph(self):
        # Puts alpha chars into pixels at row col coords
        self.parse(dedent("""
            AGRAPH(1,1)
            """))
        expected = dedent("""
            1
            1
            AGRAPH
            """)
        self.compare(de_comment(expected))

    def test_cmd_agraph_no_params(self):
        src = dedent("""
            AGRAPH()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_cmd_agraph_not_enough_params(self):
        src = dedent("""
            AGRAPH(1)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    # INPUT named variables

    def test_cmd_input(self):
        self.parse(dedent("""
            INPUT(fred)
            Reciprocal(fred)
            """))
        expected = dedent("""
            INPUT "fred"
            RCL "fred"
            1/X
            """)
        self.compare(de_comment(expected))

    def test_cmd_input_integ_prv(self):
        self.parse(dedent("""
            INPUT(fred)
            INTEG(mary)
            PRV(sam)
            """))
        expected = dedent("""
            INPUT "fred"
            INTEG "mary"
            PRV "sam"
            """)
        self.compare(de_comment(expected))

    def test_cmd_input_str(self):
        # Although this is the original syntax, its not allowed
        src = dedent("""
            INPUT("fred")
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_cmd_input_no_args(self):
        # Although this is the original syntax, its not allowed
        src = dedent("""
            INPUT()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_cmd_input_regs_not_allowed(self):
        # Although specifying registers is in the original syntax, its not allowed
        src = dedent("""
            INPUT(00)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_cmd_size(self):
        self.parse(dedent("""
            SIZE(50)
            """))
        expected = dedent("""
            SIZE 0050
            """)
        self.compare(de_comment(expected))

    def test_cmd_rdx(self):
        self.parse(dedent("""
            RDXcomma()
            RDXperiod()
            """))
        expected = dedent("""
            RDX,
            RDX.
            """)
        self.compare(de_comment(expected))

    def test_cmd_isreal(self):
        self.parse(dedent("""
            isREAL(20)
            """))
        expected = dedent("""
            20
            XEQ "pREAL"
            """)
        self.compare(de_comment(expected))

    def test_cmd_testbit(self):
        self.parse(dedent("""
            testBIT(20,2)
            """))
        expected = dedent("""
            20
            2
            XEQ "pBIT"
            """)
        self.compare(de_comment(expected))

    def test_cmd_iscpx(self):
        self.parse(dedent("""
            isCPX(20)
            """))
        expected = dedent("""
            20
            XEQ "pCPX"
            """)
        self.compare(de_comment(expected))

    def test_cmd_ismatrix(self):
        self.parse(dedent("""
            isMAT(20)
            """))
        expected = dedent("""
            20
            XEQ "pMAT"
            """)
        self.compare(de_comment(expected))

    def test_cmd_isstr(self):
        self.parse(dedent("""
            isSTR("fred")
            """))
        expected = dedent("""
            "fred"
            XEQ "pSTR"
            """)
        self.compare(de_comment(expected))

    def test_cmd_posa(self):
        self.parse(dedent("""
            POSA("C")
            """))
        expected = dedent("""
            "C"
            POSA
            """)
        self.compare(de_comment(expected))

    def test_cmd_editn_matrix(self):
        self.parse(dedent("""
            m = NEWMAT(1,4)
            EDITN(m)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "m"

            EDITN "m"
            """)
        self.compare(de_comment(expected))

    def test_cmd_edit_matrix(self):
        # map edit to editn - same thing
        self.parse(dedent("""
            m = NEWMAT(1,4)
            EDIT(m)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "m"

            EDITN "m"
            """)
        self.compare(de_comment(expected))

    def test_cmd_clp_pgmint_take_funcname(self):
        self.parse(dedent("""
            CLP("myfunc")
            PGMINT("myfunc")
            PGMSLV("myfunc")
            """))
        expected = dedent("""
            CLP "myfunc"
            PGMINT "myfunc"
            PGMSLV "myfunc"
            """)
        self.compare(de_comment(expected))

    def test_cmd_x_to_a(self):
        self.parse(dedent("""
            XTOA(30)
            XTOA("somestr")
            """))
        expected = dedent("""
            30
            XTOA
            "somestr"
            XTOA
            """)
        self.compare(de_comment(expected))

    # number of parameters checking for 'pure', 'renamed' and 'replaced' scenarios

    def test_numargs_pure_not_enough_args(self):
        src = dedent("""
            SIN()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_numargs_pure_too_many_args(self):
        src = dedent("""
            SIN(1,2,3,4)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_numargs_renamed_not_enough_args(self):
        src = dedent("""
            Reciprocal()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_numargs_renamed_too_many_args(self):
        src = dedent("""
            Reciprocal(1,2,3,4)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_numargs_replaced_no_args(self):
        src = dedent("""
            testBIT()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_numargs_replaced_not_enough_args(self):
        src = dedent("""
            testBIT(1)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_numargs_replaced_too_many_args(self):
        src = dedent("""
            testBIT(1,2,3,4)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    # multiple return values

    """
    Run this to assert that multiple values from a return statement work
    both for user defined functions and also for built in 42S commands.
    
    def dim_matrix():
      m = NEWMAT(1, 4)
      rows, cols = whatDIM(m)
      assert rows == 1
      assert cols == 4
    
      m.dim(2,3)
      rows, cols = whatDIM(m)
      assert rows == 2
      assert cols == 3
      PROMPT('matrix dim functions ok')
      multret()
      
    def multret():
        a, b = calc(1, 2)
        assert a == 100
        assert b == 3
        print("multiple return values works ok")
        
    def calc(a,b):
        c = a * 100
        return c, b+1    
    """

    def test_multiple_return(self):
        self.parse(dedent("""
            def multret():
                a = 99
                a, b = calc(1, 2)
                assert a == 100
                assert b == 3
                
            def calc(a,b):
                c = a * 100
                return c, b+1
            """))
        expected = dedent("""
            LBL "multret"
            99
            STO 00          // a
            1
            2
            XEQ A           // calc()
            STO 01          // b
            RDN
            STO 00          // a
            
            RCL 00
            100
            XEQ "pEQ"
            XEQ "pAssert"
            RCL 01
            3
            XEQ "pEQ"
            XEQ "pAssert"
            RTN
            
            LBL A           // def calc():
            XEQ "p2Param"
            STO 02
            RDN
            STO 03
            RDN
            RCL 02
            100
            *
            STO 04
            
            // return c, b+1
            
            RCL 04          // c
            RCL 03          // b
            1
            +
            RTN
            """)
        self.compare(de_comment(expected))

    def test_toPOL(self):
        # multiple return values used here for the first time
        # Converts x and y to the corresponding polar coordinates r and θ.
        self.parse(dedent("""
            a, b = toPOL(1, 2)
            a  # recall 'a' onto the stack to check which register gets recalled
            """))
        expected = dedent("""
            1
            2
            →POL
            STO 00  // b (because b is the first to get accessed it gets dibs on reg 00)
            RDN
            STO 01  // a
            RCL 01  // a
            """)
        self.compare(de_comment(expected))

    def test_toPOL_complex(self):
        # one param version,
        # If the x-register contains a complex number, converts the two parts of the number to polar values.
        self.parse(dedent("""
            c = (0+1j)
            c2 = toPOL(c)  # complex number into a complex number
            """))
        expected = dedent("""
            0
            1
            COMPLEX
            STO "c"
            RCL "c"
            →POL
            STO "c2"
            """)
        self.compare(de_comment(expected))

    def test_toREC(self):
        self.parse(dedent("""
            a, b = toREC(1, 2)
            """))
        expected = dedent("""
            1
            2
            →REC
            STO 00  // b (because b is the first to get accessed it gets dibs on reg 00)
            RDN
            STO 01  // a
            """)
        self.compare(de_comment(expected))

    def test_toREC_complex(self):
        self.parse(dedent("""
            c = (0+1j)
            c2 = toREC(c)  # complex number into a complex number
            """))
        expected = dedent("""
            0
            1
            COMPLEX
            STO "c"
            RCL "c"
            →REC
            STO "c2"
            """)
        self.compare(de_comment(expected))

    def test_toPOL_no_args(self):
        src = dedent("""
            toPOL()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_toREC_no_args(self):
        src = dedent("""
            toREC()
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_toPOL_too_many_args(self):
        src = dedent("""
            toPOL(1,2,3)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_toREC_too_many_args(self):
        src = dedent("""
            toREC(1,2,3)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_cmd_what_dim(self):
        # multiple return values used here
        self.parse(dedent("""
            rows = 99
            cols = 98
            m = NEWMAT(1, 4)
            rows, cols = whatDIM(m)
            """))
        expected = dedent("""
            99
            STO 00  // rows
            98
            STO 01  // cols
            1
            4
            NEWMAT
            STO "m"        
            RCL "m"
            DIM?
            STO 01  // cols          
            RDN
            STO 00  // rows
            """)
        self.compare(de_comment(expected))

    # Mod

    def test_cmd_mod(self):
        # % operator
        self.parse(dedent("""
            7 % 2
            """))
        expected = dedent("""
            7
            2
            MOD
            """)
        self.compare(de_comment(expected))

    # warn about nonexistent python features

    def test_no_import(self):
        src = dedent("""
            import blah
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_no_math(self):
        src = dedent("""
            math.sin(20)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_no_sin(self):
        src = dedent("""
            sin(20)
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    # 2018

    def test_node_has_no_lineno_attr(self):
        from rpn_exceptions import source_code_line_info

        # should probably mock this instead
        class Token:
            def __init__(self):
                self.line = 'hi there   '
        class Node:
            def __init__(self):
                self.first_token = Token()

        node = Node()
        s = source_code_line_info(node)
        self.assertEqual(s, 'line unknown - (missing lineno from node object):\nhi there')

    # 2021

    # def test_CLΣ(self):
    #     self.parse(dedent("""
    #         CLΣ
    #         """))
    #     expected = dedent("""
    #         CLΣ
    #         """)
    #     self.compare(de_comment(expected))    

    def test_statsclear(self):
        self.parse(dedent("""
            CLStat()
            """))
        expected = dedent("""
            CLΣ
            """)
        self.compare(de_comment(expected))    


    def test_rcl(self):
        self.parse(dedent("""
            RCL(12)
            """))
        expected = dedent("""
            RCL 12
            """)
        self.compare(de_comment(expected))
