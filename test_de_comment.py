import unittest
from test_base import BaseTest
from de_comment import de_comment
from textwrap import dedent
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class UtilCommentTests(BaseTest):

    def test_comment_stripper(self):
        commented = dedent("""
            LBL "LOOPER"  // name of function
            1
            100
            STO "X"       // use global
            RDN           // do we need a RDN here?
            1000
            /
            +
            STO 00        // i, the looping variable
            LBL 00
            VIEW 00
            RCL 00
            IP            // integer part
            STO+ "X"
            ISG 00
            GTO 00
            RCL "X"
            RTN           // returns the global, X
            """)
        expected = dedent("""
            LBL "LOOPER"
            1
            100
            STO "X"
            RDN
            1000
            /
            +
            STO 00
            LBL 00
            VIEW 00
            RCL 00
            IP
            STO+ "X"
            ISG 00
            GTO 00
            RCL "X"
            RTN
            """)
        self.assertEqual(expected, de_comment(commented))

    def test_entire_line_is_comment(self):
        commented = dedent("""
            LBL "LOOPER"
            // 1
            // 100
            RTN
            """)
        expected = dedent("""
            LBL "LOOPER"
            RTN
            """)
        self.assertEqual(expected, de_comment(commented))

    def test_remove_blank_lines(self):
        commented = dedent("""
            LBL "LOOPER"

            RTN
            """)
        expected = dedent("""
            LBL "LOOPER"
            RTN
            """)
        self.assertEqual(expected, de_comment(commented))

