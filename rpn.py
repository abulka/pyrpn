import ast
import astunparse
from attr import attrs, attrib, Factory

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
        print('='*100)
        for line in self.lines:
            print(f'{line.lineno:02d} {line.text}')


class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.program = Program()
        self.var_names = []
        self.params = []
        self.aug_assign = ''
        # self.next_label = 0
        # self.next_variable = 0

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    def reset(self):
        self.var_names = []
        self.params = []
        self.aug_assign = ''

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        print(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        print('END ASSIGN', self.var_names, self.params)
        self.program.assign(self.var_names[0], self.params[0])
        self.reset()

    def visit_AugAssign(self,node):
        """ visit a AugAssign e.g. += node and visits it recursively"""
        print(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        print('END AUG ASSIGN', self.var_names, self.params)
        if self.params:
            # we are assigning a literal
            self.program.assign(self.var_names[0], self.params[0], aug_assign=self.aug_assign)
        elif len(self.var_names) >= 2:
            # we are assigning a variable to another variable
            self.program.assign(self.var_names[0], self.var_names[1], val_is_var=True, aug_assign=self.aug_assign)
        else:
            raise RuntimeError("yeah dunno what assignment to make")
        self.reset()

    def visit_Return(self,node):
        print(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        print('END RETURN', self.var_names, self.params)
        self.program.RCL(self.var_names[0])

    @recursive
    def visit_Add(self,node):
        print(type(node).__name__)
        self.aug_assign = '+'

    @recursive
    def visit_BinOp(self, node):
        """ visit a BinOp node and visits it recursively"""
        print(type(node).__name__)

    def visit_Call(self,node):
        """
        Function call. The child nodes include the function name and the args.  do not use recursive decorator because
        we want more control, and we need to know the end of the calls so that we can generate rpn and clear params

        On the call
            self.visit(node.func)  # will emit the function name
        If we were using the decorator no need to visit explicitly as the recursive decorator will do it for us.
        if no decorator then don't do this call either !!, because visiting the children will do it for us.
        """
        print(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        print('END CALL', self.var_names, self.params)
        if 'range' in self.var_names:
            self.program.insert(self.params[0])
            self.program.insert(self.params[1])
        self.reset()

    @recursive
    def visit_Lambda(self,node):
        """ visit a Function node """
        print(type(node).__name__)

    @recursive
    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""
        print(type(node).__name__)
        self.program.LBL(node)

    @recursive
    def visit_Module(self,node):
        """ visit a Module node and the visits recursively"""
        pass

    def generic_visit(self,node):
        print(f'skipping {node}')
        if getattr(node, 'name', ''):
            print(f'name {node.name}')

    def visit_Name(self, node):
        print("visit_Name %s" % node.id)
        self.var_names.append(node.id)

    def visit_Num(self, node):
        print(f'Num {node.n}')
        self.push_param(str(node.n))  # always a string

    def push_param(self, val):
        self.params.append(val)

    def write(self, s):
        print(s)

    def visit_For(self, node):
        # self.newline(node)
        self.write('for ')
        self.visit(node.target)
        self.write(' in ')
        self.visit(node.iter)
        self.write(':')
        self.program.insert(1000)
        self.program.insert('/')
        self.program.insert('+')
        self.program.insert('STO 00')
        self.program.insert('LBL 00')
        self.body_or_else(node)
        self.write('END FOR body or else')
        self.write('END FOR ')
        self.program.insert('ISG 00')
        self.program.insert('GTO 00')

    def body(self, statements):
        # self.new_line = True
        # self.indentation += 1
        for stmt in statements:
            self.visit(stmt)
        # self.indentation -= 1

    def body_or_else(self, node):
        self.body(node.body)
        if node.orelse:
            # self.newline()
            self.write('else:')
            self.body(node.orelse)

