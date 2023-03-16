"""
First person shooter game in python using just tkinter canavas
Based on https://github.com/jdah/doomenstein-3d/blob/main/src/main_wolf.c
"""
import thumby
from thumbyGrayscale import display, Sprite
import math
import micropython

SCREEN_WIDTH = 72
SCREEN_HEIGHT = 40

# Precompute rotation values
ROTATION_ANGLE = 0.1
COS_ROT = math.cos(ROTATION_ANGLE)
SIN_ROT = math.sin(ROTATION_ANGLE)
COS_NEG_ROT = math.cos(-ROTATION_ANGLE)
SIN_NEG_ROT = math.sin(-ROTATION_ANGLE)

class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @micropython.viper
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    @micropython.viper
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    @micropython.viper
    def __mul__(self, other):
        if isinstance(other, Vector2D):
            return self.x * other.x + self.y * other.y
        else:
            return Vector2D(self.x * other, self.y * other)
    
    @micropython.viper
    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    @micropython.viper
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    @micropython.viper
    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length

    @micropython.viper
    def sign(self, other):
        return self.x * other.y - self.y * other.x
    
    @micropython.viper
    def min(self, other):
        return Vector2D(min(self.x, other.x), min(self.y, other.y))
    
    @micropython.viper
    def max(self, other):
        return Vector2D(max(self.x, other.x), max(self.y, other.y))
    
class Hit:
    def __init__(self, val: int, side: int, pos: Vector2D):
        self.val = val
        self.side = side
        self.pos = pos


MAP_SIZE = 8

# create map data
map_data = [
    1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 2, 0, 2, 2, 0, 1,
    1, 0, 0, 0, 2, 0, 0, 1,
    1, 0, 1, 0, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1,
]

class State:
    def __init__(self):
        # create a pixel buffer
        self.pos = Vector2D(2, 2)
        self.dir = Vector2D(-1, 0.1)
        self.plane = Vector2D(0, 0.66)

    def draw_pixel(self, x, y, color):
        x, y = int(x), int(y)
        display.setPixel(x, y, color)

    def vertical_line(self, x: int, y1: int, y2: int, color):
        display.drawLine(x, y1, x, y2, color)

    @micropython.native
    def rotate(self, rot):
        if rot > 0:
            cos_rot, sin_rot = COS_ROT, SIN_ROT
        elif rot < 0:
            cos_rot, sin_rot = COS_NEG_ROT, SIN_NEG_ROT
        else:
            return

        self.dir = Vector2D(
            self.dir.x * cos_rot - self.dir.y * sin_rot,
            self.dir.x * sin_rot + self.dir.y * cos_rot
        )
        self.plane = Vector2D(
            self.plane.x * cos_rot - self.plane.y * sin_rot,
            self.plane.x * sin_rot + self.plane.y * cos_rot
        )  

s = State()

@micropython.native
def calculate_camera_ray(x):
    xcam = 2 * x / SCREEN_WIDTH - 1
    dir = Vector2D(
        s.dir.x + s.plane.x * xcam,
        s.dir.y + s.plane.y * xcam
    )
    return dir

@micropython.native
def calculate_delta_dist(dir):
    delta_dist = Vector2D(
        1e30 if abs(dir.x) < 1e-20 else abs(1 / dir.x),
        1e30 if abs(dir.y) < 1e-20 else abs(1 / dir.y)
    )
    return delta_dist

@micropython.native
def calculate_side_dist(pos, ipos, dir, delta_dist):
    side_dist = Vector2D(
        delta_dist.x * ((pos.x - ipos.x) if dir.x < 0 else (ipos.x + 1 - pos.x)),
        delta_dist.y * ((pos.y - ipos.y) if dir.y < 0 else (ipos.y + 1 - pos.y))
    )
    return side_dist

@micropython.native
def calculate_step(dir):
    step = Vector2D(
        -1 if dir.x < 0 else 1,
        -1 if dir.y < 0 else 1
    )
    return step

@micropython.native
def perform_dda(hit, side_dist, delta_dist, ipos, step):
    while (hit.val == 0):
        if side_dist.x < side_dist.y:
            side_dist.x += delta_dist.x
            ipos.x += step.x
            hit.side = 0
        else:
            side_dist.y += delta_dist.y
            ipos.y += step.y
            hit.side = 1

        hit.val = map_data[ipos.x + ipos.y * MAP_SIZE]
    return hit, side_dist

@micropython.native
def calculate_color(hit):
    if hit.val == 0:
        color = 0
    elif hit.val == 1:
        color = 1
    elif hit.val == 2:
        color = 2
    else: 
        color = 3

    if hit.side == 1:
        color = min(color + 1, 3)
    return color

@micropython.native
def draw_columns(x, color, dperp):
    h = int(SCREEN_HEIGHT / dperp)
    y0 = max((SCREEN_HEIGHT / 2) - (h / 2), 0)
    y1 = min((SCREEN_HEIGHT / 2) + (h / 2), SCREEN_HEIGHT - 1)

    y0, y1 = int(y0), int(y1)
    s.vertical_line(x, 0, y0, 0)
    s.vertical_line(x, y0, y1, color)
    s.vertical_line(x, y1, SCREEN_HEIGHT - 1, 0)

@micropython.native
def render():
    for x in range(SCREEN_WIDTH):
        dir = calculate_camera_ray(x)
        pos = s.pos
        ipos = Vector2D(int(pos.x), int(pos.y))
        
        delta_dist = calculate_delta_dist(dir)
        side_dist = calculate_side_dist(pos, ipos, dir, delta_dist)
        step = calculate_step(dir)
        
        hit = Hit(0, 0, Vector2D(0, 0))
        hit, side_dist = perform_dda(hit, side_dist, delta_dist, ipos, step)
        
        color = calculate_color(hit)
        hit.pos = Vector2D(pos.x + side_dist.x, pos.y + side_dist.y)
        
        dperp = (side_dist.x - delta_dist.x) if hit.side == 0 else (side_dist.y - delta_dist.y)
        draw_columns(x, color, dperp)

# keypress handler
def keypress():
    # print(event.keysym)
    if thumby.buttonU.pressed():
        s.pos += s.dir * 0.1
    elif thumby.buttonD.pressed():
        s.pos -= s.dir * 0.1
    elif thumby.buttonL.pressed():
        s.rotate(0.1)
    elif thumby.buttonR.pressed():
        s.rotate(-0.1)

def main_loop():
    # render map
    render()

    display.update()

    keypress()

while True:
    main_loop()