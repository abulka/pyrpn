# based on https://www.reddit.com/r/learnpython/comments/1uufki/tail_f_equivalent_in_python/

import time
from escpos import *
import io
import binascii

Epson = printer.Usb(0x04b8,0x0e03)

def tail(fn, sleep=0.1):
    f = open(fn)
    f.seek(0, io.SEEK_END)
    while True:
        l = f.readline()
        if l:
            yield l
        else:
            time.sleep(sleep)

def dump(line):
    b = bytearray(line, encoding='utf8')
    print(binascii.hexlify(b))

for line in tail("/Users/Andy/Dropbox/42S 50g and Prime calcs/free42_andy.log.txt"):
    #print(line, end='')
    dump(line)
    b = bytearray(line, encoding='utf8')
    b = b.replace(b'\xe2\x96\xb8', b'\x66')
    line = b.decode(encoding='utf8')
    Epson.text(line)


"""
30 31 e2 96 b8 4c 42 4c 20 22 41 42 43 22 0a
0  1           L  B  L    "  A  B  C  "  LF

so 

e2 96 b8

is the ▸ character

>>> x='▸'
>>> b = bytearray(x, encoding='utf8')
>>> b
bytearray(b'\xe2\x96\xb8')

"""
