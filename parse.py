import asttokens
from rpn import RecursiveRpnVisitor

def parse(text):
    atok = asttokens.ASTTokens(text, parse=True)
    tree = atok.tree
    # self.dump_ast()
    visitor = RecursiveRpnVisitor()
    visitor.atok = atok
    visitor.visit(tree)
    # visitor.program.dump()
    return visitor.program