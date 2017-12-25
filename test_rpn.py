import unittest
from test_base import BaseTest
import ast
import astunparse
from textwrap import dedent
from rpn import RecursiveRpnVisitor
import logging
from logger import config_log
import maya

log = logging.getLogger(__name__)
config_log(log)

class RpnCodeGenTests(BaseTest):

    def parse(self, text, use_scope=False):
        self.tree = ast.parse(text)
        self.dump_ast()
        self.visitor = RecursiveRpnVisitor(use_scope)
        self.visitor.visit(self.tree)
        self.visitor.program.finish()
        # self.visitor.program.dump()
        return self.visitor.program.lines

    def dump_ast(self):
        """Pretty dump AST"""
        log.debug(astunparse.dump(self.tree))  # nice and compact
        log.debug(f"{'~'*25}")

    def compare(self, expected, lines, trace=False, dump=False):
        """
        Compares a multiline string of code with an array of rpn lines

        :param expected: string of rpn code with newlnes
        :param lines: Lines object
        :param trace: boolean, whether to print progress as we loop
        :return: -
        """
        if dump:
            self.visitor.program.dump()

        expected = expected.strip().split('\n')
        for i, line in enumerate(lines):
            if trace:
                log.info(f'expected={expected[i]}, got {line.text}')
            self.assertEqual(expected[i], line.text)

    # TESTS

    def test_def_empty(self):
        lines = self.parse(dedent("""
            def simple():
                pass
            """))
        self.assertEqual(lines[0].text, 'LBL "SIMPLE"')
        self.assertEqual(lines[1].text, 'RTN')

    def test_def_assignment(self):
        lines = self.parse(dedent("""
            def simple():
                x = 100
            """))
        expected = dedent("""
            LBL "SIMPLE"
            100
            STO "X"
            RDN
            RTN
            """)
        self.compare(expected, lines)

    def test_def_assignment_00(self):
        lines = self.parse(dedent("""
            def simple():
                x = 100
            """), use_scope=True)
        expected = dedent("""
            LBL "SIMPLE"
            100
            STO 00
            RDN
            RTN
            """)
        self.compare(expected, lines)

    def test_def_two_assignments(self):
        lines = self.parse(dedent("""
            def simple():
                x = 100
                y = 200
            """))
        expected = dedent("""
            LBL "SIMPLE"
            100
            STO "X"
            RDN
            200
            STO "Y"
            RDN
            RTN
            """)
        self.compare(expected, lines, trace=False, dump=False)

    def test_def_range(self):
        lines = self.parse(dedent("""
            def simple():
                for i in range(1, 200):
                    pass
            """))
        expected = dedent("""
            LBL "SIMPLE"
            1
            200
            1000
            /
            +
            STO 00
            LBL 00
            ISG 00
            GTO 00
            RTN
            """)
        self.compare(expected, lines, trace=False, dump=False)

    def test_def_range_with_body_assign(self):
        lines = self.parse(dedent("""
            def simple():
                for i in range(5, 60):
                    x = 10
            """))
        expected = dedent("""
            LBL "SIMPLE"
            5
            60
            1000
            /
            +
            STO 00
            LBL 00
            10
            STO "X"
            RDN
            ISG 00
            GTO 00
            RTN
            """)
        self.compare(expected, lines, trace=True, dump=True)

    def test_def_range_with_body_incr_i(self):
        lines = self.parse(dedent("""
            def simple():
                x = 0
                for i in range(2, 4):
                    x += i
                return x
            """))
        expected = dedent("""
            LBL "SIMPLE"
            0
            STO "X"
            RDN
            2
            4
            1000
            /
            +
            STO 00
            LBL 00
            RCL 00
            STO+ "X"
            RDN
            ISG 00
            GTO 00
            RCL "X"
            RTN
            """)
        self.compare(expected, lines, trace=True, dump=True)

    @unittest.skip("offline")
    def test_complex(self):
        """
        Expected RPN is:

        00 LBL "LOOPER"  // param n
        00 1
        01 100
        02 STO "X"
        00 RDN
        00 1000  // for i in range....
        00 /
        00 +
        00 STO 00  // counter
        00 LBL 00
        00 VIEW 00  // print(i)
        00 RCL 00  // x += n
        00 IP  // integer part
        00 STO+ "X"
        00 ISG 00
        00 GTO 00
        00 RCL "X"
        00 RTN

        """
        lines = self.parse(dedent("""
            def looper(n):
                x = 100
                for i in range(1, n):
                    print(i)
                    x += n
                return x
            """))
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
        self.compare(expected, lines)



