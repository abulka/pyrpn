import unittest
import asttokens
from test_base import BaseTest
from textwrap import dedent
import logging
from logger import config_log
from rpn import RpnError
from lookahead_rpn import LookaheadRpnVisitor
import astunparse

log = logging.getLogger(__name__)
config_log(log)

class LookaheadTests(BaseTest):

    def scan(self, text):
        atok = asttokens.ASTTokens(text, parse=True)
        tree = atok.tree
        log.debug(astunparse.dump(tree))  # output is nice and compact
        visitor = LookaheadRpnVisitor()
        visitor.atok = atok
        visitor.visit(tree)
        return visitor.labels

    # TESTS

    def test_defs_first_def_is_named(self):
        labels = self.scan(dedent("""
            def a():
                pass
            """))
        # print(labels.dump())
        data = labels.label_data
        self.assertEqual(len(data), 1)
        self.assertEqual(data['a'], '"a"')

    def test_defs_second_def_is_local(self):
        labels = self.scan(dedent("""
            def a():
                pass
            def b():
                pass
            """))
        # print(labels.dump())
        data = labels.label_data
        self.assertEqual(len(data), 2)
        self.assertEqual(data['a'], '"a"')
        self.assertEqual(data['b'], 'A')

    def test_defs_rpn_export(self):
        labels = self.scan(dedent("""
            def a():
                pass
            def b():  # rpn: export
                pass
            """))
        # print(labels.dump())
        data = labels.label_data
        self.assertEqual(len(data), 2)
        self.assertEqual(data['a'], '"a"')
        self.assertEqual(data['b'], '"b"')

    def test_defs_rpn_lbl_becomes_first_named(self):
        labels = self.scan(dedent("""
            LBL("main")
            x = 100
            def a():
                pass
            def b():  # rpn: export
                pass
            """))
        # print(labels.dump())
        data = labels.label_data
        self.assertEqual(len(data), 3)
        self.assertEqual(data['main'], '"main"')
        self.assertEqual(data['a'], 'A')
        self.assertEqual(data['b'], '"b"')

    def test_defs_nested(self):
        labels = self.scan(dedent("""
            def func():
                def func2():
                    pass
            """))
        # print(labels.dump())
        data = labels.label_data
        self.assertEqual(len(data), 2)
        self.assertEqual(data['func'], '"func"')
        self.assertEqual(data['func2'], 'A')

    def test_defs_nested_deep(self):
        labels = self.scan(dedent("""
            def func():
                def func2():
                    pass
                def func3():
                    pass  
                    def func4():
                        pass
            """))
        # print(labels.dump())
        data = labels.label_data
        self.assertEqual(len(data), 4)
        self.assertEqual(data['func'], '"func"')
        self.assertEqual(data['func2'], 'A')
        self.assertEqual(data['func3'], 'B')
        self.assertEqual(data['func4'], 'C')

    def test_defs_duplicate_disallow(self):
        src = """
            def func():
                func2()
                def func2():
                    pass
            def func2():  # duplicate of inner func2 - too hard to allow this
                pass  
            """
        self.assertRaisesRegex(RpnError, ".*line: 6.*", self.scan, dedent(src))
