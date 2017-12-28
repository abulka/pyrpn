from attr import attrs, attrib, Factory
import logging
from logger import config_log

log = logging.getLogger(__name__)
config_log(log)


@attrs
class FunctionLabels(object):
    # Function to label mapping support - not scoped

    label_data = attrib(default=Factory(dict))  # function name to label name
    next_lbl = attrib(default=0)  # indexes into A-J, a-e
    labels_created_by_def = attrib(default=Factory(list))

    def func_to_lbl(self, func_name, label=None, called_from_def=False):
        """
        Maps a function name to a label.  If the mapping already exists, the label is
        returned. This method can be called from either a function call/reference or
        a function creation situation.

        :param func_name: function name e.f. 'main' or 'add'
        :param label: force use this label name
        :param called_from_def: If 'called_from_def' is true then the second (or greater) time a mapping
                is made for a function name, the label is incremented to avoid clashes.
        :return: label e.g. 'A'
        """
        if self.has_function_mapping(func_name) and called_from_def and func_name in self.labels_created_by_def:
            del self.label_data[func_name]
        if self.has_function_mapping(func_name):
            if called_from_def:
                self.labels_created_by_def.append(func_name)
            return self.get_label(func_name)

        if label == None:
            label = list('ABCDEFGHIJabcdefghij')[self.next_lbl]
            self.next_lbl += 1
        self.label_data[func_name] = label
        if called_from_def and func_name not in self.labels_created_by_def:
            self.labels_created_by_def.append(func_name)
        return label

    def has_function_mapping(self, func_name):
        return func_name in self.label_data

    def get_label(self, func_name):
        return self.label_data[func_name]

    @property
    def label_data_empty(self):
        return len(self.label_data) == 0

    # Util

    def dump(self):
        result_labels = '-' if self.label_data_empty else str(self.label_data)
        return ' [' + result_labels + ']'

