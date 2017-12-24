from attr import attrs, attrib, Factory
from logger import config_log
import logging

log = logging.getLogger(__name__)
config_log(log)


@attrs
class Line(object):
    text = attrib(default='')
    lineno = attrib(default=0)


@attrs
class Program(object):
    lines = attrib(default=Factory(list))  # cannot just have [] because same [] gets re-used in new instances of 'Program'
    next_lineno = attrib(default=0)

    def _add_line(self, line):
        self._incr_line(line)
        self.lines.append(line)

    def _incr_line(self, line):
        line.lineno = self.next_lineno
        self.next_lineno += 1

    def LBL(self, node):
        line = Line(text=f'LBL "{node.name.upper()[-7:]}"')
        self._add_line(line)

    def STO(self, where, aug_assign=''):
        line = Line(text=f'STO{aug_assign} "{where.upper()[-7:]}"')
        self._add_line(line)

    def RCL(self, var_name):
        line = Line(text=f'RCL "{var_name.upper()[-7:]}"')
        self._add_line(line)

    def insert(self, text):
        line = Line(text=str(text))
        self._add_line(line)

    def assign(self, var_name, val, val_is_var=False, aug_assign=''):
        if val_is_var:
            print('val', val)
            self.insert('RCL 00')  # TODO need to look up the register associated with 'val'
        else:
            self.insert(val)
        if aug_assign:
            self.STO(var_name, aug_assign=aug_assign)
        else:
            self.STO(var_name)
        self.insert('RDN')

    def finish(self):
        self.insert('RTN')

    def dump(self):
        log.debug(f"{'='*20} | (Program lines dump)")
        for line in self.lines:
            log.debug(f'{line.lineno:02d} {line.text}')
        log.debug(f"{'='*20} |")