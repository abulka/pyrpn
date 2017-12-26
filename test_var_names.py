from test_base import BaseTest
from scope import Scopes, Scope
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
        v.scopes.push()
        register_x = v.var_name_to_register('x')
        self.assertEqual('01', register_x)

    def test_lowercase_varname_two_x_two_scopes_pop(self):
        v = RecursiveRpnVisitor()
        v.var_name_to_register('x')
        v.scopes.push()
        v.var_name_to_register('x')
        v.scopes.pop()
        register_x = v.var_name_to_register('x')
        self.assertEqual('00', register_x)

# class VarnameStackTests(BaseTest):
#
#     def test_X(self):
#         v = RecursiveRpnVisitor()
#         register = v.var_name_to_register('a', use_stack_register=0)
#         self.assertEqual('ST X', register)
#
#     def test_Y(self):
#         v = RecursiveRpnVisitor()
#         register = v.var_name_to_register('a', use_stack_register=1)
#         self.assertEqual('ST Y', register)

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
        v.scopes.push()
        self.assertEqual('"X"', v.var_name_to_register('X'))

    def test_uppercase_three_scopes(self):
        v = RecursiveRpnVisitor()
        v.var_name_to_register('X')
        v.scopes.push()
        v.var_name_to_register('X')
        v.scopes.push()
        self.assertEqual('"X"', v.var_name_to_register('X'))

