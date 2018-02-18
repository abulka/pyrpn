from attr import attrs, attrib, Factory
import logging
from logger import config_log
import settings

log = logging.getLogger(__name__)
config_log(log)


@attrs
class FunctionLabels(object):
    # Function to label mapping support - not scoped

    label_data = attrib(default=Factory(dict))  # function name to label name
    next_lbl = attrib(default=0)  # indexes into A-J, a-e
    labels_created_by_def = attrib(default=Factory(list))

    def func_to_lbl(self, func_name, label=None, are_defining_a_def=False):
        """
        Maps a function name to a label.  If the mapping already exists, the label is
        returned. This method can be called from either a function call/reference or
        a function creation situation.

        Deprecated: If 'are_defining_a_def' is true twice, then the label is deleted and incremented before the
          second allocation. This was an attempt to allow multiple functions with the same name, in different scopes.
          Turns out this was too complex re forward references - easier to ban any function duplication,
          even if they were in different scopes and usually allowed by Python.

        :param func_name: function name e.g. 'main' or 'add'
        :param label: force use this label name
        :param are_defining_a_def: the label is needed in the process of building a def function
        :return: local label e.g. 'A' in range A-J, a-e
        """
        if self.has_function_mapping(func_name):
            if are_defining_a_def:
                self.labels_created_by_def.append(func_name)
            return self.get_label(func_name)

        if label == None:
            label = list(settings.USER_DEF_LABELS)[self.next_lbl]
            self.next_lbl += 1
        self.label_data[func_name] = label
        if are_defining_a_def and func_name not in self.labels_created_by_def:
            self.labels_created_by_def.append(func_name)
        return label

    def has_function_mapping(self, func_name):
        return func_name in self.label_data

    def get_label(self, func_name):
        return self.label_data[func_name]

    @property
    def label_data_empty(self):
        return len(self.label_data) == 0

    def is_global_def(self, func_name):
        return '"' in self.get_label(func_name)  # if its got a " around the label

    # Util

    def dump(self):
        result_labels = '-' if self.label_data_empty else str(self.label_data)
        return ' [' + result_labels + ']'

