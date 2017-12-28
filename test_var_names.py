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
        register = v.var_to_reg('x')
        self.assertEqual('00', register)

    def test_lowercase_varname_two(self):
        v = RecursiveRpnVisitor()
        register_x = v.var_to_reg('x')
        register_y = v.var_to_reg('y')
        self.assertEqual('00', register_x)
        self.assertEqual('01', register_y)

    def test_lowercase_varname_two_x(self):
        v = RecursiveRpnVisitor()
        register_x = v.var_to_reg('x')
        self.assertEqual('00', register_x)
        register_x = v.var_to_reg('x')
        self.assertEqual('00', register_x)

    def test_lowercase_varname_two_x_two_scopes(self):
        v = RecursiveRpnVisitor()
        register_x = v.var_to_reg('x')
        self.assertEqual('00', register_x)
        v.scopes.push()
        register_x = v.var_to_reg('x')
        self.assertEqual('01', register_x)

    def test_lowercase_varname_two_x_two_scopes_pop(self):
        v = RecursiveRpnVisitor()
        v.var_to_reg('x')
        v.scopes.push()
        v.var_to_reg('x')
        v.scopes.pop()
        register_x = v.var_to_reg('x')
        self.assertEqual('00', register_x)


class VarnameUpperTests(BaseTest):

    def test_uppercase_varname(self):
        v = RecursiveRpnVisitor()
        register = v.var_to_reg('X')
        self.assertEqual('"X"', register)

    def test_uppercase_lowercase_varname(self):
        v = RecursiveRpnVisitor()
        register = v.var_to_reg('X')
        self.assertEqual('"X"', register)
        register = v.var_to_reg('x')
        self.assertEqual('00', register)
        register = v.var_to_reg('X')
        self.assertEqual('"X"', register)

    def test_uppercase_two_scopes(self):
        """
        uppercase varnames are global so scopes don't apply, but we still make mappings to the same register in each scope
        """
        v = RecursiveRpnVisitor()
        v.var_to_reg('X')
        v.scopes.push()
        self.assertEqual('"X"', v.var_to_reg('X'))

    def test_uppercase_three_scopes(self):
        v = RecursiveRpnVisitor()
        v.var_to_reg('X')
        v.scopes.push()
        v.var_to_reg('X')
        v.scopes.push()
        self.assertEqual('"X"', v.var_to_reg('X'))

