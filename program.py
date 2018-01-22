from attr import attrs, attrib, Factory
from logger import config_log
import logging
from rpn_templates import RpnTemplates
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
    next_lineno = attrib(default=0)

    def _add_line(self, line):
        self._incr_line(line)
        self.lines.append(line)

    def _incr_line(self, line):
        line.lineno = self.next_lineno
        self.next_lineno += 1

    def insert(self, text, comment='', type_=''):
        line = Line(text=str(text), comment=comment, type_=type_)
        self._add_line(line)
        log.debug(line.text)

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
    def user_insertable_pyrpn_cmds(self):
        return self.rpn_templates.get_user_insertable_pyrpn_cmds().keys()

    def is_previous_line(self, type_='string'):
        return self.lines[-1].type_ == type_

    def insert_sto(self, func_name, comment=''):
        cmd = 'ASTO' if self.is_previous_line('string') else 'STO'
        self.insert(f'{cmd} {func_name}', comment=comment)

    def insert_xeq(self, func_name, comment=''):
        # insert global function call
        if func_name in self.rpn_templates.template_names:
            self.rpn_templates.need_template(func_name)
        if func_name in self.user_insertable_pyrpn_cmds:
            # YUK
            comment = self.rpn_templates.get_user_insertable_pyrpn_cmds()[func_name]['description']
        self.insert(f'XEQ "{func_name}"', comment=comment)

    def emit_needed_rpn_templates(self, as_local_labels=True):
        if not self.rpn_templates.needed_templates:
            return

        templates_needed = set(self.rpn_templates.needed_templates)
        templates_who_need_PyBool = {'p2Bool'}
        templates_who_need_pErrRange = {'pISG'}
        templates_who_need_PyDFTB = {'pEQ', 'pGT', 'pGTE', 'pLT', 'pLTE', 'pNEQ'}

        # Add any dependent templates, using set technology
        if templates_who_need_PyBool & templates_needed:
            templates_needed.add('pBool')
        if templates_who_need_PyDFTB & templates_needed:
            templates_needed.add('_PyDFTB')
        if templates_who_need_pErrRange & templates_needed:
            templates_needed.add('pErrRange')

        self.insert('LBL "PyLIB"', comment='PyRPN Support Library of')
        self.insert('"-Utility Funcs-"')
        self.insert('RTN', comment='---------------------------')

        for template in templates_needed:
            text = getattr(self.rpn_templates, template)  # look up the field dynamically
            self.insert_raw_lines(text)
            log.debug(f'inserting rpn template {template}')

        if as_local_labels:
            self.convert_to_local_labels()

    def convert_to_local_labels(self):
        """
        Scan lines for labels and calls to Py Rpn Library and replace them with local labels
        """
        def extract_func_name(s):
            i = s.find('"')
            s = s[i+1:]
            i = s.find('"')
            s = s[:i]
            return s

        def replace_with_local_label(line, cmd):
            if line.text == 'LBL "PyLIB"':  # special case
                line.text = f'LBL {settings.LOCAL_LABEL_FOR_PyLIB}'
            else:
                text = line.text
                func_name = extract_func_name(text)
                if func_name in self.rpn_templates.template_names:
                    label = self.rpn_templates.local_alpha_labels[func_name]
                    line.text = f'{cmd} {label}'
                    log.debug(f'replaced global label "{func_name}" with local label {label}')

        for line in self.lines:
            if 'XEQ "' in line.text:
                replace_with_local_label(line, 'XEQ')
            elif 'LBL "' in line.text:
                replace_with_local_label(line, 'LBL')
