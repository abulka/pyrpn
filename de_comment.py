def de_comment(s):
    result = []
    for line in s.split('\n'):
        comment_pos = line.find('//')
        if comment_pos != -1:
            clean_line = line[0:comment_pos].strip()
            result.append(clean_line)
        else:
            result.append(line)
    return '\n'.join(result)