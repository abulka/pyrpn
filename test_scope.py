from test_base import BaseTest
from scope import ScopeStack, Scope
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class ScopeTests(BaseTest):

    def test_scope_easy(self):
        stack = ScopeStack()
        stack.allow_mappings = True

        stack.push()
        stack.add_mapping('a', '00')

        self.assertEqual('00', stack.get_register('a'))

    def test_scope_double(self):
        stack = ScopeStack()
        stack.allow_mappings = True

        stack.push()
        stack.add_mapping('a', '00')
        stack.push()
        stack.add_mapping('a', '01')

        self.assertEqual('01', stack.get_register('a'))
        stack.pop()
        self.assertEqual('00', stack.get_register('a'))

    def test_scope_mappings_off(self):
        stack = ScopeStack()
        stack.allow_mappings = False

        stack.push()
        self.assertRaises(RuntimeError, stack.add_mapping, 'a', '00')
        # self.assertRaises(KeyError, stack.get_register, 'a')

    def test_register_allocation_auto(self):
        stack = ScopeStack()
        stack.push()
        stack.allow_mappings = True

        stack.add_mapping('a')
        self.assertEqual('00', stack.get_register('a'))

    def test_register_allocation_override(self):
        stack = ScopeStack()
        stack.push()
        stack.allow_mappings = True

        stack.add_mapping('a', 'X')
        self.assertEqual('X', stack.get_register('a'))

    def test_register_allocation_multiple(self):
        stack = ScopeStack()
        stack.push()
        stack.allow_mappings = True

        stack.add_mapping('a', 'X')
        stack.add_mapping('b')
        stack.add_mapping('c')
        self.assertEqual('X', stack.get_register('a'))
        self.assertEqual('00', stack.get_register('b'))
        self.assertEqual('01', stack.get_register('c'))

    def test_register_allocation_multiple_scopes(self):
        stack = ScopeStack()
        stack.push()
        stack.allow_mappings = True

        stack.add_mapping('a')
        stack.add_mapping('b')
        self.assertEqual('00', stack.get_register('a'))
        self.assertEqual('01', stack.get_register('b'))

        stack.push()
        stack.add_mapping('a')
        stack.add_mapping('zz')
        self.assertEqual('02', stack.get_register('a'))
        self.assertEqual('03', stack.get_register('zz'))

    def test_register_allocation_multiple_scope_pop(self):
        stack = ScopeStack()
        stack.push()
        stack.allow_mappings = True

        stack.add_mapping('a')
        self.assertEqual('00', stack.get_register('a'))

        stack.push()
        stack.add_mapping('a')
        self.assertEqual('01', stack.get_register('a'))

        stack.pop()
        self.assertEqual('00', stack.get_register('a'))

        stack.add_mapping('b')
        self.assertEqual('01', stack.get_register('b'))

