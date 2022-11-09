import thumby 
from framebuf import FrameBuffer, MONO_HMSB, MONO_VLSB, MONO_HLSB
import utime

# Simulate mold in a cellular automata
simulate = False
at_start_screen = True
buf = bytearray()
cells = []
blinks = 0
fbuffer = FrameBuffer(thumby.display.display.buffer, 72, 40, MONO_VLSB) # create thumby buffer
cfilt = [[0,1,0],[1,0,1],[0,1,0]]  # convolution filter for mold growth

wb = 72//8 # 9 -> pixel width in bytes
hb = 360//wb # 40 -> pixel width in bytes

wc = 72//2 # 36 -> width in cells
hc = 40//2 # 20 -> height in cells

# BITMAP: width: 2, height: 2
cursor = bytearray([3,3])
cursor_sprite = thumby.Sprite(2, 2, cursor) # create a cursor sprite
cursor_sprite.x = 0
cursor_sprite.y = 0

# BITMAP: width: 8, height: 8
fcursor = bytearray([126,189,219,231,231,219,189,126])
fcursor_sprite = thumby.Sprite(8, 8, fcursor) # create a cursor sprite
fcursor_sprite.x = 0
fcursor_sprite.y = 0

# BITMAP: width: 72, height: 40
start_screen = bytearray([255,255,255,255,255,255,255,255,255,255,255,255,127,127,127,255,127,63,191,191,63,255,255,255,255,127,127,255,255,255,255,255,255,255,127,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,31,225,252,255,252,241,252,255,255,7,240,255,131,124,126,255,252,252,61,131,255,255,255,3,248,255,255,127,127,127,255,255,255,0,253,253,125,125,57,131,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,254,255,255,127,127,127,255,255,255,255,255,255,255,255,254,254,254,254,254,255,255,255,255,252,253,254,254,255,255,255,255,255,255,254,254,254,254,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,255,252,241,230,239,207,31,255,255,255,255,0,255,255,31,195,199,159,207,225,60,128,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,252,253,253,253,252,254,255,255,255,255,253,252,255,255,254,255,255,255,255,249,252,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255])
cover_screen = thumby.Sprite(72, 40, start_screen, 0, 0, -1)

def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

def BuildBuffer(): # converts game screen (cells) into a screen buffer
    global buf
    buf = bytearray() # will store our pixel data
    gi=0 # index into cells array
    for row in range(hb):
        if row%2 == 0:
            for col in range(wb):
                nb = 0b0
                for i in range(4):
                    nb |= (0b11*cells[gi]) << (i*2)
                    gi+=1
                buf.append(nb)
        else:
            buf.extend(buf[-wb:])

def InitCells(): # initializes the cells array
    global cells
    cells = []
    for row in range(hc):
        for col in range(wc):
            cells.append(0)

def SetCell(x, y, v): # sets a cell to a value
    global cells
    cells[y*wc+x] = v

@micropython.native
def GetCell(x, y): # gets a cell's value
    global cells
    return cells[y*wc+x]

@timed_function
def Convolve(filt): # convolves a 3x3 filter with the cells array
    _Convolve(filt)

@micropython.native
def _Convolve(filt):
    global cells
    new_cells = []
    for row in range(hc):
        for col in range(wc):
            v = 0
            for i in range(3):
                for j in range(3):
                    v |= filt[i][j] & GetCell((col+j-1) % wc-1, (row+i-1) % hc-1)
            new_cells.append(1 if v > 0 else 0)
    cells = new_cells

def Beep(): # audio feedback for inputs!
    thumby.audio.play(1000, 50)


def HandleInput(): # called every frame
    global cursor_sprite
    global simulate
    global at_start_screen
    global cells

    if thumby.buttonB.justPressed(): # toggles the simulate flag
        Beep()
        if at_start_screen:
            at_start_screen = False
        else:
            simulate = not simulate
    if thumby.buttonA.justPressed():
        Beep()
        if not at_start_screen and not simulate:
            SetCell(cursor_sprite.x//2, cursor_sprite.y//2, 1)
        elif at_start_screen:
            at_start_screen = False
    if thumby.buttonU.justPressed():
        Beep()
        cursor_sprite.y -= 2
    if thumby.buttonD.justPressed():
        Beep()
        cursor_sprite.y += 2
    if thumby.buttonL.justPressed():
        Beep()
        cursor_sprite.x -= 2
    if thumby.buttonR.justPressed():
        Beep()
        cursor_sprite.x += 2


def DrawCells():
    global buf
    global fbuffer
    fbuffer.blit(FrameBuffer(buf, 72, 40, MONO_HMSB), 0, 0, 72,40) # drawing game board
    if not simulate:
        thumby.display.drawSprite(cursor_sprite)
    thumby.display.update()
        

def Simulate():
    # Simulate mold in a cellular automata
    global cells
    global buf
    global blinks
    global cursor_sprite
    global cfilt

    if simulate:
        Convolve(cfilt)

    BuildBuffer()

def EditFilterScreen():
    # screen for editing the convolution filter
    global cfilt
    global fcursor_sprite
    global blinks
    global at_start_screen
    global simulate

    while 1:
        thumby.display.fill(0)
        thumby.display.drawSprite(fcursor_sprite)
        # draw the filter
        for i in range(3):
            for j in range(3):
                #  if filt is 1 AND cursor is not on it
                if cfilt[i][j] and not (fcursor_sprite.x == j*8 and fcursor_sprite.y == i*8):
                    thumby.display.drawFilledRectangle(j*8, i*8, 8, 8, 1)
        # draw text
        thumby.display.drawText("Edit Filter", 0, (j+1)*8, 1)
        thumby.display.update()
        if thumby.buttonU.justPressed():
            Beep()
            fcursor_sprite.y -= 8
        if thumby.buttonD.justPressed():
            Beep()
            fcursor_sprite.y += 8
        if thumby.buttonL.justPressed():
            Beep()
            fcursor_sprite.x -= 8
        if thumby.buttonR.justPressed():
            Beep()
            fcursor_sprite.x += 8 
        if thumby.buttonB.justPressed():
            Beep()
            # at_start_screen = True
            break
        if thumby.buttonA.justPressed():
            Beep()
            cfilt[fcursor_sprite.y//8][fcursor_sprite.x//8] = not cfilt[fcursor_sprite.y//8][fcursor_sprite.x//8]

# Init
thumby.display.setFPS(60)

# Start Screen
while 1: # start screen loop
    thumby.display.fill(0)
    cover_screen.setFrame(blinks) # animate the controls screen
    thumby.display.drawSprite(cover_screen)
    thumby.display.update()
    HandleInput()

    if not at_start_screen:
        break

EditFilterScreen()

# Init Game
InitCells()

# Game Loop
while 1:
    HandleInput()
    Simulate()
    DrawCells()