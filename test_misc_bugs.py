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
    from http://www.hpmuseum.org/forum/thread-10701-post-103237.html#pid103237
    """

    @unittest.skip('tofix')
    def test_crash1(self):
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
                      a[x] -= 1
                      while a[x]==0:
                        x -= 1
                        a[x] -= 1
                  if y==1:
                    break;
                if x==r:
                  break;
              print(s)

            """))

        expected = dedent("""
            """)
        # self.compare(de_comment(expected))

    @unittest.skip('tofix')
    def test_crash1_underlying_reason(self):

        self.parse(dedent("""
            a = [0]
            # a[0] = 1
            a[0] += 1
            """))
        expected = dedent("""

            """)
        # self.compare(de_comment(expected))

    def test_assignment_operators_not_supported_on_lists(self):
        src = """
            a = [0]
            a[0] += 1
        """
        self.assertRaises(RpnError, self.parse, dedent(src))
