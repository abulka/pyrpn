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
            XEQ "Py2Bool"
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
            XEQ "Py2Bool"
            AND
            1
            XEQ "Py2Bool"
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
            XEQ "Py2Bool"
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
            XEQ "PyGT"
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
            XEQ "PyLT"
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
            XEQ "PyGTE"
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
            XEQ "PyLTE"
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
            XEQ "PyEQ"
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
            XEQ "PyNEQ"
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
            XEQ "PyGT"
            XEQ "PyBool"
            XEQ "PyNot"
            """)
        self.compare(de_comment(expected))

    def test_not_and_or_t_f(self):
        self.parse(dedent("""
            not (5 > 6) and (True or False)
            """))
        expected = dedent("""
            5
            6
            XEQ "PyGT"
            XEQ "PyBool"
            XEQ "PyNot"
            1              // True
            0              // False
            XEQ "Py2Bool"  // redundant
            OR
            XEQ "Py2Bool"  // redundant
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
            XEQ "PyEQ"
            STO 01      // b
            RCL 00
            RCL 01
            XEQ "Py2Bool"
            AND
            """)
        self.compare(de_comment(expected))

    def test_unsupported_OR(self):
        src = dedent("""
            OR
            """)
        self.assertRaises(RpnError, self.parse, dedent(src))
