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
        stack.add_mapping('a', '00')
        self.assertRaises(KeyError, stack.get_register, 'a')
