class RpnError(Exception):
    pass

def source_code_line_info(node):
    return f'line: {node.lineno}\n{node.first_token.line.strip()}'