#coding:utf8
import csv
import pprint
import settings

data = {}

def extract(supported):
    # blah blah suggestion: blah blah
    # returns the first portion as info, the second portion as suggestion
    s = 'suggestion:'
    if s in supported:
        offset = supported.index(s)
        info = supported[0:offset-1]
        offset += len(s) + 1
        suggestion = supported[offset:]
    else:
        info = supported
        suggestion = ''
    return info, suggestion

def calc_num_params(params):
    if params:
        assert params[0] == '('
        assert params[-1] == ')'
        params_no_brackets = params[1:-1]
        num_params = len(params_no_brackets.split(',')) if params_no_brackets else -1
    else:
        num_params = 0
    return num_params

with open('cmd_list.csv', newline='') as csvfile:
    myreader = csv.reader(csvfile)
    for row in myreader:
        # print(', '.join(row))
        # print(row[0])
        # print(row[1])
        # print('------')
        # data[row[0].strip()] = row[1]
        cmd = row[0].strip()
        description = row[1]

        if 'Parameter:' in description:
            num_arg_fragments = 1
        elif 'Parameter 2:' in description:
            num_arg_fragments = 2
        else:
            num_arg_fragments = 0

        # if cmd == 'INPUT':
        #     import pdb;
        #     pdb.set_trace()

        supported = row[2]

        params = row[3].strip()
        num_params = calc_num_params(params)

        css_class = ''

        if supported == 'tocheck':
            supported = ''
            suggestion = 'being researched'
        elif supported[0:2] == 'na':
            if "Not programmable" in description:
                supported = "Not programmable"
                suggestion = ''
            else:
                info, suggestion = extract(supported)
                supported = "N/A"
                if not suggestion:
                    suggestion = 'Not applicable, please use native Python.'
        elif supported == 'noflow':
            supported = "No"
            suggestion = 'Use Python "if" statements instead. E.g. "if var1 == var2 or (var3 >= var4):"...'
        elif supported == 'noloop':
            supported = "No"
            suggestion = 'Use native Python for...range() or while... for looping.'
        elif supported == 'noflag':
            supported = "No"
            suggestion = 'Use any normal variable to store boolean values, test with the Python "if".'
        elif supported == 'nostack':
            supported = "No"
            suggestion = 'Use Python variables'
        elif supported == 'nobool':
            supported = "No"
            suggestion = 'Use built in Python boolean operators instead e.g. "not val or val2 and val3"'
        elif supported == 'nomatrix':
            supported = "No"
            suggestion = 'Use Python matrix/list indexing and slicing syntax.'
        elif supported == 'noregs':
            supported = "No"
            suggestion = 'Use Python variables instead, e.g. "myar = 100, myvar += 1, var2 = myvar" or even expressions like "myvar *= var3/(2-1)"'
        elif supported == 'alpha':
            supported = "No"
            suggestion = 'Use the alpha() function to build up strings in the alpha register, specifying literal strings of any length, and multiple variables. See help for more details'

        elif supported.startswith('renamed'):
            xtra_info, xtra_suggestion = extract(supported)
            supported = '✓ (renamed)'

            try:
                suggestion = f'<code>{settings.RPN_CMD_TO_PYTHON_RENAMED[cmd]}{params}</code>'
            except KeyError:
                suggestion = f'<code>{settings.RPN_TO_RPNLIB_SPECIAL[cmd]}{params}</code>'
            if xtra_suggestion:
                suggestion += '<br><br>' + xtra_suggestion

        elif supported[0:2] == 'No':
            info, suggestion = extract(supported)
            supported = 'No'
        elif supported[0:2] == 'ok':
            info, suggestion = extract(supported)
            supported = '✓'
        else:
            info, suggestion = extract(supported)
            supported = info

        # Highlight table lines with css
        if supported == "No":
            css_class = 'no'
        elif supported == "N/A":
            css_class = 'na'
        elif supported == "Not programmable":
            css_class = 'na'
            # css_class = 'not-programmable'
        elif suggestion == "being researched":
            css_class = 'tocheck'

        # Remove misleading fragments of text from descriptions
        if supported in ('No', 'N/A'):
            description = f'<del>{description}</del>'
        else:
            for phrase in (
                'skip the next program line',
                'skips the next program line',
                'execute the next program line',
                'executes the next program line',
                '(indirect allowed)',
            ):
                description = description.replace(phrase, f'<del>{phrase}</del>')


        entry = {
            'description': description,
            'num_arg_fragments': num_arg_fragments,
            'indirect_allowed': '(indirect allowed)' in description,
            'supported': supported,
            'suggestion': suggestion,
            'params': params,
            'num_params': num_params,
            'class': css_class,
        }
        data[cmd] = entry

# pprint.pprint(data)
# print(data)

with open('cmd_list.py', 'w') as f:
    f.write('cmd_list = \\\n')
    f.write(pprint.pformat(data))



