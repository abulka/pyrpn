import unittest
import ast
import astunparse
from textwrap import dedent
from rpn import RecursiveRpnVisitor

class RpnCodeGen(unittest.TestCase):

    def parse(self, text=''):
        if not text:
            text = dedent("""
                def looper(n):
                    x = 100
                    for i in range(1, n):
                        print(i)
                        x += n
                    return x
                """)
        self.tree = ast.parse(text)
        # self.dump_ast()
        self.visitor = RecursiveRpnVisitor()
        self.visitor.visit(self.tree)
        self.visitor.program.finish()
        # self.visitor.program.dump()
        return self.visitor.program.lines

    def dump_ast(self):
        """Pretty dump AST"""
        print('-'*100)
        print(astunparse.dump(self.tree))  # nice and compact
        print('-'*100)

    def compare(self, expected, lines, trace=False):
        """
        Compares a multiline string of code with an array of rpn lines

        :param expected: string of rpn code with newlnes
        :param lines: Lines object
        :param trace: boolean, whether to print progress as we loop
        :return: -
        """
        expected = expected.strip().split('\n')
        for i, line in enumerate(lines):
            if trace:
                print(f'expected={expected[i]}, got {line.text}')
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

    @unittest.skip("offline")
    def test_complex(self):
        """
        Expected RPN is:

        00 LBL "LOOPER"  // param n
        01 100
        02 STO "X"
        00 RDN
        00 1000  // for i in range....
        00 /
        00 1
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
            100
            STO "X"
            RDN
            1000
            /
            1
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



