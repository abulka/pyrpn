from escpos import *


Epson = printer.Usb(0x04b8,0x0e03)
for i in range(1,10):
    Epson.text(f"Hello World {i}\n")

Epson.barcode
Epson.barcode('1324354657687','EAN13',64,2,'','')
Epson.cut()

