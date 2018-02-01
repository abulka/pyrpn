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
            a = []
            """))
        expected = dedent("""
            0              // not a matrix (empty)
            SF 01          // 1D mode
            XEQ "pMxPrep"  // prepare ZLIST
            0
            STO "a"
            """)
        self.compare(de_comment(expected))

    def test_list_basic_two(self):
        self.parse(dedent("""
            aa = [1,2]
            """))
        expected = dedent("""
            0              // not a matrix (empty)
            SF 01          // 1D mode
            XEQ "pMxPrep"  // prepare ZLIST
            1
            XEQ "LIST+"
            2
            XEQ "LIST+"
            RCL "ZLIST"
            STO "aa"
            """)
        self.compare(de_comment(expected))

    def test_list_basic_two_vars(self):
        self.parse(dedent("""
            a = []
            B = []
            VIEW(a)
            """))
        expected = dedent("""
            0              // not a matrix (empty)
            SF 01          // 1D mode
            XEQ "pMxPrep"  // prepare ZLIST
            0
            STO "a"

            0              // not a matrix (empty)
            SF 01          // 1D mode
            XEQ "pMxPrep"  // prepare ZLIST
            0
            STO "B"

            VIEW "a"
            """)
        self.compare(de_comment(expected))

    def test_list_basic_append(self):
        self.parse(dedent("""
            A = []
            A.append(5)
            """))
        expected = dedent("""
            0              // not a matrix (empty)
            SF 01          // 1D mode
            XEQ "pMxPrep"  // prepare ZLIST
            0
            STO "A"

            RCL "A"
            SF 01          // 1D mode
            XEQ "pMxPrep"  // prepare ZLIST
            5
            XEQ "LIST+"

            RCL "ZLIST"
            STO "A"
            """)
        self.compare(de_comment(expected))

    def test_list_append_to_existing(self):
        self.parse(dedent("""
            a = [200]
            a.append(5)
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            200
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"
            RCL "a"
            SF 01
            XEQ "pMxPrep"
            5
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"
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
            SF 01
            XEQ "pMxPrep"
            0
            STO "A"
            -1.009
            STO 00
            LBL 00
            ISG 00
            GTO 01
            GTO 02
            LBL 01
            RCL "A"
            SF 01
            XEQ "pMxPrep"
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

    def test_list_access_el(self):
        self.parse(dedent("""
            A = [200]
            x = A[0]
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            200
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            
            RCL "A"
            SF 01
            XEQ "pMxPrep"
            
            0
            XEQ "p1MxIJ"  // set IJ to index 0 (which is ZLIST row 1)            
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
            SF 01
            XEQ "pMxPrep"
            200
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"

            300
               
            RCL "A"
            SF 01
            XEQ "pMxPrep"
            0
            XEQ "p1MxIJ"
            STOEL

            RCL "ZLIST"
            STO "A"
            """)
        self.compare(de_comment(expected))


    def test_list_strings(self):
        self.parse(dedent("""
          A = ["hi", "there"]
          A[0] = "hello"
          """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            
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
            SF 01
            XEQ "pMxPrep"
            
            0
            XEQ "p1MxIJ"
            STOEL
            
            RCL "ZLIST"
            STO "A"            
            """)
        self.compare(de_comment(expected))


    def test_list_aview_element(self):
        self.parse(dedent("""
            A = ["hi"]
            AVIEW(A[0])
          """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"

            "hi"
            ASTO ST X
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"

            CLA
            RCL "A"
            SF 01
            XEQ "pMxPrep"
            
            0
            XEQ "p1MxIJ"
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

    def test_neg_expr_inside_param(self):
        self.parse(dedent("""
            fred(-y + 1)
          """))
        expected = dedent("""
            RCL 00
            CHS
            1
            +
            XEQ A
            """)
        self.compare(de_comment(expected))

    # boolean expessions inside expressions inside parameters

    def test_bool_inside_param(self):
        self.parse(dedent("""
            print(x < y)
          """))
        expected = dedent("""
            CLA
            RCL 00
            RCL 01
            XEQ "pLT"
            ARCL ST X
            AVIEW
            """)
        self.compare(de_comment(expected))


    # dictionaries

    def test_dict_basic_empty(self):
        self.parse(dedent("""
            A = {}
          """))
        expected = dedent("""
            0             // not a matrix (empty)
            CF 01
            XEQ "pMxPrep" // prepare ZLIST
            0
            STO "A"
            """)
        self.compare(de_comment(expected))

    def test_dict_basic_one(self):
        self.parse(dedent("""
            A = {1: 2}
            """))
        expected = dedent("""
            0
            CF 01
            XEQ "pMxPrep"
            2            // value
            1            // key
            XEQ "LIST+"
            RCL "ZLIST"
            STO "A"
            """)
        self.compare(de_comment(expected))

    def test_dict_basic_two(self):
        self.parse(dedent("""
            A = {'a': 2, 'b':3}
            """))
        expected = dedent("""
            0
            CF 01
            XEQ "pMxPrep"
            
            2           // value
            "a"         // key
            ASTO ST X
            XEQ "LIST+"
            
            3           // value
            "b"         // key
            ASTO ST X
            XEQ "LIST+"
            
            RCL "ZLIST"
            STO "A"
            """)
        self.compare(de_comment(expected))

    def test_dict_set_key(self):
        self.parse(dedent("""
            A = {}
            A['a'] = 2
            """))
        expected = dedent("""
            0
            CF 01
            XEQ "pMxPrep"
            0
            STO "A"
            
            2
            
            RCL "A"
            CF 01
            XEQ "pMxPrep"
            
            "a"         // search for this key
            SF 02       // auto create if necessary
            XEQ "p2MxIJ"
            
            STOEL
            
            RCL "ZLIST"
            STO "A"
            """)
        self.compare(de_comment(expected))

    def test_dict_access_el(self):
        self.parse(dedent("""
            A = {1: 2}
            x = A[1]
            """))
        expected = dedent("""
            0
            CF 01
            XEQ "pMxPrep"
            
            2
            1
            XEQ "LIST+"
            
            RCL "ZLIST"
            STO "A"
            
            RCL "A"
            CF 01
            XEQ "pMxPrep"
            
            1             // search for this key  
            CF 02         // auto create if necessary  
            XEQ "p2MxIJ" // IJ is set nicely for us...

            RCLEL         // access A[1]
            STO 00        // x = 
            """)
        self.compare(de_comment(expected))

    # list and dict variable type enforcement

    def test_list_var_causes_remapping_to_named_register(self):
        self.parse(dedent("""
            a = 1       # mapping will occur to numeric register
            a = []      # upgrade mapping to named register to accomodate matrix usage
            a = 2       # mapping is now to the named register "a"
            """))
        expected = dedent("""
            1
            STO 00
            
            0
            SF 01
            XEQ "pMxPrep"
            0
            STO "a"

            2
            STO "a"
            """)
        self.compare(de_comment(expected))

    def test_list_append_var_must_be_named_register(self):
        src = """
            a = 1       # mapping will occur to numeric register
            a.append(5) # error, array needs named register
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_dict_var_causes_remapping_to_named_register(self):
        self.parse(dedent("""
            a = 1       # mapping will occur to numeric register
            a = {}      # mapping upgraded to named register
            a = 2       # mapping is now to the named register "a"
            """))
        expected = dedent("""
            1
            STO 00
            
            0
            CF 01
            XEQ "pMxPrep"
            0
            STO "a"

            2
            STO "a"
            """)
        self.compare(de_comment(expected))

    def test_dict_set_must_be_named_register(self):
        src = """
            a = 1       # mapping will occur to numeric register
            a['a'] = 5
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_dict_access_before_assign(self):
        src = """
            b = a[3]    # hmmm - never created a as a matrix or as any type before - error
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    # List and Dict len

    def test_list_len(self):
        self.parse(dedent("""
            a = [1, 2]
            x = len(a)
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            2
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"
            
            RCL "a"
            SF 01
            XEQ "pMxPrep"
            XEQ "pMxLen"  // Get matrix row length. () -> length of ZLIST
            STO 00
            """)
        self.compare(de_comment(expected))

    def test_dict_len(self):
        self.parse(dedent("""
            A = {'a': 2, 'b':3}
            x = len(A)
            """))
        expected = dedent("""
            0
            CF 01
            XEQ "pMxPrep"
            
            2           // value
            "a"         // key
            ASTO ST X
            XEQ "LIST+"

            3           // value
            "b"         // key
            ASTO ST X
            XEQ "LIST+"

            RCL "ZLIST"
            STO "A"

            RCL "A"
            CF 01
            XEQ "pMxPrep"
            XEQ "pMxLen"  // Get matrix row length. () -> length of ZLIST
            STO 00
            """)
        self.compare(de_comment(expected))

    def test_list_len_print(self):
        self.parse(dedent("""
            A = []
            print(len(A))
            """))
        expected = dedent("""
            0              // not a matrix (empty)
            SF 01          // 1D mode
            XEQ "pMxPrep"  // prepare ZLIST
            0
            STO "A"

            CLA
            
            RCL "A"
            SF 01
            XEQ "pMxPrep"
            XEQ "pMxLen"  // Get matrix row length. () -> length of ZLIST
            
            ARCL ST X
            AVIEW
            """)
        self.compare(de_comment(expected))

    # more advanced list operations

    def test_list_pop(self):
        self.parse(dedent("""
            a = [1]
            a.pop()
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"

            RCL "a"
            SF 01
            XEQ "pMxPrep"
            XEQ "LIST-"

            RCL "ZLIST"
            STO "a"
            """)
        self.compare(de_comment(expected))

    def test_list_del(self):
        src = """
            a = [1]
            del a[1]  # del not supported
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_list_slicing(self):
        src = """
            a = [1,2,3]
            a[0:1]  # slicing not supported
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_list_minus_one_indexing(self):
        self.parse(dedent("""
            a = [1]
            a[-1]
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"

            RCL "a"
            SF 01
            XEQ "pMxPrep"
            -1
            XEQ "p1MxIJ"  // set IJ, takes python 0 based index convention, converts to IJ 1 based, now handles negative indices            
            RCLEL
            """)
        self.compare(de_comment(expected))

    def test_list_minus_one_indexing_assign(self):
        self.parse(dedent("""
            a = [1]
            a[-1] = 99
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"

            99
            
            RCL "a"
            SF 01
            XEQ "pMxPrep"
            -1
            XEQ "p1MxIJ"  // set IJ, takes python 0 based index convention, converts to IJ 1 based, now handles negative indices            
            STOEL
            
            RCL "ZLIST"
            STO "a"            
            """)
        self.compare(de_comment(expected))

    def test_list_assign_between_vars(self):
        self.parse(dedent("""
            a = [1]
            b = a
            b[0]
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"

            RCL "a"
            SF 01           // not needed but hard to repress
            XEQ "pMxPrep"   // not needed but hard to repress
            RCL "ZLIST"     // forced to generate this in order to get the RCL "a" back onto the stack, due to pMxPrep eating it up  
            STO "b"
            
            RCL "b"
            SF 01
            XEQ "pMxPrep"
            0
            XEQ "p1MxIJ"  // set IJ to index 0 (which is ZLIST row 1)            
            RCLEL
            """)
        self.compare(de_comment(expected))

    def test_list_print(self):
        self.parse(dedent("""
            a = [1, 2]
            print(a)
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            2
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"

            CLA
            ARCL "a"    // in future loop and print the elements? 
            AVIEW
            """)
        self.compare(de_comment(expected))

    def test_list_for_in_var(self):
        self.parse(dedent("""
            a = [1, 2]
            for el in a:
                VIEW(el)
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            2
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"

            // for loop
            
            // setup
            0       // from
            RCL "a" // to
            SF 01
            XEQ "pMxPrep"
            XEQ "pMxLen"  
            1       // step
            XEQ "pISG"
            STO 00  // range i
                        
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            
            RCL 00  // get the index 
            IP
            RCL "a" // its an el index so prepare associated list for access
            SF 01
            XEQ "pMxPrep"
            XEQ "p1MxIJ"
            RCLEL   // get el
            VIEW ST X
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected))

    @unittest.skip('alpha variation complexities - test is written OK')
    def test_list_for_in_var_prompt(self):
        self.parse(dedent("""
            a = [1, 2]
            for el in a:
                PROMPT(el)
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            2
            XEQ "LIST+"
            RCL "ZLIST"
            STO "a"

            // for loop
            
            // setup
            0       // from
            RCL "a" // to
            SF 01
            XEQ "pMxPrep"
            XEQ "pMxLen"  
            1       // step
            XEQ "pISG"
            STO 00  // range i
                        
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            
            CLA
            RCL 00  // get the index 
            IP
            RCL "a" // its an el index so prepare associated list for access
            SF 01
            XEQ "pMxPrep"
            XEQ "p1MxIJ"
            RCLEL   // get el
            ARCL ST X
            PROMPT
            
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected))

    @unittest.skip('so hard - need temp var for list itself')
    def test_list_for_in_literal_list(self):
        self.parse(dedent("""
            for el in [1, 2]:
                pass
            """))
        expected = dedent("""
            0
            SF 01
            XEQ "pMxPrep"
            1
            XEQ "LIST+"
            2
            XEQ "LIST+"
            //RCL "ZLIST"
            //STO "temp_list"

            // for loop
            
            // setup
            0       // from
            2       // to
            1       // step
            XEQ "pISG"
            STO 00  // range i
                        
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected))


    # assert

    def test_assert(self):
        self.parse(dedent("""
            passert(2 == 2)
            """))
        expected = dedent("""
            2
            2
            XEQ "pEQ"
            XEQ "pAssert"
            """)
        self.compare(de_comment(expected))

    def get_all_lib(self):
        from program import Program
        program = Program()
        program.rpn_templates.need_all_templates()
        program.emit_needed_rpn_templates(as_local_labels=False)
        rpn = program.lines_to_str(comments=False, linenos=False)
        return rpn
