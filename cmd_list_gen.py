#coding:utf8
import csv
import pprint
import settings

data = {}
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

        supported = row[2]
        if supported == 'tocheck':
            supported = ''
            suggestion = 'being researched'
        elif supported == 'na':
            if "(Not programmable.)" in description:
                supported = "Not programmable"
                suggestion = ''
            else:
                supported = "N/A"
                suggestion = 'Not Applicable to Python or use built in Python facility'
        elif supported == 'noflow':
            supported = "No"
            suggestion = 'Use Python "if" statements instead'
        elif supported == 'noloop':
            supported = "No"
            suggestion = 'Use Python for...range() loops instead, or Python while loops'
        elif supported == 'noflag':
            supported = "No"
            suggestion = 'Use any normal variable to store boolean values, test with the Python "if" statements instead'
        elif supported == 'nostack':
            supported = "No"
            suggestion = 'Use Python variables'
        elif supported == 'nobool':
            supported = "No"
            suggestion = 'Use built in Python boolean operators instead e.g. not val or val2 and val3'
        elif supported == 'nomatrix':
            supported = "No"
            suggestion = 'Use Python matrix/list indexing and slicing syntax instead - read help for more info'
        elif supported == 'noregs':
            supported = "No"
            suggestion = 'Use Python variables instead, e.g. myar = 100, myvar += 1, var2 = myvar or even expressions like myvar *= var3/(2-1)'
        elif supported == 'alpha':
            supported = "No"
            suggestion = 'Use the alpha() function to build up strings in the alpha register, specifying literal strings of any length, and multiple variables. See help for more details'
        elif supported == 'remapped':
            supported = '✓ (renamed)'
            suggestion = f'Use {settings.RPN_CMD_TO_PYTHON_REPLACEMENT[cmd]}() instead.'
        elif supported == 'ok':
            supported = '✓'
            suggestion = ''
        else:
            supported = supported
            suggestion = ''


        entry = {
            'description': description,
            'num_arg_fragments': num_arg_fragments,
            'indirect_allowed': '(indirect allowed)' in description,
            'supported': supported,
            'suggestion': suggestion,
        }
        data[cmd] = entry

pprint.pprint(data)
# print(data)

with open('cmd_list.py', 'w') as f:
    f.write('cmd_list = \\\n')
    f.write(pprint.pformat(data))



