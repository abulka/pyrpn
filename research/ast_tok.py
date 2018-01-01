# https://github.com/gristlabs/asttokens

import asttokens, ast
source = "Robot('blue').walk(steps=10*n)"
atok = asttokens.ASTTokens(source, parse=True)
