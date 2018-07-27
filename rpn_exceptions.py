class RpnError(Exception):
    pass

def source_code_line_info(node):
    if not hasattr(node, 'lineno'):
        return f'line unknown - (missing lineno from node object):\n{node.first_token.line.strip()}'
    else:
        return f'line: {node.lineno}\n{node.first_token.line.strip()}'