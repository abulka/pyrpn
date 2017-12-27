import unittest
from test_base import BaseTest
from de_comment import de_comment
import ast
import astunparse
from textwrap import dedent
from rpn import RecursiveRpnVisitor
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class RpnCodeGenTests(BaseTest):

    def parse(self, text):
        self.tree = ast.parse(text)
        self.dump_ast()
        self.visitor = RecursiveRpnVisitor()
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
        Compares a multi-line string of code with an array of rpn lines

        :param expected: string of rpn code with newlnes
        :param lines: Lines object
        :param trace: boolean, whether to print progress as we loop
        :return: -
        """
        if dump:
            self.visitor.program.dump(comments=True)

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
        self.assertEqual(lines[0].text, 'LBL "simple"')
        self.assertEqual(lines[1].text, 'RTN')

    def test_def_assignment_global(self):
        lines = self.parse(dedent("""
            def simple():
                X = 100
            """))
        expected = dedent("""
            LBL "simple"
            100
            STO "X"
            RTN
            """)
        self.compare(expected, lines)

    def test_def_assignment_scoped(self):
        lines = self.parse(dedent("""
            def SIMPLE():
                x = 100
            """))
        expected = dedent("""
            LBL "SIMPLE"
            100
            STO 00
            RTN
            """)
        self.compare(expected, lines)

    def test_def_two_assignments_global(self):
        lines = self.parse(dedent("""
            def simple():
                X = 100
                Y = 200
            """))
        expected = dedent("""
            LBL "simple"
            100
            STO "X"
            200
            STO "Y"
            RTN
            """)
        self.compare(expected, lines, trace=False, dump=False)

    def test_def_two_assignments_scoped(self):
        lines = self.parse(dedent("""
            def simple():
                x = 100
                y = 200
            """))
        expected = dedent("""
            LBL "simple"
            100
            STO 00
            200
            STO 01
            RTN
            """)
        self.compare(expected, lines, trace=False, dump=False)

    def test_def_two_assignments_mixed(self):
        lines = self.parse(dedent("""
            def simple():
                X = 100
                y = 200
            """))
        expected = dedent("""
            LBL "simple"
            100
            STO "X"
            200
            STO 00
            RTN
            """)
        self.compare(expected, lines, trace=False, dump=False)

    def test_def_range(self):
        lines = self.parse(dedent("""
            def for_loop():
                for i in range(1, 200):
                    pass
            """))
        expected = dedent("""
            LBL "for_loo"
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
        self.compare(expected, lines, trace=False, dump=True)

    def test_def_range_with_body_assign_global(self):
        lines = self.parse(dedent("""
            def another_for_loop():
                for i in range(5, 60):
                    X = 10
            """))
        expected = dedent("""
            LBL "another"
            5
            60
            1000
            /
            +
            STO 00
            LBL 00
            10
            STO "X"
            ISG 00
            GTO 00
            RTN
            """)
        self.compare(expected, lines, trace=True, dump=True)

    def test_def_range_with_body_assign_scoped(self):
        lines = self.parse(dedent("""
            def range_with_body():
                for i in range(5, 60):
                    x = 10
            """))
        expected = dedent("""
            LBL "range_w"
            5
            60
            1000
            /
            +
            STO 00
            LBL 00
            10
            STO 01  // x
            ISG 00
            GTO 00
            RTN
            """)
        self.compare(expected, lines, trace=True, dump=True)

    def test_def_range_three_scoped_vars(self):
        lines = self.parse(dedent("""
            def three_scoped():
                x = 10
                for i in range(5, 60):
                    y = 100
            """))
        expected = dedent("""
            LBL "three_s"
            10
            STO 00
            5
            60
            1000
            /
            +
            STO 01
            LBL 00
            100
            STO 02  // y
            ISG 01
            GTO 00
            RTN
            """)
        self.compare(expected, lines, trace=True, dump=True)

    def test_def_range_with_body_accessing_i(self):
        lines = self.parse(dedent("""
            def range_i():
                X = 0
                for i in range(2, 4):
                    X += i
                return X
            """))
        expected = dedent("""
            LBL "range_i"
            0
            STO "X"
            2
            4
            1000
            /
            +
            STO 00  // i
            LBL 00
            RCL 00  // i
            STO+ "X"
            ISG 00
            GTO 00
            RCL "X"
            RTN
            """)
        self.compare(expected, lines, trace=True, dump=True)

    def test_def_range_complex(self):
        lines = self.parse(dedent("""
            def range_complex():
                X = 0
                x = 0
                total = 0
                for i in range(2, 4):
                    X = i
                    x += i
                    total += x
                return total
            """))
        # local var mappings are x:0, total:1, i:2
        expected = dedent("""
            LBL "range_c"
            0
            STO "X" // X
            0
            STO 00  // x
            0
            STO 01  // total
            2
            4
            1000
            /
            +
            STO 02  // i
            LBL 00
            RCL 02  // i
            STO "X"
            RCL 02  // i
            STO+ 00 // x
            RCL 00  // x
            STO+ 01 // total
            RDN
            ISG 02  // i
            GTO 00
            RCL 01  // total
            RTN
            """)
        self.compare(de_comment(expected), lines, trace=True, dump=True)

    @unittest.skip("offline")
    def test_complex(self):
        lines = self.parse(dedent("""
            def looper(n):
                x = 100
                for i in range(10, n):
                    print(i)
                    x += n
                return x
            """))
        expected = dedent("""
            LBL "looper"  // param n is on the stack, so that's up to the user
            100
            STO 00  // x
            1000    // stack.x gets consumed
            /
            10      // range start 
            +
            STO 01  // i our counter
            LBL 00
            VIEW 01 // print i
            RCL 01  // i
            IP
            STO+ 00 // x
            ISG 01  // i
            GTO 00
            RCL 00  // leave x on stack
            RTN
            """)
        self.compare(de_comment(expected), lines)

    # Stack param tests

    """
    So the new plan is that parameters are passed via the stack, thus a max of 4 parameters.
    And similarly, values are returned on the stack.
    
    And now the insight - we don't rely on those parameters staying in those positions - its just
    impossible to manage unless everything is hand crafted and thought about deeply.  So lets just
    store function parameters in local registers and from then on forget about the stack.
      
    The stack then just becomes a workplace to create literals and rcl values into, before operating 
    on them and storing the results back into other registers.  Though we can even avoid using most
    of the stack by using STO+ NN and RCL+ NN style operations which mean NN += x and x += NN respectively.    
    """

    def test_stack_x_as_param(self):
        lines = self.parse(dedent("""
            def func(n):
                pass
            """))
        expected = dedent("""
            LBL "func"  // param n is on the stack, so that's up to the user
            STO 00
            RDN
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_stack_x_returned(self):
        lines = self.parse(dedent("""
            def func(n):
                return n
            """))
        expected = dedent("""
            LBL "func"
            STO 00  // n
            RDN
            RCL 00  // n
            RTN
            """)
        self.compare(de_comment(expected), lines)

    def test_stack_y_returned(self):
        lines = self.parse(dedent("""
            def func(a, b):
                return b
            """))
        expected = dedent("""
            LBL "func"
            STO 00  // a
            RDN
            STO 01  // b
            RDN
            RCL 01  // b
            RTN
            """)
        self.compare(de_comment(expected), lines)

    def test_stack_x_add1(self):
        lines = self.parse(dedent("""
            def func(n):
                return n + 1
            """))
        expected = dedent("""
            LBL "func"
            STO 00
            RDN
            RCL 00
            1
            +
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_stack_x_y_add(self):
        lines = self.parse(dedent("""
            def func(a, b):
                return a + b
            """))
        expected = dedent("""
            LBL "func"
            STO 00
            RDN
            STO 01
            RDN
            RCL 00
            RCL 01
            +
            RTN
            """)
        self.compare(de_comment(expected), lines)

    def test_stack_x_y_add_plus_literal(self):
        lines = self.parse(dedent("""
            def func(a, b):
                return a + b + 10
            """))
        expected = dedent("""
            LBL "func"
            STO 00
            RDN
            STO 01
            RDN
            RCL 00
            RCL 01
            +
            10
            +
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_stack_complex1(self):
        lines = self.parse(dedent("""
            def func(a, b):
                c = 1
                return b + c + a
            """))
        expected = dedent("""
            LBL "func"
            STO 00  // a
            RDN
            STO 01  // b
            RDN
            1
            STO 02  // c
            // return
            RCL 01  // b
            RCL 02  // c
            +
            RCL 00  // a
            +
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    # @unittest.skip("offline need to figure our binop etc")
    def test_stack_complex2(self):
        lines = self.parse(dedent("""
            def func(a):
                a += 5
                c = a + 1
                return a + c + 2
            """))
        expected = dedent("""
            LBL "func"
            STO 00  // a
            RDN
            5
            STO+ 00
            RCL 00  // a
            1
            +
            STO 01  // c
            // return
            RCL 01  // c
            RCL 00  // a
            +
            2
            +
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

        # Learn about binop assignments

    def test_binop_1(self):
        lines = self.parse(dedent("""
            def func():
                a = 5 + 6 + 7 
                b = a + 8 + a
                return a + b + 9
            """))
        expected = dedent("""
            LBL "func"
            5
            6
            +
            7
            +
            STO 00  // a
            RCL 00  // a ... could be left out as an optimisation since its on stack already
            8
            +
            RCL 00 // a
            +
            STO 01 // b
            // return
            RCL 00  // a
            RCL 01  // b
            +
            9
            +
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)
