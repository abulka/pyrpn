import unittest
import ast
import astunparse
import astpretty
from textwrap import dedent
from rpn1 import RecursiveRpnVisitor, Line

class RpnCodeGen(unittest.TestCase):

    # def setUp(self):
    #     self.visitor = None
    #
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

    def dump_ast(self):
        """Pretty dump AST"""
        # print('-'*100)
        # print(ast.dump(self.tree))  # very compact - all on one line
        # print('-'*100)
        # print(astpretty.pformat(self.tree)) # quite spaced out and verbose
        print('-'*100)
        print(astunparse.dump(self.tree))  # nice
        print('-'*100)

    def test_def_empty(self):
        text = dedent("""
            def simple():
                pass
            """)
        self.parse(text)
        print('='*100)
        self.visitor.program.dump()
        lines = self.visitor.program.lines
        self.assertEqual(lines[0].text, 'LBL "SIMPLE"')
        self.assertEqual(lines[1].text, 'RTN')

    # @unittest.skip("offline")
    def test_def(self):
        self.parse()
        print('='*100)
        self.visitor.program.dump()
        # self.assertEqual(out[0].text, 'LBL "FRED"')
        # self.assertIn('unittest.TestCase <|- AccessParsing', plant_uml_text)

    def test_attrs(self):
        from rpn1 import Program
        a = Program()
        a.add_generic('FRED')
        # b = Program(lines=[])
        b = Program()
        print(a)
        print(b)
        self.assertEqual(1, len(a.lines))
        self.assertEqual(0, len(b.lines))
