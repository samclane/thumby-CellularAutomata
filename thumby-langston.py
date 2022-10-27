import thumby 
import random
from framebuf import FrameBuffer, MONO_HMSB, MONO_VLSB, MONO_HLSB
import time

# langston's ant for thumby
# based on game of life for thumby

simulate = True

buf = bytearray()
cells = []
blinks = 0
antd = 0

wb = 72//8 # 9 -> pixel width in bytes
hb = 360//wb # 40 -> pixel width in bytes

wc = 72//2 # 36 -> width in cells
hc = 40//2 # 20 -> height in cells
antx = wc//2
anty = hc//2

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
        
def Simulate(): # simulates langstons ant
    global antx
    global anty
    global antd
    global cells
    global blinks
    
    gi = anty*wc + antx # get index into cells array
    
    if cells[gi] == 0: # change direction and color
        antd = (antd+1)%4
        cells[gi] = 1
    else:
        antd = (antd-1)%4
        cells[gi] = 0

    if antd == 0: # move ant
        anty -= 1
    elif antd == 1:
        antx += 1
    elif antd == 2:
        anty += 1
    elif antd == 3:
        antx -= 1
        
    if antx < 0: # wrap ant
        antx = wc-1
    elif antx >= wc:
        antx = 0
    if anty < 0:
        anty = hc-1
    elif anty >= hc:
        anty = 0
            
    # set frame buffer
    BuildBuffer()
    

fbuffer = FrameBuffer(thumby.display.display.buffer, 72, 40, MONO_VLSB) # create thumby buffer

old_ticks=0 # timer count on last frame
blink_interval=600 # ~ms per blink
next_blink = blink_interval # time until next blink in ms
blinks = 0 # used for animating sprite
thumby.display.setFPS(30) # who needs 60fps?!
InitCells()

while 1: # simulation screen
    Timing()
    
    thumby.display.fill(0)
    fbuffer.blit(FrameBuffer(buf, 72, 40, MONO_HMSB), 0, 0, 72,40) # drawing game board
    
    if simulate: # hide cursor if simulating
        Simulate()
    
    thumby.display.update() # flush the screenbuffer