import thumby 
import random
from framebuf import FrameBuffer, MONO_HMSB, MONO_VLSB, MONO_HLSB
import time

# simulate 1D cellular automata by Stephen Wolfram
# http://mathworld.wolfram.com/ElementaryCellularAutomaton.html

simulate = False
buf = bytearray()
cells = []
blinks = 0
rule = 30
fbuffer = FrameBuffer(thumby.display.display.buffer, 72, 40, MONO_VLSB) # create thumby buffer
old_ticks=0 # timer count on last frame
blink_interval=600 # ~ms per blink
next_blink = blink_interval # time until next blink in ms

wb = 72//8 # 9 -> pixel width in bytes
hb = 360//wb # 40 -> pixel width in bytes

wc = 72//2 # 36 -> width in cells
hc = 40//2 # 20 -> height in cells

# BITMAP: width: 72, height: 40
start_screen = bytearray([255,199,63,255,255,31,231,31,255,255,63,199,255,63,223,223,223,223,63,255,255,3,255,255,223,7,219,219,255,255,31,191,223,223,255,191,223,223,223,63,255,255,31,191,223,223,63,191,223,223,63,255,255,255,31,239,247,247,247,247,239,255,255,63,207,247,207,63,255,255,255,255,
           255,255,254,241,252,255,255,255,252,241,254,255,255,248,247,247,247,247,248,255,255,240,255,255,255,240,255,255,255,255,240,255,255,255,255,249,246,246,250,240,255,255,240,255,255,255,240,255,255,255,240,255,255,255,252,251,247,247,247,247,251,243,252,253,253,253,253,253,252,243,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,255,255,31,223,223,223,223,63,255,255,127,255,127,127,255,255,127,127,127,127,255,255,255,255,127,127,127,255,255,255,127,127,127,255,255,255,255,255,255,255,63,223,63,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,255,255,192,253,253,253,253,254,255,255,192,254,255,255,255,224,219,219,219,219,216,255,255,220,219,219,231,255,255,220,219,219,231,255,255,255,255,207,243,244,247,247,247,244,243,207,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255])
cover_screen = thumby.Sprite(72, 40, start_screen, 0, 0, -1)


# contains all rows
def BuildBuffer():
    global buf
    buf = bytearray(wb*hb)
    for i in range(0, wb*hb):
        buf[i] = 0

# contains all cells
def BuildCells():
    global cells
    cells = []
    for i in range(0, wc*hc + 2):
        cells.append(0)

# set cell to 1
def SetCell(x, y):
    global cells
    cells[y*wc+x] = 1

# set cell to 0
def ClearCell(x, y):
    global cells
    cells[y*wc+x] = 0

# get cell state
def GetCell(x, y):
    global cells
    return cells[y*wc+x]

def CheckRule(x, y, i):
    global rule
    if (rule & (1 << i)) > 0:
        SetCell(x, y)
    else:
        ClearCell(x, y)

def SetPixel(x, y):
    global buf
    buf[y*wb+x//8] |= 1 << (x%8)

def ClearPixel(x, y):
    global buf
    buf[y*wb+x//8] &= ~(1 << (x%8))

def RandomizeFirstRow():
    for i in range(0, wc):
        if random.randint(0, 1) == 1:
            SetCell(i, 0)
        else:
            ClearCell(i, 0)

def Beep(): # audio feedback for inputs!
    thumby.audio.play(1000, 50)

def Timing(): # does some common timing and animation handling
    global old_ticks
    global blink_interval
    global next_blink
    global blinks
    
    new_ticks = time.ticks_ms() # calculating delta ticks
    dt = new_ticks - old_ticks
    old_ticks = new_ticks
    
    next_blink -= dt # handle blinking the cursor sprite
    if next_blink <= 0:
        next_blink = blink_interval
        blinks += 1

def Simulate():
    # simulate 1D cellular automata by Stephen Wolfram
    # http://mathworld.wolfram.com/ElementaryCellularAutomaton.html
    global cells
    global buf
    global simulate
    global blinks

    if simulate:
        # build next generation
        for y in range(1, hc):
            for x in range(1, wc-1):
                l = GetCell(x-1, y-1)
                c = GetCell(x, y-1)
                r = GetCell(x+1, y-1)
                i = l*4 + c*2 + r
                CheckRule(x, y, i)

        # draw next generation
        for y in range(0, hc):
            for x in range(0, wc):
                if GetCell(x, y) == 1:
                    SetPixel(x*2, y*2)
                    SetPixel(x*2+1, y*2)
                    SetPixel(x*2, y*2+1)
                    SetPixel(x*2+1, y*2+1)
                else:
                    ClearPixel(x*2, y*2)
                    ClearPixel(x*2+1, y*2)
                    ClearPixel(x*2, y*2+1)
                    ClearPixel(x*2+1, y*2+1)

        # shift cells up
        for y in range(1, hc):
            for x in range(0, wc):
                cells[y*wc+x] = GetCell(x, y-1)

        # randomize first row
        for x in range(0, wc):
            if random.randint(0, 1) == 1:
                SetCell(x, 0)
            else:
                ClearCell(x, 0)

        # draw first row
        for x in range(0, wc):
            if GetCell(x, 0) == 1:
                SetPixel(x*2, 0)
                SetPixel(x*2+1, 0)
            else:
                ClearPixel(x*2, 0)
                ClearPixel(x*2+1, 0)

        # draw buffer
        thumby.display.fill(0)
        fbuffer.blit(FrameBuffer(buf, 72, 40, MONO_HMSB), 0, 0, 72,40) # drawing game board
        thumby.display.update() # flush the screenbuffer

def Draw():
    global buf
    global blinks
    global simulate
    global cursor_x
    global cursor_y
    global cursor_sprite

    # draw the cursor
    if blinks % 2 == 0:
        cursor_sprite.draw()
    else:
        cursor_sprite.erase()
    # draw the buffer
    thumby.draw_buffer(buf)
    thumby.update()
    Timing()

def HandleInput():
    global simulate
    if thumby.buttonA.justPressed():
        Beep()
        simulate = not simulate

while 1:
    thumby.display.fill(0)
    cover_screen.setFrame(blinks)
    thumby.display.drawSprite(cover_screen)
    thumby.display.update()
    HandleInput()

    if simulate:
        break

    thumby.display.update()

BuildBuffer()
BuildCells()
RandomizeFirstRow()

while 1:
    Simulate()
    HandleInput()
    if not simulate:
        break