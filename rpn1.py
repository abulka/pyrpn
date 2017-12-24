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
        line = Line(text=text)
        self.add_line(line)

    def add_rpn_assign(self, val):
        self.add_rpn_val(val)
        self.add_rpn_STO(self.assign_pending)
        self.add_rpn_rdn()

    def finish(self):
        self.add_generic('RTN')

    def dump(self):
        for line in self.lines:
            print(f'{line.lineno:02d} {line.text}')


class RecursiveRpnVisitor(ast.NodeVisitor):
    """ recursive visitor with RPN generating capability :-) """

    def __init__(self):
        self.program = Program()
        self.assign_pending = None
        self.for_loop = False
        self.next_label = 0
        self.next_variable = 0

    def recursive(func):
        """ decorator to make visitor work recursive """
        def wrapper(self,node):
            func(self,node)
            for child in ast.iter_child_nodes(node):
                self.visit(child)
        return wrapper

    @recursive
    def visit_Assign(self,node):
        """ visit a Assign node and visits it recursively"""
        print(type(node).__name__)

    @recursive
    def visit_BinOp(self, node):
        """ visit a BinOp node and visits it recursively"""
        print(type(node).__name__)

    @recursive
    def visit_Call(self,node):
        """ visit a Call node and visits it recursively"""
        print('call...', end=' ')
        print(type(node).__name__)
        # self.visit(node.func)  # no need to visit explicitly as the recursive decorator will do it for us

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
        # if self.for_loop and node.id == 'range':
        #     """
        #     00 1000  // for i in range....
        #     00 /
        #     00 1
        #     00 +
        #     00 STO 00  // counter
        #     00 LBL 00
        #     """
        #     self.out.append(f'{self.lineno:02d} {node.id}')
        #     self.increment_lineno()
        # else:
        #     self.assign_pending = node.id
        self.program.assign_pending = node.id

    def visit_Num(self, node):
        print(f'num {node.n}')
        self.program.add_rpn_assign(node.n)

    def write(self, s):
        print(s)

    def visit_For(self, node):
        # self.newline(node)
        self.for_loop = True
        self.write('for ')
        self.visit(node.target)
        self.write(' in ')
        self.visit(node.iter)
        self.write(':')
        self.body_or_else(node)
        self.for_loop = False
        self.write('END FOR ')

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

# ANDY

s1 = """
def looper(n):
    x = 100
    for i in range(1, n):
        print(i)
        x += n
    return x
"""


# visitor = RecursiveRpnVisitor()
# tree = ast.parse(s1)
# print(astunparse.dump(tree))
# visitor.visit(tree)
# print(visitor.out)

"""
expected

00 LBL "LOOPER"  // param n
01 100
02 STO "X"
00 RDN
00 1000  // for i in range....
00 /
00 1
00 +
00 STO 00  // counter
00 LBL 00
00 VIEW 00  // print(i)
00 RCL 00  // x += n
00 IP  // integer part
00 STO+ "X"
00 ISG 00
00 GTO 00
00 RCL "X"
00 RTN

 
"""