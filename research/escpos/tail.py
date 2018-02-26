# based on https://www.reddit.com/r/learnpython/comments/1uufki/tail_f_equivalent_in_python/

import time

def tail(fn, sleep=0.1):
    f = open(fn)
    while True:
        l = f.readline()
        if l:
            yield l
        else:
            time.sleep(sleep)

for line in tail("/Users/Andy/Dropbox/42S 50g and Prime calcs/free42_andy.log.txt"):
    print(line, end='')


