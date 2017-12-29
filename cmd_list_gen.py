#coding:utf8
import csv
import pprint

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

        entry = {
            'description': description,
            'num_arg_fragments': num_arg_fragments,
            'indirect_allowed': '(indirect allowed)' in description,
        }
        data[cmd] = entry

pprint.pprint(data)
# print(data)

with open('cmd_list.py', 'w') as f:
    f.write('cmd_list = \\\n')
    f.write(pprint.pformat(data))



