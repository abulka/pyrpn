def de_comment(s):
    """
    Strips comments from RPN code
    If an entire line is commented, it is removed

    Note:
        Allow only first line and last lines to be blank (cos tests have expected strings
        in triple quoted string with blank first line), the rest are removed

    :param s: RPN code string newline separated
    :return: RPN code string newline separated
    """
    lines = s.split('\n')
    result = []
    immune = [0, len(lines) - 1]  # first and last allow to be blank
    for i, line in enumerate(lines):
        comment_pos = line.find('//')
        if comment_pos != -1:
            clean_line = line[0:comment_pos].strip()
            if clean_line == '' and not i in immune:
                continue
            result.append(clean_line)
        elif line.strip() == '' and not i in immune:
            continue
        else:
            result.append(line.strip())
    return '\n'.join(result)