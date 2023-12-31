from attr import attrs, attrib, Factory
from logger import config_log
import logging
from rpn_lib import RpnTemplates
from rpn_exceptions import RpnError
import settings

log = logging.getLogger(__name__)
config_log(log)


@attrs
class Line:
    text = attrib(default='')
    lineno = attrib(default=0)
    comment = attrib(default='')
    type_ = attrib(default='')


@attrs
class BaseRpnProgram:
    lines = attrib(default=Factory(list))  # cannot just have [] because same [] gets re-used in new instances of 'Program'
    next_lineno = attrib(default=1)

    def _add_line(self, line):
        self._incr_line(line)
        self.lines.append(line)

    def _incr_line(self, line):
        line.lineno = self.next_lineno
        self.next_lineno += 1

    def insert(self, text, comment='', type_=''):
        comment = self.remove_html(comment)
        line = Line(text=str(text), comment=comment, type_=type_)
        self._add_line(line)
        self.insert_logging(line)

    def remove_html(self, comment):
        comment = comment.replace('<del>', '')
        comment = comment.replace('</del>', '')
        return comment

    def insert_logging(self, line):
        # debug
        info = f'    [ {line.type_} ]' if line.type_ else '' + \
               f'    // {line.comment}' if line.comment else ''
        log.debug(f'{line.text}{info}')

    def insert_raw_lines(self, text):
        # inserts rpn text, removes any blank lines, preserves comments
        for line in text.split('\n'):
            comment_pos = line.find('//')
            if comment_pos != -1:
                clean_line = line[0:comment_pos].strip()
                if clean_line == '':
                    continue
                comment = line[comment_pos + 2:].strip()
                self.insert(clean_line, comment)
            elif line.strip() == '':
                continue
            else:
                self.insert(line.strip())

    def lines_to_str(self, comments=False, linenos=False):
        result = []
        for line in self.lines:
            comment = f'  // {line.comment}' if comments and line.comment else ''
            lineno = f'{line.lineno:02d} ' if linenos else ''
            rpn = f'{line.text:14s}' if comment else line.text
            result.append(f'{lineno}{rpn}{comment}')
        return '\n'.join(result)

    # logging

    def dump(self, comments=False, linenos=False):
        log.debug(f"{'='*20} | (Program lines dump)")
        log.debug(self.lines_to_str(comments, linenos))
        log.debug(f"{'='*20} |")


@attrs
class Program(BaseRpnProgram):
    rpn_templates = attrib(default=Factory(RpnTemplates))

    @property
    def last_line(self):
        return self.lines[-1]

    def is_previous_line(self, type_='string'):
        return self.last_line.type_ == type_

    def insert_sto(self, register, comment='', type_=''):
        def need_rcl_zlist():
            # Special cases, its a matrix command that returns a normal number, or a RCLEL which returns normal number/string
            if 'pMxLen' in self.last_line.text or \
               'RCLEL' in self.last_line.text:
                return False
            # A bit of a guess - list/dict/matrix related
            return \
                'LIST' in self.last_line.text or \
                'STOEL' in self.last_line.text or \
                'pMxPrep' in self.last_line.text

        if 'empty' in self.last_line.type_:
            self.insert('0')  # signifies an empty list, since empty matrices are not possible
        elif need_rcl_zlist():
            self.insert('RCL "ZLIST"')

        cmd = 'ASTO' if self.is_previous_line('string') else 'STO'
        self.insert(f'{cmd} {register}', comment=comment, type_=type_)

    def insert_xeq(self, func_name, comment='', type_=''):
        if func_name in settings.PYLIB_INSERTABLE_WHEN_ORIGINAL_REPLACED.keys():
            comment = settings.PYLIB_INSERTABLE_WHEN_ORIGINAL_REPLACED[func_name]['description']
        self.insert(f'XEQ "{func_name}"', comment=comment, type_=type_)

    @property
    def user_insertable_rpn_functions(self):
        return settings.PYLIB_INSERTABLE_WHEN_ORIGINAL_REPLACED.keys()

    def emit_needed_rpn_templates(self, as_local_labels=True):
        self.insert('LBL "PyLIB"', comment='PyRPN Support Library of')
        self.insert('"-Utility Funcs-"')
        self.insert('RTN', comment='---------------------------')

        self.rpn_templates.embedded = as_local_labels

        if self.rpn_templates.need_all_templates:
            self.inject_dependencies(sorted(self.rpn_templates.template_names))
        else:
            # Supersedes any tracking - we just scan the lines repeatedly...
            dependencies = set()
            while True:
                new_dependencies = self.find_dependencies() - dependencies
                log.debug(f'new rpnlib function dependencies {new_dependencies}' if new_dependencies else 'no more dependencies')
                self.inject_dependencies(new_dependencies)
                dependencies = dependencies | new_dependencies  # combine
                if not new_dependencies:
                    break

        if as_local_labels:
            self.convert_to_local_labels()

    def inject_dependencies(self, templates_needed):
        for template in sorted(templates_needed):
            text = getattr(self.rpn_templates, template)  # look up the field dynamically
            log.debug(f'inserting rpn template {template}')
            self.insert_raw_lines(text)

    def find_dependencies(self):
        # Scan all the needed library functions for their dependencies - all XEQ calls need to be recorded into a set
        labels_called = set()
        for line in self.lines:
            if 'XEQ "' in line.text or 'GTO "' in line.text:
                func_name = self.extract_func_name(line.text)
                if func_name in ('LIST+', 'LIST-', 'CLIST'):
                    func_name = 'pList'
                elif func_name not in self.rpn_templates.template_names:
                    # log.debug(f'skipping dependency on {func_name}')
                    continue
                labels_called.add(func_name)
        return labels_called

    def extract_func_name(self, s):
        i = s.find('"')
        s = s[i + 1:]
        i = s.find('"')
        s = s[:i]
        return s

    def convert_to_local_labels(self):
        """
        Scan lines for labels and calls to Py Rpn Library and replace them with local labels
        """
        def replace_with_local_label(line, cmd):
            if line.text == 'LBL "PyLIB"':  # special case
                line.text = f'LBL {settings.LOCAL_LABEL_FOR_PyLIB}'
            else:
                text = line.text
                func_name = self.extract_func_name(text)
                if func_name in self.rpn_templates.template_names:
                    label = self.rpn_templates.local_alpha_labels[func_name]
                elif func_name == 'LIST+':
                    label = settings.LIST_PLUS
                elif func_name == 'LIST-':
                    label = settings.LIST_MINUS
                elif func_name == 'CLIST':
                    label = settings.LIST_CLIST
                else:
                    log.debug(f'skipped converting global label "{func_name}" to local')
                    return
                line.text = f'{cmd} {label}'
                log.debug(f'replaced global label "{func_name}" with local label {label}')

        for line in self.lines:
            if 'XEQ "' in line.text:
                replace_with_local_label(line, 'XEQ')
            elif 'LBL "' in line.text:
                replace_with_local_label(line, 'LBL')
            elif 'GTO "' in line.text:
                replace_with_local_label(line, 'GTO')
