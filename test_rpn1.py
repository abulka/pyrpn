import unittest
import ast
import astunparse
import astpretty
from textwrap import dedent
from rpn1 import RecursiveRpnVisitor, Line

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

    def dump_ast(self):
        """Pretty dump AST"""
        # print('-'*100)
        # print(ast.dump(self.tree))  # very compact - all on one line
        # print('-'*100)
        # print(astpretty.pformat(self.tree)) # quite spaced out and verbose
        print('-'*100)
        print(astunparse.dump(self.tree))  # nice
        print('-'*100)

    def test_def(self):
        self.parse()
        self.visitor.visit(self.tree)
        print('='*100)
        self.visitor.program.dump()
        # self.assertEqual(out[0].text, 'LBL "FRED"')
        # self.assertIn('unittest.TestCase <|- AccessParsing', plant_uml_text)
