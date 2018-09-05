import unittest
from test_base import BaseTest
from de_comment import de_comment
from textwrap import dedent
import logging
from logger import config_log
from rpn import RpnError
from parse import parse
import settings

log = logging.getLogger(__name__)
config_log(log)


class RpnTestMiscBugs1(BaseTest):

    def parse(self, text):
        self.program = parse(text, debug_options={'dump_ast': True, 'emit_pyrpn_lib': False})
        self.program.dump()

    def compare(self, expected, keep_comments=False):
        self.assertEqual(expected.strip(), self.program.lines_to_str(comments=keep_comments).strip())

    # TESTS

    # Misc bugs

    """
    Assignment Operators (e.g. += -= etc.) on matrix/list elements not currently supported - 
    try using the longer explicit syntax (e.g. a[0] = a[0] + 1) as a workaround
        """
    @unittest.skip('tofix')
    def test_assignment_operators_not_supported_crash1_underlying_reason(self):
        # Need to support a[0] += 1 syntax
        # it is already supported on variables e.g. a += 1
        self.parse(dedent("""
            a = [0]
            # a[0] = 1
            a[0] += 1
            """))
        expected = dedent("""

            """)
        # self.compare(de_comment(expected))

    def test_assignment_operators_not_supported_on_lists(self):
        # workaround which at least tells the user of the problem
        src = """
            a = [0]
            a[0] += 1
        """
        self.assertRaises(RpnError, self.parse, dedent(src))

    @unittest.skip('tofix')
    def test_assignment_operators_not_supported_crash1(self):
        # from http://www.hpmuseum.org/forum/thread-10701-post-103237.html#pid103237
        self.parse(dedent("""
            for i in range(100):
              a = [0,0,0,0,0,0,0,0,0]
              r = 8
              s = 0
              x = 0
              y = 0
              t = 0
              while True:
                x += 1
                a[x] = r
                while True:
                  s += 1
                  y = x
                  while y>1:
                    y -= 1
                    t = a[x]-a[y]
                    if t==0 or x-y==ABS(t):
                      y=0
                      a[x] -= 1  # <------- this is not supported by me yet
                      while a[x]==0:
                        x -= 1
                        a[x] -= 1  # <------- this is not supported by me yet
                  if y==1:
                    break;
                if x==r:
                  break;
              print(s)

            """))

        expected = dedent("""
            """)
        # self.compare(de_comment(expected))

    def test_works_ok_but_runs_infinitely_why(self):
        # from http://www.hpmuseum.org/forum/thread-10701-post-103237.html#pid103237
        # adjusted the syntax to generate rpn, but it runs forever - why?
        self.parse(dedent("""
            for i in range(100):
              a = [0,0,0,0,0,0,0,0,0]
              r = 8
              s = 0
              x = 0
              y = 0
              t = 0
              while True:
                x += 1
                a[x] = r
                while True:
                  s += 1
                  y = x
                  while y>1:
                    y -= 1
                    t = a[x]-a[y]
                    if t==0 or x-y==ABS(t):
                      y=0
                      a[x] = a[x] - 1  # a[x] -= 1
                      while a[x]==0:
                        x -= 1
                        a[x] = a[x] - 1  # a[x] -= 1
                  if y==1:
                    break;
                if x==r:
                  break;
              print(i, s)
            """))

        expected = dedent("""
            """)
        # self.compare(de_comment(expected))

