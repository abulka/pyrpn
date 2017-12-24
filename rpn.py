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
    assign_pending = attrib(default='')

    def add_line(self, line):
        self.incr_line(line)
        self.lines.append(line)

    def incr_line(self, line):
        line.lineno = self.next_lineno
        self.next_lineno += 1

    def add_rpn_label(self, node):
        line = Line(text=f'LBL "{node.name.upper()[-7:]}"')
        self.add_line(line)

    def add_rpn_val(self, val):
        line = Line(text=f'{val}')
        self.add_line(line)

    def add_rpn_STO(self, where):
        line = Line(text=f'STO "{where.upper()[-7:]}"')
        self.add_line(line)

    def add_rpn_rdn(self):
        self.add_generic('RDN')

    def add_generic(self, text):
        line = Line(text=str(text))
        self.add_line(line)

    def add_rpn_assign(self, val):
        self.add_rpn_val(val)
        self.add_rpn_STO(self.assign_pending)
        self.add_rpn_rdn()

    def finish(self):
        self.add_generic('RTN')

    def dump(self):
        print('='*100)
        for line in self.lines:
            print(f'{line.lineno:02d} {line.text}')


class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.program = Program()
        self.assign_pending = None
        self.next_label = 0
        self.next_variable = 0
        self.params = []

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        print(type(node).__name__)
        for child in ast.iter_child_nodes(node):
            self.visit(child)
        print('END ASSIGN', self.program.assign_pending, self.params)
        self.program.add_rpn_assign(self.params[0])
        self.params = []

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
        print('END CALL', self.program.assign_pending, self.params)
        if self.program.assign_pending == 'range':
            self.program.add_generic(self.params[0])
            self.program.add_generic(self.params[1])
        self.params = []

    @recursive
    def visit_Lambda(self,node):
        """ visit a Function node """
        print(type(node).__name__)

    @recursive
    def visit_FunctionDef(self,node):
        """ visit a Function node and visits it recursively"""
        print(type(node).__name__)
        self.program.add_rpn_label(node)

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
        self.program.assign_pending = node.id

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
        self.program.add_generic(1000)
        self.program.add_generic('/')
        self.program.add_generic('+')
        self.program.add_generic('STO 00')
        self.program.add_generic('LBL 00')
        self.body_or_else(node)
        self.write('END FOR body or else')
        self.write('END FOR ')
        self.program.add_generic('ISG 00')
        self.program.add_generic('GTO 00')

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

