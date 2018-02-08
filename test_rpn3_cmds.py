import unittest
from test_base import BaseTest
from de_comment import de_comment
from textwrap import dedent
import logging
from logger import config_log
from rpn import RpnError
from parse import parse

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
    # INDEX, STOIJ, RCLIJ, I+, I-, J+, J-
    # and PUTM, GETM   <--- yikes, requires slicing !!
    # INSR and DELR are however, probably OK

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
            RDN
            RDN
            5              // size of sub-matrix to extract
            6
            XEQ "p2MxSub"  // (row_to, col_to) -> (row_size, col_size) - Converts from 0 based Python 'to' into 1 based size for GETM
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
                               # aha, but could use [2,5] since HP42S doesn't check or care.
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

    @unittest.skip('matrices')
    def test_matrices_insert_row(self):
        """
        Inserting and deleting rows
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            INSR(1)
            DELR(1)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"

            INDEX "x"
            1
            1
            STOIJ
            RDN
            RDN
            INSR

            INDEX "x"
            1
            1
            STOIJ
            RDN
            RDN
            DELR
            """)
        self.compare(de_comment(expected))

    # END radical

    @unittest.skip('matrices')
    def test_matrices_dim(self):
        self.parse(dedent("""
            #x = DIM(1,4)   # hmmmm
            DIM(x, 1,4)  # perhaps this is better - but not Pythonic?
            #x.dim(1,4)  # perhaps even nicer
            """))
        expected = dedent("""
            1
            4
            DIM "x"
            """)
        self.compare(de_comment(expected))

    @unittest.skip('matrices')
    def test_matrices_dim_existing(self):
        # redimension a matrix
        self.parse(dedent("""
            x = DIM(1,4)
            #x = DIM(2,5)  # hmmmmmm
            x = DIM(x, 2,5)  # perhaps this is better?
            #x.DIM(2,5)  # or this?
            """))
        expected = dedent("""
            1
            4
            DIM "x"
            2
            5
            DIM "x"
            """)
        self.compare(de_comment(expected))

    @unittest.skip('matrices')
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
            
            RCL "x"
            3.5
            *
            STO "x"
            """)
        self.compare(de_comment(expected))

    @unittest.skip('matrices')
    def test_matrices_invert(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            x = INVRT(x)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            RCL "x"
            INVRT
            STO "x"
            """)
        self.compare(de_comment(expected))

    @unittest.skip('matrices')
    def test_matrices_index(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            INDEX(x)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            INDEX "x"
            """)
        self.compare(de_comment(expected))

    @unittest.skip('matrices')
    def test_matrices_index_ij(self):
        """
        import numpy as np
        x = np.zeros((1,4)) # or np.array([[0,0,0,0]])
        y = x[0,2]
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            INDEX(x)
            STOIJ(1,2)
            y = RCLEL()
            Iplus
            Iminus
            Jplus
            Jminus
            a, b = RCLIJ()
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            
            INDEX "x"
            1
            2
            STOIJ
            RCLEL
            STO "y"
            I+
            I-
            J+
            J-
            RCLIJ
            STO 00
            X<>Y
            STO 01
            """)
        self.compare(de_comment(expected))

    @unittest.skip('matrices')
    def test_matrices_wrap_grow(self):
        self.parse(dedent("""
            x = NEWMAT(1,4)
            INDEX(x)
            INSR()
            DELR()
            WRAP()
            GROW()
            ROWswapROW(1,2)
            """))
        expected = dedent("""
            1
            4
            NEWMAT
            STO "x"
            INDEX "x"

            INSR
            DELR
            WRAP
            GROW
            
            1
            2
            R<>R
            """)
        self.compare(de_comment(expected))

    @unittest.skip('matrices')
    def test_matrices_getm_putm(self):
        """
        GETM recalls the submatrix to the X-register.
            1. Move the index pointers to the first element of the submatrix.
            2. Enter the dimensions of the submatrix: number of rows in the Y-
                register and number of columns in the X-register.
            3. Execute the GETM (get matrix) function (. 1MATRIX 1  .U l)·
                GETM recalls the submatrix to the X-register.

        PUTM copies the matrix in the X-register, element for element, into the indexed matrix beginning at the current element.
            1. Move the index pointers to the element where you want the first element of the submatrix to go.
            2. Execute the PUTM (put matrix) function (. 1MATRIX I  ). PUTM copies the matrix in the X-register,
            element for element, into the indexed matrix beginning at the current element.
        """
        self.parse(dedent("""
            x = NEWMAT(1,4)
            INDEX(x)
            STOIJ(1,3)      # step 1
            z = GETM(1,1)   # steps 2 & 3
            
            STOIJ(1,3)      # step 1
            PUTM(z)         # step 2
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
            1
            1
            GETM
            STO "z"
            
            1
            3
            STOIJ
            RCL "z"
            PUTM
            """)
        self.compare(de_comment(expected))



    # Complex numbers

    def test_complex_create(self):
        self.parse(dedent("""
            x = COMPLEX(1, 0)
            """))
        expected = dedent("""
            1
            0
            COMPLEX        
            STO 00
            """)
        self.compare(de_comment(expected))

    @unittest.skip('complex matrix')
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

    @unittest.skip('complex matrix')
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
            X<>Y
            STO "a"
            """)
        self.compare(de_comment(expected))

