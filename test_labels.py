from test_base import BaseTest
from scope import Scopes
from labels import FunctionLabels
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)

class FunctionLabelsTests(BaseTest):

    # Allocation of function labels A through J and a through e

    def test_function_label_allocation_1(self):
        labels = FunctionLabels()
        labels.add_function_mapping('func')
        self.assertEqual('A', labels.get_label('func'))

    def test_function_label_allocation_multiple(self):
        labels = FunctionLabels()
        labels.add_function_mapping('func')
        labels.add_function_mapping('func2')
        self.assertEqual('A', labels.get_label('func'))
        self.assertEqual('B', labels.get_label('func2'))

    def test_function_label_push_pop(self):
        # labels are global so scope push pop does not affect anything
        scopes = Scopes()
        labels = FunctionLabels()
        labels.add_function_mapping('func')
        scopes.push()
        self.assertEqual('A', labels.get_label('func'))
        scopes.pop()
        self.assertEqual('A', labels.get_label('func'))

    def test_function_multiple_mappings_refs_not_defs(self):
        # multiple labels created by references to labels, not defs
        labels = FunctionLabels()
        labels.add_function_mapping('func')
        self.assertEqual('A', labels.get_label('func'))
        labels.add_function_mapping('func')
        self.assertEqual('A', labels.get_label('func'))

    def test_function_multiple_mappings_refs_and_single_def(self):
        # multiple labels created by a mixture of references to labels, and one def
        labels = FunctionLabels()
        labels.add_function_mapping('func')
        self.assertEqual('A', labels.get_label('func'))
        labels.add_function_mapping('func')
        self.assertEqual('A', labels.get_label('func'))
        labels.add_function_mapping('func', called_from_def=True)
        self.assertEqual('A', labels.get_label('func'))

    def test_function_replace_mapping_cos_two_defs(self):
        # its only when there are two label calls from a def creation, that label is redefined
        labels = FunctionLabels()
        labels.add_function_mapping('func', called_from_def=True)
        self.assertEqual('A', labels.get_label('func'))
        labels.add_function_mapping('func', called_from_def=True)
        self.assertEqual('B', labels.get_label('func'))

    def test_function_replace_function_mapping_then_ref(self):
        labels = FunctionLabels()
        labels.add_function_mapping('func', called_from_def=True)
        self.assertEqual('A', labels.get_label('func'))
        labels.add_function_mapping('func', called_from_def=True)
        self.assertEqual('B', labels.get_label('func'))
        labels.add_function_mapping('func')
        self.assertEqual('B', labels.get_label('func'))
