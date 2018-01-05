from test_base import BaseTest
from scope import Scopes, Scope
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class ScopeTests(BaseTest):

    def test_scope_default(self):
        scopes = Scopes()
        self.assertEqual(1, len(scopes))
        self.assertTrue(scopes.current_empty)

    def test_scopes_push(self):
        scopes = Scopes()
        self.assertEqual(1, len(scopes))
        scopes.push()
        self.assertEqual(2, len(scopes))
        scopes.pop()
        self.assertEqual(1, len(scopes))

    def test_scopes_push_pop(self):
        scopes = Scopes()
        self.assertEqual(1, len(scopes))
        self.assertTrue(scopes.current_empty)
        scopes.push()
        self.assertEqual(2, len(scopes))
        self.assertTrue(scopes.current_empty)
        scopes._add_mapping('a', 'blah')
        self.assertFalse(scopes.current_empty)
        scopes.pop()
        self.assertEqual(1, len(scopes))
        self.assertTrue(scopes.current_empty)

    def test_scope_cannot_pop_default(self):
        scopes = Scopes()
        scopes.pop()
        self.assertEqual(1, len(scopes))

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

    # New thinking - don't reuse registers and start testing var_to_reg() not _add_mapping()

    def test_register_allocation_multiple_scope_pop(self):
        scopes = Scopes()
        scopes.var_to_reg('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.push()
        scopes.var_to_reg('a')
        self.assertEqual('01', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('00', scopes.get_register('a'))
        scopes.var_to_reg('b')
        self.assertEqual('02', scopes.get_register('b'))

    def test_do_not_reuse_registers(self):
        scopes = Scopes()
        scopes.var_to_reg('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.push()
        scopes.var_to_reg('a')
        self.assertEqual('01', scopes.get_register('a'))
        scopes.var_to_reg('b')
        self.assertEqual('02', scopes.get_register('b'))
        scopes.pop()
        # Back at the original scope, only 'a' exists but registers 0,1,2 used
        self.assertEqual('00', scopes.get_register('a'))
        # new registers should be allocated for new var names
        scopes.var_to_reg('nn')
        self.assertEqual('03', scopes.get_register('nn'))
        # new registers should be allocated for old var names that are now popped
        scopes.var_to_reg('b')
        self.assertEqual('04', scopes.get_register('b'))

