import unittest
from test_base import BaseTest
from scope import Scopes, Scope
import logging
from logger import config_log
from rpn_exceptions import RpnError

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
        self.assertRaises(RpnError, scopes.get_register, 'X')

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


class MultipleScopes(BaseTest):

    # trickle back stage 1 semantics

    def test_stage1_trickle_back_variable_referencing(self):
        """
        Multiple scopes

        If variable 'a' is referenced in current scope
            - if its just a load: look backwards into previous scopes for 'a'.
            - if its a store: overrides 'a' of previous scope, unless 'global' or 'nonlocal' declared

        How to know when to use previous scope or recreate variable in the new scope?  Well python and
        javascript have different approaches. Python assumes local, javascript assumes global. Change
        the python assumption by declaring 'global' or 'nonlocal'.  Change the javascript assumption by
        declaring the variable local with 'let'.

        Stage 1 implementation:
            If its a recall - trickle back, look to previous scope
            If its an assign/store - trickle back, look to previous scope

        Future (maybe):

        Stage 2 implementation:
            If its an assign/store - assume local and create new
        Stage 3 implementation:
            If its an assign/store - assume local and create new, unless 'global' or 'nonlocal' declared
        """
        scopes = Scopes()
        scopes.var_to_reg('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.push()
        scopes.var_to_reg('a')
        self.assertEqual('00', scopes.get_register('a'))  # stage 1 semantics

    def test_lowercase_varname_two_x_two_scopes(self):
        scopes = Scopes()
        register_x = scopes.var_to_reg('x')
        self.assertEqual('00', register_x)
        scopes.push()
        register_x = scopes.var_to_reg('x')
        self.assertEqual('00', register_x)  # stage 1 trickle back semantics, otherwise would be 01

    # Never reuse registers

    def test_register_allocation_multiple_scope_pop(self):
        """
        When I create code objects, for each Python function that is compiled, instead of mapping variables to
        offsets that always start at ‘0’ (indicating the memory location on a newly pushed stack frame) I instead map
        to offsets into a fixed piece of memory, continually incrementing the offsets and never going backwards. The
        first Python function’s code object might use offsets 0..5, the next Python function’s code object would use
        6..8 etc.
        """
        scopes = Scopes()
        scopes.var_to_reg('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.push()
        scopes.var_to_reg('a')
        # self.assertEqual('01', scopes.get_register('a'))  # old original semantics
        self.assertEqual('00', scopes.get_register('a'))  # stage 1 semantics
        scopes.pop()
        self.assertEqual('00', scopes.get_register('a'))
        scopes.var_to_reg('b')
        # self.assertEqual('02', scopes.get_register('b'))
        self.assertEqual('01', scopes.get_register('b'))

    def test_stage1_do_not_reuse_registers(self):
        scopes = Scopes()
        scopes.var_to_reg('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.push()
        scopes.var_to_reg('a')
        self.assertEqual('00', scopes.get_register('a'))
        scopes.var_to_reg('b')
        self.assertEqual('01', scopes.get_register('b'))
        scopes.pop()
        # Back at the original scope, only 'a' exists but registers 0,1 used
        self.assertEqual('00', scopes.get_register('a'))
        # new registers should be allocated for new var names
        scopes.var_to_reg('nn')
        self.assertEqual('02', scopes.get_register('nn'))
        # new registers should be allocated for old var names that are now popped
        scopes.var_to_reg('b')
        self.assertEqual('03', scopes.get_register('b'))

