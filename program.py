from attr import attrs, attrib, Factory
from logger import config_log
import logging

log = logging.getLogger(__name__)
config_log(log)


@attrs
class Line(object):
    text = attrib(default='')
    lineno = attrib(default=0)
    comment = attrib(default='')


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
        line = Line(text=f'LBL "{node.name[:7]}"')
        self._add_line(line)

    def STO(self, to_register, aug_assign=''):
        line = Line(text=f'STO{aug_assign} {to_register}')
        self._add_line(line)

    def RCL(self, from_register, aug_assign=''):
        line = Line(text=f'RCL{aug_assign} {from_register}')
        self._add_line(line)

    def insert(self, text, comment=''):
        line = Line(text=str(text), comment=comment)
        self._add_line(line)

    def assign(self, to_register, val, val_type, aug_assign=''):
        # handling special stack register operations is a nightmare

        def is_stack_x_or_y(register):
            return register in ['ST X', 'ST Y']

        if val_type == 'literal':
            self.insert(val)
        else:
            from_register = val
            if is_stack_x_or_y(to_register) and is_stack_x_or_y(to_register):
                pass  # redundant to recall either x and y because they are there already
            else:
                self.insert(f'RCL {from_register}')  # val might be "X" or 00

        if aug_assign:
            if to_register == 'ST X':
                log.info('X SITUATION (aug)')
                self.insert(aug_assign)
            elif to_register == 'ST Y':
                log.info('Y SITUATION (aug)')
                self.insert('SWAP')
                self.insert(aug_assign)
            else:
                self.STO(to_register, aug_assign=aug_assign)
        else:
            # not sure how to handle these cos
            # pushing values onto the stack affects the stack positions!
            if to_register == 'ST X':
                log.info('X SITUATION - yikes')
                pass
            elif to_register == 'ST Y':
                log.info('Y SITUATION - yikes')
                pass
            else:
                self.STO(to_register)

        if 'ST' not in to_register:
            self.insert('RDN')

    def finish(self):
        self.insert('RTN')

    def dump(self, comments=False):
        log.debug(f"{'='*20} | (Program lines dump)")
        for line in self.lines:
            comment = f'  // {line.comment}' if comments and line.comment else ''
            log.debug(f'{line.lineno:02d} {line.text}{comment}')
        log.debug(f"{'='*20} |")