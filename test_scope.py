import unittest
from test_base import BaseTest
from scope import ScopeStack, Scope
import logging
from logger import config_log
import maya

log = logging.getLogger(__name__)
config_log(log)

class ScopeTests(BaseTest):

    def test_scope_easy(self):
        stack = ScopeStack()
        stack.push()
        stack.add_mapping('a', '00')

        self.assertEqual('00', stack.get_register('a'))
