"""

def dd1_draw_demo1():
  FIX(0)
  CLLCD()
  draw_line(0, 0, 10, 10)
  draw_line(10, 10, 20, 5)
  draw_line(20, 5, 100, 16)
  draw_line(100, 16, 131, 1)
  draw_rect(70, 4, 5, 5)
  fill_rect(18, 9, 12, 4)
  draw_circle(96, 8, 5)
  fill_circle(125, 10, 3)

def dd2_draw_demo():  # rpn: export
    FIX(0)
    CLLCD()

    XRES = 131
    YRES = 16

    # some pixels
    for i in range(1, XRES, 5):
        x = i
        PIXEL(x, YRES / 2)

    # some lines (note the quite likely 'Moire pattern')
    for i in range(1, XRES / 4, 2):
        x = i
        draw_line(0, 0, x, YRES)

    # some rectangles
    fromx = XRES / 4
    fromy = YRES / 2
    width = XRES / 4
    height = YRES / 4
    draw_rect(fromx, fromy, width, height)

    fromx = XRES / 4 + 10
    fromy = YRES / 2 + 4
    width = XRES / 4 - 20
    height = YRES / 4
    draw_rect(fromx, fromy, width, height)

    fromx = XRES / 8
    width = XRES / 4
    height = YRES / 4
    fill_rect(fromx, 1, width, height)

    # some circles
    for i in range(2, YRES / 2, 2):
        d = i
        draw_circle(3 * XRES / 4, 2 * YRES / 4, d)

    fill_circle(15 * XRES / 16, 2 * YRES / 4, YRES / 3)
    fill_circle(8 * XRES / 13, 3 * YRES / 4, YRES / 2)

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

def draw_circle(x0, y0, r):  # rpn: int
    x = r;
    y = 0;
    radiusError = 1 - x;

    while (x >= y):
        PRA('x= ', x, ' y= ', y, ' ', radiusError)
        PIXEL(-y + x0, -x + y0)  # top left
        PIXEL(y + x0, -x + y0)  # top right
        PIXEL(-x + x0, -y + y0)  # upper middle left
        PIXEL(x + x0, -y + y0)  # upper middle right
        PIXEL(-x + x0, y + y0)  # lower middle left
        PIXEL(x + x0, y + y0)  # lower middle right
        PIXEL(-y + x0, x + y0)  # bottom left
        PIXEL(y + x0, x + y0)  # bottom right

        y += 1;
        if (radiusError < 0):
            radiusError += 2 * y + 1
        else:
            x -= 1
            radiusError += 2 * (y - x + 1)

def fill_circle(x0, y0, r):
    x = r
    y = 0
    radiusError = 1 - x

    while (x >= y):
        fromx = -y + x0
        fromy = -x + y0
        tox = y + x0
        toy = -x + y0
        draw_line(fromx, fromy, tox, toy)  # top

        fromx = -x + x0
        fromy = -y + y0
        tox = x + x0
        toy = -y + y0
        draw_line(fromx, fromy, tox, toy)  # upper middle

        fromx = -x + x0
        fromy = y + y0
        tox = x + x0
        toy = y + y0
        draw_line(fromx, fromy, tox, toy)  # lower middle

        fromx = -y + x0
        fromy = x + y0
        tox = y + x0
        toy = x + y0
        draw_line(fromx, fromy, tox, toy)  # bottom

        y += 1
        if radiusError < 0:
            radiusError += 2 * y + 1
        else:
            x -= 1
            radiusError += 2 * (y - x + 1)


"""


"""
# Test code for arrays and dictionaries
def t1():
  A = {1:11,5:22}
  passert(A[5] == 22)
  passert(A[1] == 11)
  A[1] = 88
  passert(A[1] == 88)
  A[6] = 66
  passert(A[6] == 66)
  passert(A[5] == 22)
  passert(A[1] == 88)
  #PROMPT(A[1])
  #PROMPT(A[222])
  B = [1,2,3]
  B.append(4)
  passert(B[0] == 1)
  passert(B[1] == 2)
  passert(B[2] == 3)
  passert(B[3] == 4)
  B[2] = 333
  passert(B[2] == 333)
  print("all tests pass")
  
"""