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

class RpnCodeGenTests(BaseTest):

    def parse(self, text, debug_gen_descriptive_labels=False):
        debug_options = {'gen_descriptive_labels': debug_gen_descriptive_labels,
                         'dump_ast': True,
                         'emit_pyrpn_lib': False}
        self.program = parse(text, debug_options)
        self.program.dump()
        return self.program.lines

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
            self.program.dump(comments=True)

        # All in one comparison
        self.assertEqual(expected.strip(), self.program.lines_to_str(comments=keep_comments).strip())

        if trace:
            expected = expected.strip().split('\n')
            for i, line in enumerate(lines):
                log.debug(f'expected={expected[i]}, got {line.text}')
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

    # For

    def test_for_range_two_param_literals(self):
        lines = self.parse(dedent("""
            for i in range(1, 200):
                pass
            """))
        expected = dedent("""
            // setup
            0.199
            STO 00
            
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected), lines, trace=False, dump=True)

    def test_for_range_one_param_literal(self):
        lines = self.parse(dedent("""
            for i in range(20):
                pass
            """))
        expected = dedent("""
            // setup
            -1.019
            STO 00
            
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected), lines, trace=False, dump=True)

    def test_for_range_two_param_var(self):
        lines = self.parse(dedent("""
            a = 0
            b = 200
            for i in range(a, b):
                pass
            """))
        expected = dedent("""
            0
            STO 00  // a
            200
            STO 01  // b

            // setup
            RCL 00
            RCL 01
            1       // step
            XEQ "PyIsgPr"
            STO 02  // range i
            
            LBL 00  // for
            ISG 02  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected), lines, trace=False, dump=True)

    def test_for_range_one_param_var(self):
        lines = self.parse(dedent("""
            n = 20
            for i in range(n):
                pass
            """))
        expected = dedent("""
            20
            STO 00
            
            // setup
            0
            RCL 00
            1       // step
            XEQ "PyIsgPr"
            STO 01  // i
            
            LBL 00  // for
            ISG 01  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected), lines, trace=False, dump=True)

    # for with step

    def test_for_step_two_param_literals(self):
        lines = self.parse(dedent("""
            for i in range(1, 200, 2):
                pass
            """))
        expected = dedent("""
            // setup
            -1.19902
            STO 00

            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected), lines, trace=False, dump=True)

    def test_for_step_two_param_literals_negative(self):
        lines = self.parse(dedent("""
            for i in range(-2, 200, 2):
                pass
            """))
        expected = dedent("""
            // setup
            -4.19902  // initial value must be -step value so that first incr. will bring it to the start range val
            STO 00

            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected), lines, trace=False, dump=True)

    def test_for_step_two_param_var_mixed(self):
        lines = self.parse(dedent("""
            b = 200
            for i in range(5, b, 10):
                pass
            """))
        expected = dedent("""
            200
            STO 00  // b

            // setup
            5
            RCL 00  // b
            10      // step
            XEQ "PyIsgPr"
            STO 01  // range i

            LBL 00  // for
            ISG 01  // test i
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected), lines, trace=False, dump=True)

    # for - other

    def test_for_range_loop_view_i(self):
        lines = self.parse(dedent("""
            for i in range(1,20):
                VIEW(i)
        """))
        expected = dedent("""
            // setup
            0.019
            STO 00
            
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            LBL 01  // for body
            RCL 00
            IP
            VIEW ST X
            GTO 00  // for
            LBL 02  // resume
            """)
        self.compare(de_comment(expected), lines, trace=False, dump=True)

    # for continues ....

    def test_for_range_with_body_accessing_i(self):
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
            
            1.003
            STO 00  // i =
                        
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume
            
            LBL 01  // for body
            RCL 00  // i
            IP
            STO+ "X"
            GTO 00  // for
                        
            LBL 02  // resume
            RCL "X"
            RTN
            """)
        self.compare(de_comment(expected), lines, trace=True, dump=True)

    def test_for_complex1(self):
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
            
            1.003
            STO 02  // i =

            LBL 00  // for
            ISG 02  // test
            GTO 01  // for body
            GTO 02  // resume
            
            LBL 01  // for body
            RCL 02  // i
            IP
            STO "X"
            RCL 02  // i
            IP
            STO+ 00 // x +=
            RCL 00  // x
            STO+ 01 // total +=
            GTO 00  // for

            LBL 02  // resume
            RCL 01  // total
            RTN
            """)
        self.compare(de_comment(expected), lines, trace=True, dump=True)

    def test_for_complex2(self):
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
            STO 00    // param n
            RDN

            100
            STO 01    // x

            10        // range start, 10
            RCL 00    // range end, n
            1         // step
            XEQ "PyIsgPr"
            STO 02    // i our counter

            LBL 00  // for
            ISG 02  // test
            GTO 01  // for body
            GTO 02  // resume

            LBL 01  // for body
            //PRV 02 // print i  TODO 
            RCL 00    // n
            STO+ 01   // x +=
            RCL 02    // i
            IP        // when using a loop counter elsewhere, IP it first
            STO+ 01   // x +=
            GTO 00  // for

            LBL 02  // resume
            RCL 01    // leave x on stack
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True, trace=True)

    def test_for_continue(self):
        src = """
            for i in range(1,3):
                continue
                PSE()
        """
        expected = dedent("""
            0.002
            STO 00
            
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume

            LBL 01  // for body
            GTO 00  // (continue)
            PSE
            GTO 00  // for
            
            LBL 02  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True, keep_comments=False)

    def test_for_break(self):
        src = """
            for i in range(1,3):
                break
                PSE()
        """
        expected = dedent("""
            0.002
            STO 00
            
            LBL 00  // for
            ISG 00  // test
            GTO 01  // for body
            GTO 02  // resume

            LBL 01  // for body
            GTO 02  // resume (break)
            PSE
            GTO 00  // for
            
            LBL 02  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True, keep_comments=False)

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
            XEQ "p2Param"
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
            XEQ "p2Param"
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
            XEQ "p2Param"
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
            XEQ "p2Param"
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
            XEQ "p2Param"
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
            XEQ "p2Param"
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
            LBL B  // def add()
            XEQ "p2Param"
            STO 02
            RDN
            STO 03
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

    # if

    def test_if_isFS(self):
        lines = self.parse(dedent("""
            if isFS(1):
                CF(1)
            FIX(2)
            """))
        expected = dedent("""
            1
            XEQ "PyFS"
            
            X≠0?
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
            if isFS(1):
                CF(5)
            else:
                CF(6)
            FIX(2)  
            """))
        expected = dedent("""
            1
            XEQ "PyFS"
            
            X≠0?
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
            if isFS(20):
                CF(5)
            elif isFS(21):
                CF(6)
            else:
                CF(7)
            FIX(2)  
        """
        expected_descriptive = dedent("""
            20
            XEQ "PyFS"
            X≠0?
            GTO if body
            GTO elif 1

            LBL if body
            CF 05
            GTO resume

            LBL elif 1
            21
            XEQ "PyFS"
            X≠0?
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
            20
            XEQ "PyFS"
            X≠0?
            GTO 00  // if body
            GTO 03  // elif

            LBL 00  // if body
            CF 05
            GTO 01  // resume

            LBL 03  // elif
            21
            XEQ "PyFS"
            X≠0?
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
            if isFS(20):
                pass
            elif isFS(21):
                pass
            elif isFS(22):
                pass
            else:
                pass
            FIX(2)  
        """
        expected_descriptive = dedent("""
            20
            XEQ "PyFS"
            X≠0?
            GTO if body
            GTO elif 1

            LBL if body
            GTO resume

            LBL elif 1
            21
            XEQ "PyFS"
            X≠0?
            GTO elif body 1   // new
            GTO elif 2  // 2nd

            LBL elif body 1
            GTO resume

            // ---- new ------ \.
            
            LBL elif 2 // 2nd
            22
            XEQ "PyFS"
            X≠0?
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
            20
            XEQ "PyFS"
            X≠0?
            GTO 00  // if body
            GTO 03  // elif

            LBL 00  // if body
            GTO 01  // resume

            LBL 03  // elif
            21
            XEQ "PyFS"
            X≠0?
            GTO 04  // elif body
            GTO 05  // elif (2nd)

            LBL 04  // elif body
            GTO 01  // resume


            // This is the second elif
            LBL 05  // elif (2nd)
            22
            XEQ "PyFS"
            X≠0?
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

    def test_compare_GT_if(self):
        src = """
            if 2 > 1:
                PSE()
        """
        expected = dedent("""
            2
            1
            XEQ "PyGT"
            X≠0?
            GTO 00  // if body
            GTO 01  // resume
            LBL 00  // if body
            PSE
            LBL 01  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

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
            STO 02  // param: n
            RDN
            RCL 02  // n
            0
            XEQ "PyEQ"
            X≠0?    // if true?
            GTO 00  // if body
            GTO 03  // elif 1
            LBL 00  // if body
            999
            RTN  // return
            GTO 01  // resume
            LBL 03  // elif 1
            RCL 02  // n
            1
            XEQ "PyEQ"
            X≠0?    // if true?
            GTO 04  // elif body 1
            GTO 05  // elif 2
            LBL 04  // elif body 1
            "one"
            ASTO ST X
            RTN  // return
            GTO 01  // resume
            LBL 05  // elif 2
            RCL 02  // n
            2
            XEQ "PyEQ"
            X≠0?    // if true?
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
            STO 00  // x
        """)
        lines = self.parse(dedent(src))
        self.compare(expected, lines, dump=True, keep_comments=True)

    def test_def_double_export(self):
        src = """
            def main():
                useful()
                
            def useful():  # rpn: export
                pass
        """
        expected = dedent("""
            LBL "main"
            XEQ A
            RTN
            LBL A
            LBL "useful"
            RTN
        """)
        lines = self.parse(dedent(src))
        self.compare(expected, lines, dump=True, keep_comments=False)

    def test_def_double_export_no_calls_till_later(self):
        # two clean definitions, no calls till later
        src = """
            def main():
                pass
                
            def useful():  # rpn: export
                pass
                
            main()
            useful()
        """
        expected = dedent("""
            LBL "main"
            RTN
            LBL "useful"
            RTN
            XEQ "main"
            XEQ "useful"
        """)
        lines = self.parse(dedent(src))
        self.compare(expected, lines, dump=True, keep_comments=False)

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

    # Expressions

    def test_expr_two_ops(self):
        src = """
            x = 1 + 2 - 6        
        """
        expected = dedent("""
            1
            2
            +
            6
            -
            STO 00
        """)
        lines = self.parse(dedent(src))
        self.compare(expected, lines, dump=True, keep_comments=False)

    def test_expr_two_ops_multiplication_precedence(self):
        src = """
            x = 1 + 2 * 6        
        """
        expected_ori = dedent("""
            2
            6
            *
            1
            +
            STO 00
        """)
        expected = dedent("""
            1
            2
            6
            *
            +
            STO 00
        """)
        lines = self.parse(dedent(src))
        self.compare(expected, lines, dump=True, keep_comments=False)

    def test_expr_brackets(self):
        src = """
            x = ((1 + 2) * (6 + 2 - 3) * (2 + 7)) / 200       
        """
        expected = dedent("""
            1
            2
            +
            6
            2
            +
            3
            -
            *
            2
            7
            +
            *
            200
            /
            STO 00
        """)
        lines = self.parse(dedent(src))
        self.compare(expected, lines, dump=True, keep_comments=False)

    # expression complexity protection

    def test_expr_ok_simple(self):
        src = """
            x = 1+2*(3+4)
        """
        self.parse(dedent(src))  # don't care about the result, as long as we don't blow

    def test_expr_ok_at_limit(self):
        src = """
            x = 1+2*(3+4)*(5+6) # still ok
        """
        self.parse(dedent(src))  # don't care about the result, as long as we don't blow

    def test_expr_blows_by_one(self):
        src = """
            1+2*(3+4)*(5+6*7)  # blows
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_expr_blow_stack_complex(self):
        # Complex expressions compile OK but may in practice overflow the stack, so warn
        src = """
            x = 1+2*(3+4*(5+6*(7+8*9)))       
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_expr_blow_stack_no_assign(self):
        # Complex expressions compile OK but may in practice overflow the stack, so warn
        src = """
            1+2*(3+4*(5+6*(7+8*9)))       
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_expr_blow_reset(self):
        # Need to be careful and reset the tracking of stack values after new lines.
        src = """
            1+2*(3+4)
            1+2*(3+4)
        """
        self.parse(dedent(src))  # don't care about the result, as long as we don't blow

    def test_expr_blow_reset2(self):
        # Need to be careful and reset the tracking of stack values after new lines.
        src = """
            FROM -= 1
            TO -= 1
            result = ABS(FROM) + TO / 1000
        """
        self.parse(dedent(src))  # don't care about the result, as long as we don't blow

    def test_expr_blow_reset3(self):
        # Need to be careful and reset the tracking of stack values after new lines.
        src = """
            hard = TO >= 0
            result = ABS(FROM) + TO / 1000
        """
        self.parse(dedent(src))  # don't care about the result, as long as we don't blow

    def test_expr_blow_reset4(self):
        # Need to be careful and reset the tracking of stack values after new lines.
        src = """
            for i in range(3, max_iterations, 2):
                if subtract:
                    result -= 1.0/i
                    subtract = False
        """
        self.parse(dedent(src))  # don't care about the result, as long as we don't blow

    def test_expr_mixed_bool(self):
        # this was reported to me as a bug
        src = """
            a < 0 or b < 0
        """
        self.parse(dedent(src))  # don't care about the result, as long as we don't blow

    def test_expr_mixed_bool_in_def(self):
        # this was reported to me as a bug because of expressions and booleans
        # interestingly, the visit_Expr is never done cos 'if' takes a BoolOp
        src = """
            def x(a, b):
              if a < 0 or b < 0:
                return 0
              return a+b
        """
        self.parse(dedent(src))  # don't care about the result, as long as we don't blow

    # More control structures

    def test_while(self):
        src = """
            while 1 < 2:
                pass
        """
        expected = dedent("""
            LBL 00  // while
            1
            2
            XEQ "PyLT"
            X≠0?    // while true?
            GTO 01  // while body
            GTO 02  // resume
            LBL 01  // while body
            GTO 00  // while (loop again)
            LBL 02  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True, keep_comments=False)

    def test_while_else(self):
        """
        The else clause is only executed when your while condition becomes false. If you break out of the loop,
        or if an exception is raised, it won't be executed.

        The else clause is executed if you exit a block normally, by hitting the loop condition or falling off the
        bottom of a try block. It is not executed if you break or return out of a block, or raise an exception. It
        works for not only while and for loops, but also try blocks.
        """
        src = """
            n = 10
            while n > 2:
                n -= 1
            else:
                VIEW(n)
        """
        expected = dedent("""
            10
            STO 00  // n
            LBL 00  // while
            RCL 00
            2
            XEQ "PyGT"
            X≠0?    // while true?
            GTO 01  // while body
            GTO 03  // else
            LBL 01  // while body
            1
            STO- 00
            GTO 00  // while (loop again)
            LBL 03  // else
            VIEW 00 // n
            LBL 02  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True, keep_comments=False)

    def test_while_break(self):
        src = """
            while 1 < 2:
                break
        """
        expected = dedent("""
            LBL 00  // while
            1
            2
            XEQ "PyLT"
            X≠0?    // while true?
            GTO 01  // while body
            GTO 02  // resume
            LBL 01  // while body
            GTO 02  // resume (break)
            GTO 00  // while (loop again)
            LBL 02  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True, keep_comments=False)

    def test_while_continue(self):
        src = """
            while 1 < 2:
                continue
        """
        expected = dedent("""
            LBL 00  // while
            1
            2
            XEQ "PyLT"
            X≠0?    // while true?
            GTO 01  // while body
            GTO 02  // resume
            LBL 01  // while body
            GTO 00  // continue (loop again)
            GTO 00  // while (loop again)
            LBL 02  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True, keep_comments=False)

    # @unittest.skip('offline')
    def test_while_else_break(self):
        """
        The else clause is only executed when your while condition becomes false. If you break out of the loop,
        or if an exception is raised, it won't be executed.
        """
        src = """
            n = 2
            while n == 2:
                break
            else:
                VIEW(n)
        """
        expected = dedent("""
            2
            STO 00  // n
            LBL 00  // while
            RCL 00
            2
            XEQ "PyEQ"
            X≠0?    // while true?
            GTO 01  // while body
            GTO 03  // else
            
            LBL 01  // while body
            GTO 02  // resume (break, thus skip else)
            GTO 00  // while
            
            LBL 03  // else
            VIEW 00 // n
            
            LBL 02  // resume
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines, dump=True, keep_comments=False)

    # Text and the alpha register

    """
    Normal string assignment to variables, long strings can be specified but only six chars make it into whatever variable 

    VIEW   - Normal VIEW, specify Python variables only.  Viewing stack or indirect not supported.
             Nothing to do with alpha register.  Any strings in variables will only be 6 chars. 
             Must have param.  If param is integer literal - it will evaluate and show stack X.
             
    AVIEW  - Same as built in, except takes parameters.  
             No params is allowed, which will insert a single AVIEW, just in case you have something 
             in the alpha register ready to show. Can specify strings and numbers and variables.
             
    alpha  - Builds strings in the alpha register, typically takes parameters.  
             No params inserts "".  (currently not implemented)
             If want to append, then add parameter append=True, ├"" any string is appended (currently not implemented)
             
    print  - synonym for AVIEW
    
    PROMPT - Same as built in, except takes parameters.  See AVIEW re taking multiple parameters.
    
    CLA    - Supported, same as RPN.
    AIP    - Append Integer part of x to the Alpha register.
             Supported, takes a variable as a parameter.  Must have parameter. If param is variable, ok.
             If param is number, ok.  If param is string - no good.
    ASTO   - Stores six chars from the alpha register into any Python variable.  
             Cannot specify stack registers or addressing specific registers.
             
    for loops and number formats 
             - Accessing a range i variable causes that variable to be converted to integer part otherwise all appends 
             to alpha are done in the current FIX etc. mode.  
             Unless its a literal integer, then it stays as integer
             If you want to append variables as ints then change the 
             FIX mode or whatever before you do the AVIEW. I might later support a mode=fix02 option in AVIEW 
             commands. (currently not implemented) 
                         
    """

    def test_text_string_assignment(self):
        src = """
            s = "this is my string"  # albeit only six chars make it into whatever register.
        """
        expected = dedent("""
            "this is my stri"
            ASTO 00
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_aview_deprecated(self):
        src = """
            aview("Hello there all is well in London!!")
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_text_VIEW_variable(self):
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
        self.compare(de_comment(expected), lines)

    def test_text_VIEW_no_args(self):
        src = """
            VIEW()
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_text_VIEW_literal_number(self):
        src = """
            VIEW(5)
        """
        expected = dedent("""
            5
            VIEW ST X
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_VIEW_literal_expr(self):
        src = """
            VIEW(5+6)
        """
        expected = dedent("""
            5
            6
            +
            VIEW ST X
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_VIEW_mixed_expr(self):
        src = """
            a = 10
            VIEW(a+6)
        """
        expected = dedent("""
            10
            STO 00
            RCL 00
            6
            +
            VIEW ST X
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_VIEW_bool_and_func_call_expr(self):
        src = """
            VIEW(not isFS(21))
        """
        expected = dedent("""
            21
            XEQ "PyFS"
            XEQ "PyBool"
            XEQ "PyNot"
            VIEW ST X
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_blow_stack_no(self):
        src = """
            alpha("this", " is ", "my ", "string", "and", "I", "can", "break it up")
        """
        expected = dedent("""
            "this"
            ├" is "
            ├"my "
            ├"string"
            ├"and"
            ├"I"
            ├"can"
            ├"break it up"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_mixed_blow_stack_no(self):
        src = """
            alpha("this", 1, " is ", 2, "my ", 3, "string", 4, "and", 5, "I", 6, "can", 7, "break it up")
        """
        expected = dedent("""
            "this"
            1
            ARCL ST X
            ├" is "
            2
            ARCL ST X
            ├"my "
            3
            ARCL ST X
            ├"string"
            4
            ARCL ST X
            ├"and"
            5
            ARCL ST X
            ├"I"
            6
            ARCL ST X
            ├"can"
            7
            ARCL ST X
            ├"break it up"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_ints_blow_stack_no(self):
        src = """
            alpha("a", 1, 2, 3, 4, 5, 6, 7)
        """
        expected = dedent("""
            "a"
            1
            ARCL ST X
            2
            ARCL ST X
            3
            ARCL ST X
            4
            ARCL ST X
            5
            ARCL ST X
            6
            ARCL ST X
            7
            ARCL ST X
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_expression_as_param(self):
        src = """
            alpha("a", 1+2, 3)
        """
        expected = dedent("""
            "a"
            1
            2
            +
            ARCL ST X
            3
            AIP
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_first_param_not_string(self):
        src = """
            n = 0
            alpha(n)
        """
        expected = dedent("""
            0
            STO 00
            ""
            ARCL 00
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_all_literal_nums(self):
        src = """
            alpha(1, 2, 3)
        """
        expected = dedent("""
            ""
            1
            ARCL ST X
            2
            ARCL ST X
            3
            ARCL ST X
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_AVIEW_no_args(self):
        src = """
            AVIEW()
        """
        expected = dedent("""
            AVIEW
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_AVIEW_with_arg(self):
        src = """
            AVIEW("hello")
        """
        expected = dedent("""
            "hello"
            AVIEW
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_AVIEW_of_previous_alpha(self):
        src = """
            alpha("this is my string")
            AVIEW()
        """
        expected = dedent("""
            "this is my str"
            ├"ing"
            AVIEW
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_AVIEW_long_string(self):
        src = """
            AVIEW("Hello there all is well in London!!")
        """
        expected = dedent("""
            "Hello there al"
            ├"l is well in L"
            ├"ondon!!"
            AVIEW
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)


    @unittest.skip('text handling - advanced - do later')
    def test_text_AVIEW_literal_number(self):
        src = """
            AVIEW(5)
        """
        expected = dedent("""
            5
            AIP
            AVIEW
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_AVIEW_literal_expr(self):
        src = """
            AVIEW(5+6)
        """
        expected = dedent("""
            5
            6
            +
            ARCL ST X
            AVIEW
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_AVIEW_mixed_expr(self):
        src = """
            a = 10
            AVIEW(a+6)
        """
        expected = dedent("""
            10
            STO 00
            RCL 00
            6
            +
            ARCL ST X
            AVIEW
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)


    def test_text_alpha_long_string(self):
        src = """
            alpha("Hello there all is well in London!!")
        """
        expected = dedent("""
            "Hello there al"
            ├"l is well in L"
            ├"ondon!!"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_no_args(self):
        src = """
            alpha()
        """
        expected = dedent("""
            ""
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_long_plus_literal(self):
        src = """
            alpha("Hello there all is well in London!!", 3)
        """
        expected = dedent("""
            "Hello there al"
            ├"l is well in L"
            ├"ondon!!"
            3
            ARCL ST X
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_two_str_params(self):
        src = """
            alpha("hello there this is a test of things", "fred is a very big man")
        """
        expected = dedent("""
            "hello there th"
            ├"is is a test o"
            ├"f things"
            ├"fred is a very"
            ├" big man"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_AIP_extended(self):
        """
        Nicer way to build strings
        """
        src = """
            n = 100
            alpha("Ans: ", n)
        """
        expected = dedent("""
            100
            STO 00
            "Ans: "
            ARCL 00
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_AIP_extended_two(self):
        """
        Nicer way to build strings
        """
        src = """
            n = 100
            alpha("Ans: ", n, " and ", n)
        """
        expected = dedent("""
            100
            STO 00
            "Ans: "
            ARCL 00
            ├" and "
            ARCL 00
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_alpha_no_append(self):
        src = """
            alpha("hi")
            alpha("there")
        """
        expected = dedent("""
            "hi"
            "there"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_alpha_append(self):
        src = """
            alpha("hi")
            alpha("there", append=True)
        """
        expected = dedent("""
            "hi"
            ├"there"
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_print(self):
        src = """
            print("Hello")
        """
        expected = dedent("""
            "Hello"
            AVIEW
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_PROMPT(self):
        src = """
            PROMPT("Hello", "there")
        """
        expected = dedent("""
            "Hello"
            ├"there"
            PROMPT
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_CLA(self):
        src = """
            CLA()
        """
        expected = dedent("""
            CLA
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_AIP(self):
        """
        AIP means append integer part of variable to alpha.
        Stack or specific register addressing not supported in Python but
        because AIP only works from stack x we need to recall into x.
        """
        src = """
            n = 100.12
            alpha("Ans: ")
            AIP(n) 
        """
        expected = dedent("""
            100.12
            STO 00
            "Ans: "
            RCL 00
            AIP
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_AIP_no_args(self):
        src = """
            AIP() 
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    @unittest.skip('text handling - advanced - do later')
    def test_text_AIP_literal_num(self):
        src = """
            AIP(5) 
        """
        expected = dedent("""
            5
            AIP
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_AIP_literal_num_expr(self):
        src = """
            AIP(5+6) 
        """
        expected = dedent("""
            5
            6
            +
            AIP
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_AIP_string_num(self):
        src = """
            AIP("some string:) 
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    def test_text_ASTO(self):
        src = """
        alpha("this is my string")
        ASTO(s)
        """
        expected = dedent("""
            "this is my str"
            ├"ing"
            ASTO(s)
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    def test_text_ASTO(self):
        src = """
            alpha("Hello there all is well in London!!")
            ASTO(s)  # Copy the first six characters into a register or variable
        """
        expected = dedent("""
            "Hello there al"
            ├"l is well in L"
            ├"ondon!!"
            ASTO 00
        """)
        lines = self.parse(dedent(src))
        self.compare(de_comment(expected), lines)

    @unittest.skip('text handling - advanced - do later')
    def test_text_for_range_AVIEW_access_i(self):
        """
        ensure can access i and that is an integer
        """
        lines = self.parse(dedent("""
            for i in range(2):
              AVIEW(i)
            """))
        expected = dedent("""
            -1.001
            STO 00
            LBL 00
            ISG 00
            GTO 01
            GTO 02
            LBL 01
            RCL 00
            IP
            ARCL ST X
            AVIEW            
            GTO 00
            LBL 02
            """)
        self.compare(de_comment(expected), lines, dump=True)

    @unittest.skip('text handling - advanced - do later')
    def test_text_for_range_AVIEW_access_i_mixed(self):
        """
        ensure can access i and that is an integer and can repeatedly do so and
        do expression calculations with it to boot.
        """
        lines = self.parse(dedent("""
            for i in range(2):
              AVIEW("index ", i, " ", i*2)
            """))
        expected = dedent("""
            -1.001
            STO 00
            LBL 00
            ISG 00
            GTO 01
            GTO 02
            LBL 01
            "index "
            RCL 00
            IP
            ARCL ST X
            ├" "
            RCL 00
            IP
            2
            *
            AVIEW            
            GTO 00
            LBL 02
            """)
        self.compare(de_comment(expected), lines, dump=True)

    # Number formats

    @unittest.skip('text handling - advanced - do later')
    def test_text_formats_FIX00(self):
        """
        ensure can access i and that is an integer and can repeatedly do so and
        do expression calculations with it to boot.
        """
        lines = self.parse(dedent("""
            FIX(00)
            """))
        expected = dedent("""
            FIX 00
            """)
        self.compare(de_comment(expected), lines, dump=True)

    # Scope

    def test_scope_basic(self):
        """
        Every variable should be given a new register, unless that variable is named the same and we are in the
        same scope.
        """
        lines = self.parse(dedent("""
            def main():
                x = 100
                f(x)
            
            def f(a):
                return a + 50
            """))
        expected = dedent("""
            LBL "main"
            100
            STO 00
            RCL 00
            XEQ A
            RTN
            LBL A
            STO 01
            RDN
            RCL 01
            50
            +
            RTN
            """)
        self.compare(de_comment(expected), lines, dump=True)

    def test_Pow(self):
        """
        Power function
        """
        lines = self.parse(dedent("""
            5**2
            """))
        expected = dedent("""
            5
            2
            Y↑X
            """)
        self.compare(de_comment(expected), lines, dump=True)

    @unittest.skip('tough one - how to return expr when not in a def')
    def test_add_inside_print(self):
        """
        Power function
        """
        lines = self.parse(dedent("""
            x = 1
            y = 2
            print(x+y)
            """))
        expected = dedent("""
            1
            STO 00
            2
            STO 01
            RCL 00
            RCL 01
            +
            AVIEW
            """)
        self.compare(de_comment(expected), lines, dump=True)

