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

    def insert(self, text, comment=''):
        line = Line(text=str(text), comment=comment)
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
                self.insert(line)

    def lines_to_str(self, comments=False, linenos=False):
        result = []
        for line in self.lines:
            comment = f'  // {line.comment}' if comments and line.comment else ''
            lineno = f'{line.lineno:02d} ' if linenos else ''
            result.append(f'{lineno}{line.text}{comment}')
        return '\n'.join(result)

    # logging

    def dump(self, comments=False, linenos=False):
        log.debug(f"{'='*20} | (Program lines dump)")
        log.debug(self.lines_to_str(comments, linenos))
        log.debug(f"{'='*20} |")

