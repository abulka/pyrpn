"""
def dd1():
  FIX(0)
  CLLCD()
  draw_line(0, 0, 10, 10)
  draw_line(10, 10, 20, 5)
  draw_line(20, 5, 100, 16)
  draw_line(100, 16, 131, 1)
  draw_rect(70, 4, 5, 5)
  fill_rect(18, 9, 12, 4)

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
        PIXEL(x0, y0)
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

# (x0, y0) = left top corner coordinates
# w = width and h = height
def draw_rect(x0, y0, w, h):  # rpn: int
  #PRA('draw_rect', x0, y0, w, h);
  y1 = y0 + h
  draw_line(x0, y0, x0 + w, y0)  # top
  draw_line(x0, y0, x0, y1)  # left
  draw_line(x0, y0 + h, x0 + w, y1)  # bottom
  draw_line(x0 + w, y0, x0 + w, y1)  # right

def fill_rect(x0, y0, w, h):  # rpn: int
  #for (y = 0; y < h; y++):  # TODO make any var work in a for loop
  for i in range(h):  # TODO make any var work in a for loop
    y = i
    y1 = y0 + y
    draw_line(x0, y0 + y, x0 + w, y1)

"""
