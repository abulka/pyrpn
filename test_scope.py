from test_base import BaseTest
from scope import ScopeStack, Scope
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class ScopeTests(BaseTest):

    def test_scope_default(self):
        scopes = ScopeStack()
        self.assertEqual(1, len(scopes.stack))
        
    def test_scope_cannot_pop_default(self):
        scopes = ScopeStack()
        scopes.pop()
        self.assertEqual(1, len(scopes.stack))
        
    def test_scope_default(self):
        scopes = ScopeStack()
        scopes.add_mapping('a', '"A"')
        self.assertEqual('"A"', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('"A"', scopes.get_register('a'))

    def test_register_allocation_explicit(self):
        scopes = ScopeStack()
        scopes.push()
        scopes.add_mapping('X', '"X"')
        self.assertEqual('"X"', scopes.get_register('X'))
        scopes.pop()
        self.assertRaises(KeyError, scopes.get_register, 'X')

    def test_register_allocation_auto(self):
        scopes = ScopeStack()
        scopes.push()
        scopes.add_mapping('a')
        self.assertEqual('00', scopes.get_register('a'))

    def test_scope_double(self):
        scopes = ScopeStack()
        scopes.push()
        scopes.add_mapping('a', '00')
        scopes.push()
        scopes.add_mapping('a', '01')
        self.assertEqual('01', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('00', scopes.get_register('a'))

    def test_register_allocation_mixed(self):
        scopes = ScopeStack()
        scopes.add_mapping('a', 'X')
        scopes.add_mapping('b')
        scopes.add_mapping('c')
        self.assertEqual('X', scopes.get_register('a'))
        self.assertEqual('00', scopes.get_register('b'))
        self.assertEqual('01', scopes.get_register('c'))

    def test_register_allocation_multiple_scopes(self):
        scopes = ScopeStack()
        scopes.add_mapping('a')
        scopes.add_mapping('b')
        self.assertEqual('00', scopes.get_register('a'))
        self.assertEqual('01', scopes.get_register('b'))
        scopes.push()
        scopes.add_mapping('a')
        scopes.add_mapping('zz')
        self.assertEqual('02', scopes.get_register('a'))
        self.assertEqual('03', scopes.get_register('zz'))

    def test_register_allocation_multiple_scope_pop(self):
        scopes = ScopeStack()
        scopes.add_mapping('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.push()
        scopes.add_mapping('a')
        self.assertEqual('01', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('00', scopes.get_register('a'))
        scopes.add_mapping('b')
        self.assertEqual('01', scopes.get_register('b'))
