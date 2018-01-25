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

class RpnTests2(BaseTest):

    def parse(self, text):
        self.program = parse(text, debug_options={'dump_ast': True, 'emit_pyrpn_lib': False})
        self.program.dump()

    def compare(self, expected, keep_comments=False):
        self.assertEqual(expected.strip(), self.program.lines_to_str(comments=keep_comments).strip())

    # TESTS

    def test_and_two_param(self):
        self.parse(dedent("""
            1 and 0
            """))
        expected = dedent("""
            1
            0
            XEQ "p2Bool"
            AND
            """)
        self.compare(de_comment(expected))

    def test_and_or_two_param(self):
        self.parse(dedent("""
            1 and 0 or 1
            """))
        expected = dedent("""
            1
            0
            XEQ "p2Bool"
            AND
            1
            XEQ "p2Bool"
            OR
            """)
        self.compare(de_comment(expected))

    def test_and_two_param_if(self):
        self.parse(dedent("""
            if 1 and 0:
                CF(5)
            """))
        expected = dedent("""
            1
            0
            XEQ "p2Bool"
            AND

            X≠0?    // if true?
            GTO 00  // true
            GTO 01  // jump to resume
            
            LBL 00  // true
            CF 05
            
            LBL 01  // resume (code block after the if)
            """)
        self.compare(de_comment(expected))

    # Comparison operators

    def test_compare_GT(self):
        src = """
            2 > 1
        """
        expected = dedent("""
            2
            1
            XEQ "pGT"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_compare_LT(self):
        src = """
            2 < 1
        """
        expected = dedent("""
            2
            1
            XEQ "pLT"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_compare_GTE(self):
        src = """
            2 >= 1
        """
        expected = dedent("""
            2
            1
            XEQ "pGTE"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_compare_LTE(self):
        src = """
            2 <= 1
        """
        expected = dedent("""
            2
            1
            XEQ "pLTE"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_compare_EQ(self):
        src = """
            2 == 1
        """
        expected = dedent("""
            2
            1
            XEQ "pEQ"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_compare_NEQ(self):
        src = """
            2 != 1
        """
        expected = dedent("""
            2
            1
            XEQ "pNEQ"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    # not logic, incl true and false

    def test_not(self):
        self.parse(dedent("""
            not (1 > 0)
            """))
        expected = dedent("""
            1
            0
            XEQ "pGT"
            XEQ "pBool"
            XEQ "pNot"
            """)
        self.compare(de_comment(expected))

    def test_not_and_or_t_f(self):
        self.parse(dedent("""
            not (5 > 6) and (True or False)
            """))
        expected = dedent("""
            5
            6
            XEQ "pGT"
            XEQ "pBool"
            XEQ "pNot"
            1              // True
            0              // False
            XEQ "p2Bool"  // redundant
            OR
            XEQ "p2Bool"  // redundant
            AND
            """)
        self.compare(de_comment(expected))

    # more....

    def test_and_true_vars(self):
        self.parse(dedent("""
            a = True
            b = 2 == 3
            a and b
            """))
        expected = dedent("""
            1           // True
            STO 00      // a
            2
            3
            XEQ "pEQ"
            STO 01      // b
            RCL 00
            RCL 01
            XEQ "p2Bool"
            AND
            """)
        self.compare(de_comment(expected))

    def test_unsupported_OR(self):
        src = dedent("""
            OR
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))

    # Lists - using LIST util rpn

    def test_list_basic_empty(self):
        self.parse(dedent("""
            A = []
            """))
        expected = dedent("""
            0             // not a matrix (empty)
            XEQ "p1DMtx"  // prepare ZLIST
            STO "A"
            """)
        self.compare(de_comment(expected))

    def test_list_basic_two(self):
        self.parse(dedent("""
            A = [1,2]
            """))
        expected = dedent("""
            0             // not a matrix (empty)
            XEQ "p1DMtx"  // prepare ZLIST
            1
            XEQ "LIST+"
            2
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            """)
        self.compare(de_comment(expected))

    def test_list_basic_two_vars(self):
        self.parse(dedent("""
            A = []
            B = []
            VIEW(A)
            """))
        expected = dedent("""
            0             // not a matrix (empty)
            XEQ "p1DMtx"  // prepare ZLIST
            STO "A"

            0             // not a matrix (empty)
            XEQ "p1DMtx"  // prepare ZLIST
            STO "B"

            VIEW "A"
            """)
        self.compare(de_comment(expected))

    def test_list_basic_append(self):
        self.parse(dedent("""
            A = []
            A.append(5)
            """))
        expected = dedent("""
            0             // not a matrix (empty)
            XEQ "p1DMtx"  // prepare ZLIST
            STO "A"

            RCL "A"
            XEQ "p1DMtx"  // prepare ZLIST
            5
            XEQ "LIST+"

            RCL "ZLIST"
            STO "A"
            """)
        self.compare(de_comment(expected))

    def test_list_append_to_existing(self):
        self.parse(dedent("""
            A = [200]
            A.append(5)
            """))
        expected = dedent("""
            0
            XEQ "p1DMtx"
            200
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            RCL "A"
            XEQ "p1DMtx"
            5
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            """)
        self.compare(de_comment(expected))


    def test_list_append_i_in_loop(self):
        self.parse(dedent("""
            def a10():
              A = []
              for i in range(10):
                A.append(i)
            """))
        expected = dedent("""
            LBL "a10"
            0
            XEQ "p1DMtx"
            STO "A"
            -1.009
            STO 00
            LBL 00
            ISG 00
            GTO 01
            GTO 02
            LBL 01
            RCL "A"
            XEQ "p1DMtx"
            RCL 00
            IP
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            GTO 00
            LBL 02
            RTN
            """)
        self.compare(de_comment(expected))

    def test_list_var_must_be_uppercase(self):
        src = """
            a = []
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_list_append_var_must_be_uppercase(self):
        src = """
            a.append(5)
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_list_access_el(self):
        self.parse(dedent("""
            A = [200]
            x = A[0]
            """))
        expected = dedent("""
            0
            XEQ "p1DMtx"
            200
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            
            RCL "A"
            XEQ "p1DMtx"
            INDEX "ZLIST"
            0
            1
            +
            1
            STOIJ
            RCLEL
            
            STO 00
            """)
        self.compare(de_comment(expected))

    def test_list_access_el_store(self):
        self.parse(dedent("""
            A = [200]
            A[0] = 300
            """))
        expected = dedent("""
            0
            XEQ "p1DMtx"
            200
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"

            300
                        
            RCL "A"
            XEQ "p1DMtx"
            INDEX "ZLIST"
            0
            1
            +
            1
            STOIJ
            RCL ST T
            STOEL
            """)
        self.compare(de_comment(expected))


    def test_list_strings(self):
        self.parse(dedent("""
          A = ["hi", "there"]
          A[0] = "hello"
          """))
        expected = dedent("""
            0
            XEQ "p1DMtx"
            "hi"
            ASTO ST X
            XEQ "LIST+"
            "there"
            ASTO ST X
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            "hello"
            ASTO ST X
            RCL "A"
            XEQ "p1DMtx"
            INDEX "ZLIST"
            0
            1
            +
            1
            STOIJ
            RCL ST T
            STOEL
            """)
        self.compare(de_comment(expected))


    def test_list_aview_element(self):
        self.parse(dedent("""
            A = ["hi"]
            AVIEW(A[0])
          """))
        expected = dedent("""
            0
            XEQ "p1DMtx"
            "hi"
            ASTO ST X
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            CLA
            RCL "A"
            XEQ "p1DMtx"
            INDEX "ZLIST"
            0
            1
            +
            1
            STOIJ
            RCLEL
            ARCL ST X
            AVIEW
            """)
        self.compare(de_comment(expected))

    # Parameters forced to be INT

    def test_params_force_int(self):
        self.parse(dedent("""
            def f(a, b):  # rpn: int
                pass
          """))
        expected = dedent("""
            LBL "f"
            XEQ "p2Param"   // reorder 2 params for storage
            IP
            STO 00          // param: a
            RDN
            IP
            STO 01          // param: b
            RDN
            RTN
            """)
        self.compare(de_comment(expected))

    # Parameter reversal for some commands

    def test_params_pixel_swap(self):
        """
        Intuitive order for calling a user defined function is a,b,c which results in z:a y:b x:c which is
        wrong way around for def parsing where parameters are stored in register in order of the param declaration.
        So RPN code is inserted to reverse the parameter order at the beginning of all user defined functions.

        However a built in function like PIXEL takes y: row (y axis), x: col (x axis) which is not intuitive,
        cos when you enter coordinate its x,y which means PIXEL should arguably take Y:x X:y - but would have
        been weird cos of the coincidence re the names being around the wrong way, so probably HP switched it.
        But for algebraic notation use, it should be the other way around, so I correct this.
        :return:
        """
        self.parse(dedent("""
            PIXEL(100, 1)
          """))
        expected = dedent("""
            100
            1
            X<>Y
            PIXEL
            """)
        self.compare(de_comment(expected))

    # += and -= expressions

    def test_y_plus_eq_one(self):
        self.parse(dedent("""
            y += 1
          """))
        expected = dedent("""
            1
            STO+ 00
            """)
        self.compare(de_comment(expected))

    def test_y_minus_eq_one(self):
        self.parse(dedent("""
            y -= 1
          """))
        expected = dedent("""
            1
            STO- 00
            """)
        self.compare(de_comment(expected))

    def test_y_minus_eq_neg_one(self):
        self.parse(dedent("""
            y -= -1
          """))
        expected = dedent("""
            -1
            STO- 00
            """)
        self.compare(de_comment(expected))

    # negatives inside expressions inside parameters

    def test_neg_inside_param(self):
        self.parse(dedent("""
            fred(-y)
          """))
        expected = dedent("""
            RCL 00
            CHS
            XEQ A
            """)
        self.compare(de_comment(expected))

    @unittest.skip('hard')
    def test_neg_expr_inside_param(self):
        self.parse(dedent("""
            fred(-y + 1)
          """))
        expected = dedent("""
            RCL 00
            CHS
            1
            +
            XEQ "A"
            """)
        self.compare(de_comment(expected))

    # boolean expessions inside expressions inside parameters

    @unittest.skip('hard')
    def test_bool_inside_param(self):
        self.parse(dedent("""
            print(x < y)
          """))
        expected = dedent("""
            RCL 00
            RCL 01
            XEQ "pLT"
            CLA
            ARCL ST X
            AVIEW
            """)
        self.compare(de_comment(expected))

