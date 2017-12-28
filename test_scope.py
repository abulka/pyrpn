from test_base import BaseTest
from scope import Scopes, Scope
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class ScopeTests(BaseTest):

    def test_scope_default(self):
        scopes = Scopes()
        self.assertEqual(1, scopes.length)
        self.assertTrue(scopes.current_empty)

    def test_scopes_push(self):
        scopes = Scopes()
        self.assertEqual(1, scopes.length)
        scopes.push()
        self.assertEqual(2, scopes.length)
        scopes.pop()
        self.assertEqual(1, scopes.length)

    def test_scopes_push_pop(self):
        scopes = Scopes()
        self.assertEqual(1, scopes.length)
        self.assertTrue(scopes.current_empty)
        scopes.push()
        self.assertEqual(2, scopes.length)
        self.assertTrue(scopes.current_empty)
        scopes._add_mapping('a', 'blah')
        self.assertFalse(scopes.current_empty)
        scopes.pop()
        self.assertEqual(1, scopes.length)
        self.assertTrue(scopes.current_empty)

    def test_scope_cannot_pop_default(self):
        scopes = Scopes()
        scopes.pop()
        self.assertEqual(1, scopes.length)

    def test_scope_empty(self):
        scopes = Scopes()
        self.assertTrue(scopes.current_empty)
        scopes._add_mapping('a', 'blah')
        self.assertFalse(scopes.current_empty)

    def test_scope_default(self):
        scopes = Scopes()
        scopes._add_mapping('a', '"A"')
        self.assertEqual('"A"', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('"A"', scopes.get_register('a'))

    def test_register_allocation_explicit(self):
        scopes = Scopes()
        scopes.push()
        scopes._add_mapping('X', '"X"')
        self.assertEqual('"X"', scopes.get_register('X'))
        scopes.pop()
        self.assertRaises(KeyError, scopes.get_register, 'X')

    def test_register_allocation_auto(self):
        scopes = Scopes()
        scopes.push()
        scopes._add_mapping('a')
        self.assertEqual('00', scopes.get_register('a'))

    def test_scope_double(self):
        scopes = Scopes()
        scopes.push()
        scopes._add_mapping('a', '00')
        scopes.push()
        scopes._add_mapping('a', '01')
        self.assertEqual('01', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('00', scopes.get_register('a'))

    def test_register_allocation_mixed(self):
        scopes = Scopes()
        scopes._add_mapping('a', 'X')
        scopes._add_mapping('b')
        scopes._add_mapping('c')
        self.assertEqual('X', scopes.get_register('a'))
        self.assertEqual('00', scopes.get_register('b'))
        self.assertEqual('01', scopes.get_register('c'))

    def test_register_allocation_multiple_scopes(self):
        scopes = Scopes()
        scopes._add_mapping('a')
        scopes._add_mapping('b')
        self.assertEqual('00', scopes.get_register('a'))
        self.assertEqual('01', scopes.get_register('b'))
        scopes.push()
        scopes._add_mapping('a')
        scopes._add_mapping('zz')
        self.assertEqual('02', scopes.get_register('a'))
        self.assertEqual('03', scopes.get_register('zz'))

    def test_register_allocation_multiple_scope_pop(self):
        scopes = Scopes()
        scopes._add_mapping('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.push()
        scopes._add_mapping('a')
        self.assertEqual('01', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('00', scopes.get_register('a'))
        scopes._add_mapping('b')
        self.assertEqual('01', scopes.get_register('b'))

