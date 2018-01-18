import unittest
from test_base import BaseTest
from de_comment import de_comment
from textwrap import dedent
import logging
from logger import config_log
from rpn import RpnError
from rpn_templates import ISG_PREPARE
from parse import parse

log = logging.getLogger(__name__)
config_log(log)

class RpnTests2(BaseTest):

    def parse(self, text):
        self.program = parse(text, debug_options={'dump_ast': True})
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
            XEQ "LGICNM"  // tobool
            AND
            X≠O?  // true?
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
            XEQ "LGICNM"  // tobool
            AND
            X≠O?  // true?
            
            GTO 00  // true
            GTO 01  // jump to resume
            
            LBL 00  // true
            CF 05
            
            LBL 01  // resume (code block after the if)
            """)
        self.compare(de_comment(expected))

    @unittest.skip('if needs revamp')
    def test_or(self):
        self.parse(dedent("""
            1 or 0 or 1
            """))
        expected = dedent("""
            1
            0
            OR
            1
            OR
            """)
        self.compare(de_comment(expected))

    @unittest.skip('if needs revamp')
    def test_and(self):
        self.parse(dedent("""
            a = 1
            b = 0
            a and b
            """))
        expected = dedent("""
            1
            STO 00
            0
            STO 01
            RCL 00
            RCL 01
            AND
            """)
        self.compare(de_comment(expected))

    @unittest.skip('if needs revamp')
    def test_if_or(self):
        self.parse(dedent("""
            if 1 or 0:
                a = 88
            """))
        expected = dedent("""
            1
            0
            OR
            X<>0?  // if (anything non zero is True)
            GTO 00
            GTO 01
            LBL 00 // true
            88
            STO 00
            LBL 01 // resume
            """)
        self.compare(de_comment(expected))
