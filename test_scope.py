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
        scopes.add_mapping('a', 'blah')
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
        scopes.add_mapping('a', 'blah')
        self.assertFalse(scopes.current_empty)

    def test_scope_default(self):
        scopes = Scopes()
        scopes.add_mapping('a', '"A"')
        self.assertEqual('"A"', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('"A"', scopes.get_register('a'))

    def test_register_allocation_explicit(self):
        scopes = Scopes()
        scopes.push()
        scopes.add_mapping('X', '"X"')
        self.assertEqual('"X"', scopes.get_register('X'))
        scopes.pop()
        self.assertRaises(KeyError, scopes.get_register, 'X')

    def test_register_allocation_auto(self):
        scopes = Scopes()
        scopes.push()
        scopes.add_mapping('a')
        self.assertEqual('00', scopes.get_register('a'))

    def test_scope_double(self):
        scopes = Scopes()
        scopes.push()
        scopes.add_mapping('a', '00')
        scopes.push()
        scopes.add_mapping('a', '01')
        self.assertEqual('01', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('00', scopes.get_register('a'))

    def test_register_allocation_mixed(self):
        scopes = Scopes()
        scopes.add_mapping('a', 'X')
        scopes.add_mapping('b')
        scopes.add_mapping('c')
        self.assertEqual('X', scopes.get_register('a'))
        self.assertEqual('00', scopes.get_register('b'))
        self.assertEqual('01', scopes.get_register('c'))

    def test_register_allocation_multiple_scopes(self):
        scopes = Scopes()
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
        scopes = Scopes()
        scopes.add_mapping('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.push()
        scopes.add_mapping('a')
        self.assertEqual('01', scopes.get_register('a'))
        scopes.pop()
        self.assertEqual('00', scopes.get_register('a'))
        scopes.add_mapping('b')
        self.assertEqual('01', scopes.get_register('b'))

    # Allocation of function labels A through J and a through e

    def test_function_label_allocation_1(self):
        scopes = Scopes()
        scopes.add_function_mapping('func')
        self.assertEqual('A', scopes.get_label('func'))

    def test_function_label_allocation_multiple(self):
        scopes = Scopes()
        scopes.add_function_mapping('func')
        scopes.add_function_mapping('func2')
        self.assertEqual('A', scopes.get_label('func'))
        self.assertEqual('B', scopes.get_label('func2'))

    def test_function_label_push_pop(self):
        # labels are global so scope push pop does not affect anything
        scopes = Scopes()
        scopes.add_function_mapping('func')
        scopes.push()
        if not scopes.has_function_mapping('func'):
            scopes.add_function_mapping('func')
        self.assertEqual('A', scopes.get_label('func'))
        scopes.pop()
        self.assertEqual('A', scopes.get_label('func'))

    def test_function_multiple_mappings_refs_not_defs(self):
        scopes = Scopes()
        scopes.add_function_mapping('func')
        self.assertEqual('A', scopes.get_label('func'))
        scopes.add_function_mapping('func')
        self.assertEqual('A', scopes.get_label('func'))

    def test_function_multiple_mappings_refs_and_single_def(self):
        scopes = Scopes()
        scopes.add_function_mapping('func')
        self.assertEqual('A', scopes.get_label('func'))
        scopes.add_function_mapping('func')
        self.assertEqual('A', scopes.get_label('func'))
        scopes.add_function_mapping('func', called_from_def=True)
        self.assertEqual('A', scopes.get_label('func'))

    def test_function_replace_mapping_cos_two_defs(self):
        scopes = Scopes()
        scopes.add_function_mapping('func', called_from_def=True)
        self.assertEqual('A', scopes.get_label('func'))
        scopes.add_function_mapping('func', called_from_def=True)
        self.assertEqual('B', scopes.get_label('func'))

    def test_function_replace_function_mapping_then_ref(self):
        scopes = Scopes()
        scopes.add_function_mapping('func', called_from_def=True)
        self.assertEqual('A', scopes.get_label('func'))
        scopes.add_function_mapping('func', called_from_def=True)
        self.assertEqual('B', scopes.get_label('func'))
        scopes.add_function_mapping('func')
        self.assertEqual('B', scopes.get_label('func'))
