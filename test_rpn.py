import unittest
from test_base import BaseTest
from de_comment import de_comment
import ast
import astunparse
from textwrap import dedent
from rpn import RecursiveRpnVisitor
import logging
from logger import config_log
import asttokens

log = logging.getLogger(__name__)
config_log(log)

class RpnCodeGenTests(BaseTest):

    def parse(self, text, debug_gen_descriptive_labels=False):
        # self.tree = ast.parse(text)

        self.atok = asttokens.ASTTokens(text, parse=True)  # this keeps source code in the AST tree
        self.tree = self.atok.tree

        self.dump_ast()
        self.visitor = RecursiveRpnVisitor()
        self.visitor.debug_gen_descriptive_labels=debug_gen_descriptive_labels
        self.visitor.atok = self.atok
        self.visitor.visit(self.tree)
        # self.visitor.program.dump()
        return self.visitor.program.lines

    def dump_ast(self):
        """Pretty dump AST"""
        log.debug(astunparse.dump(self.tree))  # nice and compact
        log.debug(f"{'~'*25}")

    def compare(self, expected, lines, trace=False, dump=False, keep_comments=False):
        """
        Compares a multi-line string of code with an array of rpn lines

        :param expected: string of rpn code with newlnes
        :param lines: Lines object
        :param trace: boolean, whether to print progress as we loop
        :param dump: boolean, whether to dump to log the lines of entire program
        :param comments: boolean, whether to compare comments too
        :return: -
        """
        if dump:
            self.visitor.program.dump(comments=True)

        # All in one comparison
        self.assertEqual(expected.strip(), self.visitor.program.lines_to_str(lines, comments=keep_comments).strip())

        if trace:
            expected = expected.strip().split('\n')
            for i, line in enumerate(lines):
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
        self.compare(de_comment(expected), lines, trace=True, dump=True)

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
        self.compare(de_comment(expected), lines, trace=True, dump=True)

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
            IP
            STO+ "X"
            ISG 00
            GTO 00
            RCL "X"
            RTN
            """)
        self.compare(de_comment(expected), lines, trace=True, dump=True)

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
            LBL 00  // for
            RCL 02  // i
            IP
            STO "X"
            RCL 02  // i
            IP
            STO+ 00 // x +=
            RCL 00  // x
            STO+ 01 // total +=
            ISG 02  // i
            GTO 00
            RCL 01  // total
            RTN
            """)
        self.compare(de_comment(expected), lines, trace=True, dump=True)

    # @unittest.skip("offline")
    def test_complex(self):
        lines = self.parse(dedent("""
            def looper(n):
                x = 100
                for i in range(10, n):
                    #print(i)
                    x += n
                    x += i
                return x
            """))
        expected = dedent("""
            LBL "looper"  // param n is on the stack, so that's up to the user
            STO 00
            RDN
            100
            STO 01    // x
            10        // range start, 10
            RCL 00    // range end, n
            1000
            /
            +
            STO 02    // i our counter
            LBL 00
            //VIEW 02 // print i  TODO 
            RCL 00    // n
            STO+ 01   // x +=
            RCL 02    // i
            IP        // when using a loop counter elsewhere, IP it first
            STO+ 01   // x +=
            ISG 02    // i
            GTO 00
            RCL 01    // leave x on stack
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True, trace=True)

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
            RCL 00  // a
            RCL 01  // c
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

    # Function calls

    def test_xeq_simple(self):
        lines = self.parse(dedent("""
            def main():
                f(1)
            """))
        expected = dedent("""
            LBL "main"
            1
            XEQ A
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_xeq_real(self):
        lines = self.parse(dedent("""
            def main():
                f(1)
                
            def f(n):
                pass
            """))
        expected = dedent("""
            LBL "main"
            1
            XEQ A
            RTN
            LBL A
            STO 00
            RDN
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_xeq_add_subroutine(self):
        lines = self.parse(dedent("""
            def main():
                add(1,2)

            def add(a,b):
                return a + b
            """))
        expected = dedent("""
            LBL "main"
            1
            2
            XEQ A
            RTN
            LBL A  // def add()
            STO 00
            RDN
            STO 01
            RDN
            RCL 00 // could be optimised not to use 01 and 02
            RCL 01
            +
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_nested_defs(self):
        """
        Nested defs are ok but they aren't really private
        and use up a label within the program, so future functions with the
        same name would refer to the same label!  Workaround is that
        if you redefine a def, no matter the scope, it gets a new label mapping.
        """
        lines = self.parse(dedent("""
            def main():
            
                def add(a,b):
                    # print('inner')
                    return a + b
                    
                add(1,2)  # will call the inner add()
            
            def add(a,b):
                pass
            """))
        expected = dedent("""
            LBL "main"
            LBL A  // inner def add()
            STO 00
            RDN
            STO 01
            RDN
            RCL 00 // could be optimised not to use 01 and 02
            RCL 01
            +
            RTN
            1
            2
            XEQ A  // will call inner add, viz A
            RTN
            LBL B  // outer def add()
            STO 00
            RDN
            STO 01
            RDN
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    # Calls to HP42s methods

    def test_mvar(self):
        lines = self.parse(dedent("""
            def mvadd():
                MVAR("length")
                MVAR("width")
                VARMENU("mvadd")
                STOP()
                EXITALL()
                return length * width 
            """))
        expected = dedent("""
            LBL "mvadd"
            MVAR "length"
            MVAR "width"
            VARMENU "mvadd"
            STOP
            EXITALL
            RCL "length"
            RCL "width"
            *
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_varmenu(self):
        """
        new construct - to save time
        """
        lines = self.parse(dedent("""
            def myvmnu():
                varmenu("length", "width")
                return length * width 
            """))
        expected = dedent("""
            LBL "myvmnu"
            MVAR "length"
            MVAR "width"
            VARMENU "myvmnu"
            STOP
            EXITALL
            RCL "length"
            RCL "width"
            *
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    # play with default scope

    def test_no_def(self):
        """
        no def - so you don't get a label - still pastable into free42
        """
        lines = self.parse(dedent("""
            val = 10
            res = val * 10
            """))
        expected = dedent("""
            10
            STO 00
            RCL 00
            10
            *
            STO 01
        """)
        self.compare(de_comment(expected), lines, dump=True)

    # generic handling of any 41S command

    def test_generic_cmds_1(self):
        """
        looks up generic list of 41S commands
        """
        lines = self.parse(dedent("""
            fred = 1
            FIX(2)
            FP()
            IP()
            GRAD()
            """))
        expected = dedent("""
            1
            STO 00
            FIX 02
            FP
            IP
            GRAD
        """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_generic_cmds_non_multi_part(self):
        """
        These commands might take parameters, but are themselves not
        multi-part commands that require a parameter on the same line.
        """
        lines = self.parse(dedent("""
            ABS(-1)
            ACOS(2)
            ACOSH(3)
            ADV()
            AGRAPH(4,5)
            """))
        expected = dedent("""
            -1
            ABS
            2
            ACOS
            3
            ACOSH
            ADV
            4
            5
            AGRAPH
        """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_multi_cmd_one_arg_frag(self):
        """
        multi-part commands that require an arg fragment "parameter" as part of the single rpn command
        """
        lines = self.parse(dedent("""
            INDEX("matrix1")
            INPUT("length")
            INTEG("somevar")
            """))
        expected = dedent("""
            INDEX "matrix1"
            INPUT "length"
            INTEG "somevar"
        """)
        self.compare(de_comment(expected), lines, dump=True)


    def test_multi_cmd_two_arg_frag(self):
        """
        multi-part commands that require two arg fragments "parameters" as part of the single rpn command
        """
        lines = self.parse(dedent("""
            KEYG(1, "doblah")
            ASSIGN("someprog", 18)
            """))
        expected = dedent("""
            KEYG 01 "doblah"
            ASSIGN "someprog" 18
        """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_if(self):
        lines = self.parse(dedent("""
            if FS(1):
                CF(1)
            FIX(2)
            """))
        expected = dedent("""
            FS? 01
            GTO 00  // true, flag is set
            GTO 01  // jump to resume
            
            LBL 00  // true
            CF 01
            
            LBL 01  // resume (code block after the if)
            FIX 02
        """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_if_else(self):
        lines = self.parse(dedent("""
            if FS(1):
                CF(5)
            else:
                CF(6)
            FIX(2)  
            """))
        expected = dedent("""
            FS? 01
            GTO 00  // true, flag is set
            GTO 02  // else (false), jump to else

            LBL 00  // true
            CF 05
            GTO 01  // jump to resume

            LBL 02  // else (false)
            CF 06

            LBL 01  // resume
            FIX 02
        """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_if_elif(self):
        src = """
            if FS(20):
                CF(5)
            elif FS(21):
                CF(6)
            else:
                CF(7)
            FIX(2)  
        """
        expected_descriptive = dedent("""
            FS? 20
            GTO if body
            GTO elif 1

            LBL if body
            CF 05
            GTO resume

            LBL elif 1
            FS? 21
            GTO elif body 1
            GTO else

            LBL elif body 1
            CF 06
            GTO resume

            LBL else
            CF 07

            LBL resume
            FIX 02
        """)

        """
        Label allocation:
            label_if_body   00
            label_resume    01
            label_else      02
            label_elif      03
            label_elif_body 04
        """
        expected = dedent("""
            FS? 20
            GTO 00  // if body
            GTO 03  // elif

            LBL 00  // if body
            CF 05
            GTO 01  // resume

            LBL 03  // elif
            FS? 21
            GTO 04  // elif body
            GTO 02  // else

            LBL 04  // elif body
            CF 06
            GTO 01  // resume

            LBL 02  // else
            CF 07

            LBL 01  // resume
            FIX 02
        """)

        lines = self.parse(dedent(src), debug_gen_descriptive_labels=True)
        self.compare(de_comment(expected_descriptive), lines, dump=True)

        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True)

    def test_if_elif_elif(self):
        src = """
            if FS(20):
                pass
            elif FS(21):
                pass
            elif FS(22):
                pass
            else:
                pass
            FIX(2)  
        """
        expected_descriptive = dedent("""
            FS? 20
            GTO if body
            GTO elif 1

            LBL if body
            GTO resume

            LBL elif 1
            FS? 21
            GTO elif body 1   // new
            GTO elif 2  // 2nd

            LBL elif body 1
            GTO resume

            // ---- new ------ \.
            
            LBL elif 2 // 2nd
            FS? 22
            GTO elif body 2
            GTO else

            LBL elif body 2
            GTO resume

            // ---- new end -- /.

            LBL else

            LBL resume
            FIX 02
        """)

        """
        Label allocation:
            label_if_body     00
            label_resume      01
            label_else        02
            label_elif        03
            label_elif_body   04
            label_elif 2      05  // new
            label_elif_body 2 06  // new
        """
        expected = dedent("""
            FS? 20
            GTO 00  // if body
            GTO 03  // elif

            LBL 00  // if body
            GTO 01  // resume

            LBL 03  // elif
            FS? 21
            GTO 04  // elif body
            GTO 05  // elif (2nd)

            LBL 04  // elif body
            GTO 01  // resume


            // This is the second elif
            LBL 05  // elif (2nd)
            FS? 22
            GTO 06  // elif body (2nd)
            GTO 02  // else
            // This is the second elif body
            LBL 06  // elif body (2nd)
            GTO 01  // resume


            LBL 02  // else

            LBL 01  // resume
            FIX 02
        """)

        lines = self.parse(dedent(src), debug_gen_descriptive_labels=True)
        self.compare(de_comment(expected_descriptive), lines, dump=True)

        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True)


    def test_view_variable(self):
        src = """
            a = 100
            VIEW(a)
        """
        expected = dedent("""
            100
            STO 00
            VIEW 00
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True)

    # returns and strings and compares

    def test_return(self):
        src = """
            def main():
                return
        """
        expected = dedent("""
            LBL "main"
            RTN
        """)
        lines = self.parse(dedent(src), debug_gen_descriptive_labels=False)
        self.compare(de_comment(expected), lines, dump=True)

    def test_return_multiple(self):
        src = """
            def main():
                return 5
                pass
                return
        """
        expected = dedent("""
            LBL "main"
            5
            RTN
            RTN
        """)
        lines = self.parse(dedent(src), debug_gen_descriptive_labels=False)
        self.compare(de_comment(expected), lines, dump=True)

    def test_compare(self):
        src = """
            if 2 > 1:
                PSE()
        """
        expected = dedent("""
            2
            1
            X<Y?
            GTO 00  // if body
            GTO 01  // resume
            LBL 00  // if body
            PSE
            LBL 01  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True)

    def test_elif_view(self):
        src = """
            def selectr(n):
                msg = num_to_txt(n)
                VIEW(n)
                PSE()
                VIEW(msg)
                
            def num_to_txt(n):
                if n == 0:
                    return 999 # "zero"
                elif n == 1:
                    return "one"
                elif n == 2:
                    return "two"
                else:
                    return "dunno"
        """
        expected = dedent("""
            LBL "selectr"
            STO 00  // param: n
            RDN
            RCL 00  // n
            XEQ A  // num_to_txt()
            STO 01  // msg = 
            VIEW 00  // n
            PSE
            VIEW 01  // msg
            RTN  // end def selectr
            LBL A  // def num_to_txt
            STO 00  // param: n
            RDN
            RCL 00  // n
            0
            X=Y?
            GTO 00  // if body
            GTO 03  // elif 1
            LBL 00  // if body
            999
            RTN  // return
            GTO 01  // resume
            LBL 03  // elif 1
            RCL 00  // n
            1
            X=Y?
            GTO 04  // elif body 1
            GTO 05  // elif 2
            LBL 04  // elif body 1
            "one"
            ASTO ST X
            RTN  // return
            GTO 01  // resume
            LBL 05  // elif 2
            RCL 00  // n
            2
            X=Y?
            GTO 06  // elif body 2
            GTO 02  // else
            LBL 06  // elif body 2
            "two"
            ASTO ST X
            RTN  // return
            GTO 01  // resume
            LBL 02  // else
            "dunno"
            ASTO ST X
            RTN  // return
            LBL 01  // resume
            RTN  // end def num_to_txt        
        """)
        lines = self.parse(dedent(src))
        # print(self.visitor.program.dump(linenos=True, comments=False))  # for pasting into free42
        self.compare(de_comment(expected), lines, dump=True)

    def test_comment(self):
        src = """
            # nothing here
            x = 1  # my comment
            # or here
        """
        expected = dedent("""
            1
            STO 00  // x = # my comment
        """)
        lines = self.parse(dedent(src))
        self.compare(expected, lines, dump=True, keep_comments=True)

