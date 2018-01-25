"""
def dd1():
  FIX(0)
  CLLCD()
  draw_line(0, 0, 10, 10)
  draw_line(10, 10, 20, 5)
  draw_line(20, 5, 100, 16)
  draw_line(100, 16, 131, 1)

def draw_line(x0, y0, x1, y1):  # rpn: int
    dx = ABS(x1 - x0)
    dy = ABS(y1 - y0)
    if x0 < x1:
        sx = 1
    else:
        sx = -1
    if y0 < y1:
        sy = 1
    else:
        sy = -1
    err = dx - dy
    done = 0
    while not done:
        #alpha('pixel ', x0, ' ', y0)
        #PRA()
        PIXEL(y0, x0);  # note col, row not row, col
        #alpha('if ', x0, ' ', x1, ' ', y0, ' ', y1)
        #PRA()
        if (x0 == x1) and (y0 == y1):
            done = 1
        else:
            e2 = 2 * err
            if e2 > -dy:
                err = err - dy
                x0 = x0 + sx
            if e2 < dx:
                err = err + dx
                y0 = y0 + sy
"""
