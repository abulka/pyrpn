from test_base import BaseTest
from scope import ScopeStack, Scope
from rpn import RecursiveRpnVisitor
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class VarnameLowerTests(BaseTest):

    def test_lowercase_varname(self):
        v = RecursiveRpnVisitor()
        register = v.var_name_to_register('x')
        self.assertEqual('00', register)

    def test_lowercase_varname_two(self):
        v = RecursiveRpnVisitor()
        register_x = v.var_name_to_register('x')
        register_y = v.var_name_to_register('y')
        self.assertEqual('00', register_x)
        self.assertEqual('01', register_y)

    def test_lowercase_varname_two_x(self):
        v = RecursiveRpnVisitor()
        register_x = v.var_name_to_register('x')
        self.assertEqual('00', register_x)
        register_x = v.var_name_to_register('x')
        self.assertEqual('00', register_x)

    def test_lowercase_varname_two_x_two_scopes(self):
        v = RecursiveRpnVisitor()
        register_x = v.var_name_to_register('x')
        self.assertEqual('00', register_x)
        v.scope_stack.push()
        register_x = v.var_name_to_register('x')
        self.assertEqual('01', register_x)

    def test_lowercase_varname_two_x_two_scopes_pop(self):
        v = RecursiveRpnVisitor()
        v.var_name_to_register('x')
        v.scope_stack.push()
        v.var_name_to_register('x')
        v.scope_stack.pop()
        register_x = v.var_name_to_register('x')
        self.assertEqual('00', register_x)

class VarnameUpperTests(BaseTest):

    def test_uppercase_varname(self):
        v = RecursiveRpnVisitor()
        register = v.var_name_to_register('X')
        self.assertEqual('"X"', register)

    def test_uppercase_lowercase_varname(self):
        v = RecursiveRpnVisitor()
        register = v.var_name_to_register('X')
        self.assertEqual('"X"', register)
        register = v.var_name_to_register('x')
        self.assertEqual('00', register)
        register = v.var_name_to_register('X')
        self.assertEqual('"X"', register)

    def test_uppercase_two_scopes(self):
        """
        uppercase varnames are global so scopes don't apply, but we still make mappings to the same register in each scope
        """
        v = RecursiveRpnVisitor()
        v.var_name_to_register('X')
        v.scope_stack.push()
        self.assertEqual('"X"', v.var_name_to_register('X'))

    def test_uppercase_three_scopes(self):
        v = RecursiveRpnVisitor()
        v.var_name_to_register('X')
        v.scope_stack.push()
        v.var_name_to_register('X')
        v.scope_stack.push()
        self.assertEqual('"X"', v.var_name_to_register('X'))

