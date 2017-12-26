def de_comment(s):
    """
    Strips comments from RPN code
    If an entire line is commented, it is removed

    Note:
        Allow only first line to be blank (cos tests have expected strings
        in triple quoted string with blank first line), the rest are removed

    :param s: RPN code string newline separated
    :return: RPN code string newline separated
    """
    result = []
    for i, line in enumerate(s.split('\n')):
        comment_pos = line.find('//')
        if comment_pos != -1:
            clean_line = line[0:comment_pos].strip()
            if clean_line == '' and i > 0:
                continue
            result.append(clean_line)
        else:
            result.append(line)
    return '\n'.join(result)