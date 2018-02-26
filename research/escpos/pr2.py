from escpos import *
# from escpos.codepages import CodePageManager
#
# mgr = CodePageManager
# s = mgr.get_all()
# print(s)
#
#
# p = printer.Usb(0x04b8,0x0e03)
# text = "£\n"
# text2 = '01▸LBL "main"'
# p.charcode("MULTILINGUAL")
# p.text(text2)
# p.text(text)
#
#
# # Some software barcodes
# p.soft_barcode('code128', 'Hello')
# p.soft_barcode('code39', '123456')

# p = printer.Usb(0x04b8,0x0e03, profile="POS-5890")
#
# p.soft_barcode('code128', 'Hello')
# p.soft_barcode('code39', '123456')


from escpos.printer import Usb


# # Adapt to your needs
# #p = Usb(0x0416, 0x5011, profile="POS-5890")
# p = Usb(0x04b8,0x0e03, profile="POS-5890")
#
# # Some software barcodes
# p.soft_barcode('code128', 'Hello')
# p.soft_barcode('code39', '123456')
#


#
# import sys
#
# from escpos.printer import Usb
#
#
# def usage():
#     print("usage: qr_code.py <content>")
#
#
# if __name__ == '__main__':
#     if len(sys.argv) != 2:
#         usage()
#         sys.exit(1)
#
#     content = sys.argv[1]
#
#     # Adapt to your needs
#     # p = Usb(0x0416, 0x5011, profile="POS-5890")
#     p = Usb(0x04b8,0x0e03, profile="POS-5890")
#     p.qr(content, center=True)
#


"""Prints code page tables.
"""

# from __future__ import print_function

import six
import sys

from escpos import printer
from escpos.constants import CODEPAGE_CHANGE, ESC, CTL_LF, CTL_FF, CTL_CR, CTL_HT, CTL_VT


def main():
    dummy = printer.Dummy()
    # dummy = Usb(0x04b8,0x0e03)

    dummy.hw('init')

    # enter_user(dummy)

    if True:
        for codepage in sys.argv[1:] or ['USA']:
            dummy.set(height=2, width=2)
            dummy._raw(codepage + "\n\n\n")
            print_codepage(dummy, codepage)
            dummy._raw("\n\n")
    # dummy.cut()

    # print(dummy.output)

    # ANDY modification
    arr = bytearray()
    for item in dummy._output_list:
        if type(item) == bytes:
            arr.extend(item)
        elif type(item) == str:
            # b = str.encode(item)  # but do I really want utf8 here?
            b = str.encode(item, encoding='ISO-8859-1')
            arr.extend(b)
    print(bytes(arr))



def print_codepage(printer, codepage):
    if codepage.isdigit():
        codepage = int(codepage)
        printer._raw(CODEPAGE_CHANGE + six.int2byte(codepage))
        printer._raw("after")
    else:
        printer.charcode(codepage)

    sep = ""

    # Table header
    printer.set(font='b')
    printer._raw("  {}\n".format(sep.join(map(lambda s: hex(s)[2:], range(0, 16)))))
    printer.set()

    # The table
    for x in range(0, 16):
        # First column
        printer.set(font='b')
        printer._raw("{} ".format(hex(x)[2:]))
        printer.set()

        for y in range(0, 16):
            byte = six.int2byte(x * 16 + y)

            if byte in (ESC, CTL_LF, CTL_FF, CTL_CR, CTL_HT, CTL_VT):
                byte = ' '

            printer._raw(byte)
            printer._raw(sep)
        printer._raw('\n')


def enter_user(printer):
    bs = b'0x1D0x280x450x030x000x010x490x4E'
    printer._raw(bs)

def exit_user(printer):
    # 1D		28		45		04		00		02		4F		55		54
    bs = b'0x1D0x280x450x040x000x020x4F0x550x54'
    printer._raw(bs)

if __name__ == '__main__':
    main()

