from test_base import BaseTest
from scope import Scopes, Scope
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class VarnameLowerTests(BaseTest):

    def test_lowercase_varname(self):
        scopes = Scopes()
        register = scopes.var_to_reg('x')
        self.assertEqual('00', register)

    def test_lowercase_varname_two(self):
        scopes = Scopes()
        register_x = scopes.var_to_reg('x')
        register_y = scopes.var_to_reg('y')
        self.assertEqual('00', register_x)
        self.assertEqual('01', register_y)

    def test_lowercase_varname_two_x(self):
        scopes = Scopes()
        register_x = scopes.var_to_reg('x')
        self.assertEqual('00', register_x)
        register_x = scopes.var_to_reg('x')
        self.assertEqual('00', register_x)

    def test_lowercase_varname_two_x_two_scopes(self):
        scopes = Scopes()
        register_x = scopes.var_to_reg('x')
        self.assertEqual('00', register_x)
        scopes.push()
        register_x = scopes.var_to_reg('x')
        self.assertEqual('01', register_x)

    def test_lowercase_varname_two_x_two_scopes_pop(self):
        scopes = Scopes()
        scopes.var_to_reg('x')
        scopes.push()
        scopes.var_to_reg('x')
        scopes.pop()
        register_x = scopes.var_to_reg('x')
        self.assertEqual('00', register_x)


class VarnameUpperTests(BaseTest):

    def test_uppercase_varname(self):
        scopes = Scopes()
        register = scopes.var_to_reg('X')
        self.assertEqual('"X"', register)

    def test_uppercase_lowercase_varname(self):
        scopes = Scopes()
        register = scopes.var_to_reg('X')
        self.assertEqual('"X"', register)
        register = scopes.var_to_reg('x')
        self.assertEqual('00', register)
        register = scopes.var_to_reg('X')
        self.assertEqual('"X"', register)

    def test_uppercase_two_scopes(self):
        """
        uppercase varnames are global so scopes don't apply, but we still make mappings to the same register in each scope
        """
        scopes = Scopes()
        scopes.var_to_reg('X')
        scopes.push()
        self.assertEqual('"X"', scopes.var_to_reg('X'))

    def test_uppercase_three_scopes(self):
        scopes = Scopes()
        scopes.var_to_reg('X')
        scopes.push()
        scopes.var_to_reg('X')
        scopes.push()
        self.assertEqual('"X"', scopes.var_to_reg('X'))

class RangeVarNames(BaseTest):
    # Track that certain variables have been used in for loop range expressions

    def test_not_range_index(self):
        scopes = Scopes()
        var_name = 'i'
        register = scopes.var_to_reg(var_name, is_range_index=False)
        self.assertEqual('00', register)
        self.assertFalse(scopes.is_range_index(var_name))

    def test_i(self):
        scopes = Scopes()
        var_name = 'i'
        register = scopes.var_to_reg(var_name, is_range_index=True)
        self.assertTrue(scopes.is_range_index(var_name))
