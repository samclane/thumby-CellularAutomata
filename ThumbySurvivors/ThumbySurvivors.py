import random
from thumby import Sprite, display
import thumby

# BITMAP: width: 144, height: 80
titlescreenFrames = bytearray([255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,247,247,7,247,247,255,7,223,223,31,255,255,31,255,255,31,255,255,31,223,223,31,223,223,31,255,255,7,223,223,63,255,159,127,255,63,223,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,252,255,255,255,252,255,255,252,255,255,252,253,253,252,255,255,252,255,255,252,255,255,252,255,255,252,253,253,254,255,255,246,249,254,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,153,182,182,204,255,255,131,191,191,131,255,255,131,251,251,251,231,159,159,227,255,130,255,251,231,159,159,227,255,131,187,187,131,255,255,131,251,251,179,171,139,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,31,223,223,63,255,255,127,127,127,255,255,127,127,255,255,127,127,127,255,255,127,127,127,255,255,255,255,255,255,31,159,127,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,
           255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,240,254,254,255,255,255,240,255,255,255,248,245,245,244,255,246,245,241,255,255,246,245,241,255,255,255,255,247,248,253,253,252,243,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255])
cover_screen = Sprite(72, 40, titlescreenFrames, 0, 0, -1)

play = False

class Weapon: # abstract
    def __init__(self, x, y, direction):
        self._x = x
        self._y = y
        self._direction = direction
        self.weapon = None
        self.weaponOutline = None
        self.weaponSlash = None
        self.weaponSlashOutline = None
        self.sprites = [self.weapon, self.weaponOutline, self.weaponSlash, self.weaponSlashOutline]

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.weapon.x = value
        self.weaponOutline.x = value
    
    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.weapon.y = value
        self.weaponOutline.y = value

    @property
    def direction(self):
        return self._direction
    
    @direction.setter
    def direction(self, value):
        if value != self._direction:
            for sprite in self.sprites:
                if sprite:
                    sprite.mirrorX = not sprite.mirrorX
        self._direction = value

    
    def draw(self, frame=0):
        # update frame
        for sprite in self.sprites:
            if sprite:
                sprite.setFrame(frame // 10)
        # draw the icon
        display.drawSprite(self.weaponOutline)
        display.drawSprite(self.weapon)
        # draw the slash
        if self.weaponSlashOutline:
            display.drawSprite(self.weaponSlashOutline)
        display.drawSprite(self.weaponSlash)

    def attack(self, character):
        # move the slash to the character
        self.weaponSlash.x = character.char.x + (character.char.width * self.direction)
        self.weaponSlash.y = character.char.y
        if self.weaponSlashOutline:
            self.weaponSlashOutline.x = character.char.x + (character.char.width * self.direction)
            self.weaponSlashOutline.y = character.char.y
    
    def checkCollision(self, zombie, frame=0):
        # check if the slash is colliding with the zombie
        if self.weaponSlash.x + self.weaponSlash.width > zombie.zombie.x and self.weaponSlash.x < zombie.zombie.x + zombie.zombie.width:
            if self.weaponSlash.y + self.weaponSlash.height > zombie.zombie.y and self.weaponSlash.y < zombie.zombie.y + zombie.zombie.height:
                zombie.die(frame)

class Knife(Weapon):
    # 12x13 for 1 frames
    knifeFrames = bytearray([0,14,20,40,80,160,192,64,0,0,0,0,0,0,0,0,0,1,0,1,2,4,8,0])
    # 12x13 for 1 frames
    knifeOutlineFrames = bytearray([224,192,128,1,3,7,15,31,31,255,255,255,31,31,31,31,28,28,28,24,16,0,1,3])
    # 8x14 for 2 frames
    knifeSlashFrames = bytearray([1,3,14,226,4,24,224,0,32,48,28,17,8,6,1,0,0,0,1,0,194,28,248,224,0,0,32,0,16,14,7,1])
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.weapon = Sprite(12, 13, self.knifeFrames, x, y)
        self.weaponOutline = Sprite(12, 13, self.knifeOutlineFrames, x, y)
        self.weaponSlash = Sprite(8, 14, self.knifeSlashFrames, x, y)
        self.weaponSlashOutline = None
        self.sprites = [self.weapon, self.weaponOutline, self.weaponSlash, self.weaponSlashOutline]

class Sword(Weapon):
    # 17x17 for 1 frames
    gswordFrames = bytearray([0,14,30,62,108,216,176,96,192,128,0,0,0,0,0,0,0,0,0,0,0,0,0,1,3,22,9,1,10,17,32,64,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    gswordOutlineFrames = bytearray([224,192,128,0,0,1,3,7,15,31,63,127,127,127,255,255,255,255,255,255,255,254,252,248,192,192,192,224,192,128,4,15,31,63,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0])
    # 20x30 for 1 frames
    gswordSlashFrames = bytearray([1,1,3,7,7,14,30,54,126,236,204,24,56,48,96,192,128,0,0,0,0,0,0,0,0,0,0,0,0,0,3,15,254,240,0,0,3,15,254,240,0,0,0,0,0,0,0,0,128,192,240,60,31,3,128,192,112,60,31,3,32,32,48,56,56,28,30,27,31,13,12,6,7,3,1,0,0,0,0,0])
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.weapon = Sprite(17, 17, self.gswordFrames, x, y)
        self.weaponOutline =  Sprite(17, 17, self.gswordOutlineFrames, x, y)
        self.weaponSlash = Sprite(20, 30, self.gswordSlashFrames, x, y)
        self.weaponSlashOutline = None
        self.sprites = [self.weapon, self.weaponOutline, self.weaponSlash, self.weaponSlashOutline]


class Projectile(Weapon): # abstract class
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.shooting_direction = direction
        self._direction = direction

    def attack(self, character):
        if not self.shooting_direction:
            # move the projectile to the weapon
            self.weaponSlash.x = character.char.x + character.char.width * self.direction
            self.weaponSlash.y = character.char.y
            if self.weaponSlashOutline:
                self.weaponSlashOutline.x = character.char.x + character.char.width * self.direction
                self.weaponSlashOutline.y = character.char.y
            self.shooting_direction = self._direction

    def draw(self, frame=0):
        # draw the weapon slash, which is the projectile
        super().draw(frame)
        # move the projectile
        if self.shooting_direction != 0:
            self.weaponSlash.x += 1 * self.shooting_direction
            if self.weaponSlashOutline:
                self.weaponSlashOutline.x += 1 * self.shooting_direction
            # check if the projectile is out of the screen
            if self.weaponSlash.x > 72 or self.weaponSlash.x < 0:
                self.shooting_direction = 0
            

class Wand(Projectile):
    # 12x7 for 2 frames
    boltFrames = bytearray([8,24,12,24,44,8,34,9,93,72,34,8,8,12,24,12,26,8,34,72,93,9,34,8])

    # 13x13 for 1 frames
    wandFrames = bytearray([0,22,22,88,14,32,72,128,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,4,8,0])
    # 13x13 for 1 frames
    wandOutlineFrames = bytearray([192,192,0,0,0,0,3,3,63,127,255,255,255,31,31,31,31,31,31,30,28,24,16,0,1,3])
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction)
        self.weapon = Sprite(13, 13, self.wandFrames, x, y)
        self.weaponOutline = Sprite(13, 13, self.wandOutlineFrames, x, y)
        self.weaponSlash = Sprite(12, 7, self.boltFrames, x, y, mirrorX=True)
        self.weaponSlashOutline = None
        self.sprites = [self.weapon, self.weaponOutline, self.weaponSlash, self.weaponSlashOutline]

class Char:
    # 8x9 for 1 frames
    charFrames = bytearray([0,16,200,62,62,200,16,0,0,0,0,0,0,0,0,0])
    # 8x9 for 1 frames
    charOutlineFrames = bytearray([199,3,0,0,0,0,3,199,1,0,0,0,0,0,0,1])
    # 11x7 for 4 frames
    explosionFrames = bytearray([8,34,0,65,0,0,0,65,0,34,8,28,54,34,65,65,65,65,65,34,54,28,8,42,20,93,42,20,42,93,20,42,8,0,0,0,0,20,8,20,0,0,0,0])

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = Sprite(8, 9, self.charFrames, 0, 0)
        self.charOutline = Sprite(8, 9, self.charOutlineFrames, 0, 0)
        self.weapon = Wand(72//2 - self.char.width*2, 40//2 - self.char.height, -1)
        self.explosion = Sprite(11, 7, self.explosionFrames, 0, 0)
        self.is_dead = False
        self._is_facing_right = True
        self._is_facing_up = False
        self.fire_rate = 5

    @property
    def is_facing_right(self):
        return self._is_facing_right

    @is_facing_right.setter
    def is_facing_right(self, value):
        self._is_facing_right = value
        self.weapon.direction = 1 if value else -1
        self.weapon.x = 72//2 + self.char.width//2 if value else 72//2 - self.char.width*2
    
    @property
    def is_facing_up(self):
        return self._is_facing_up

    @is_facing_up.setter
    def is_facing_up(self, value):
        self._is_facing_up = value
        self.weapon.weaponSlash.mirrorY = value
        if self.weapon.weaponSlashOutline:
            self.weapon.weaponSlashOutline.mirrorY = value

    def draw(self, frame=0):
        if self.is_dead:
            return
        self.char.x = 72//2 - self.char.width//2
        self.char.y = 40//2 - self.char.height//2 
        self.charOutline.x = self.char.x
        self.charOutline.y = self.char.y
        display.drawSprite(self.charOutline)
        self.weapon.draw(frame)
        if frame % self.fire_rate == 0:
            self.weapon.attack(self)
        display.drawSprite(self.char)

    def die(self, frame=0):
        self.explosion.x = self.char.x
        self.explosion.y = self.char.y
        self.explosion.setFrame(frame // 10)
        display.drawSprite(self.explosion)


class Zombie:
    # 5x8 for 3 frames
    zombieFrames = bytearray([243,59,204,12,4,243,251,12,12,4,192,51,251,12,4])
    # 5x5 for 2 frames
    dieFrames = bytearray([0,4,14,4,0,4,10,17,10,4])

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.zombie = Sprite(5, 8, self.zombieFrames, 0, 0)
        self.dieSprite = Sprite(5, 5, self.dieFrames, 0, 0)
        self.is_dead = False
        self.despawn = False

    def draw(self, character):
        self.zombie.x = self.x - character.x + 72//2 - self.zombie.width//2
        self.zombie.y = self.y  - character.y + 40//2 - self.zombie.height//2
        if self.is_dead:
            self.dieSprite.x = self.x - character.x + 72//2 - self.dieSprite.width//2
            self.dieSprite.y = self.y - character.y + 40//2 - self.dieSprite.height//2
            display.drawSprite(self.dieSprite)
        else:
            display.drawSprite(self.zombie)

    def spawn(self, character):
        # spawn in a random location off screen with respect to the player
        if random.randint(0, 1) == 0:
            self.x = character.x + random.randint(0, 72)
        else:
            self.x = character.x - random.randint(0, 72)
        if random.randint(0, 1) == 0:
            self.y = character.y + random.randint(0, 40)
        else:
            self.y = character.y - random.randint(0, 40)
        self.is_dead = False
        self.despawn = False

    def move(self, character, frame=0):
        if self.is_dead:
            return
        self.zombie.setFrame(frame // 10)
        # move towards the player
        if random.randint(0, 100) < 10:
            if self.x < character.x:
                self.x += 1
            elif self.x > character.x:
                self.x -= 1
            if self.y < character.y:
                self.y += 1
            elif self.y > character.y:
                self.y -= 1

    def die(self, frame=0):
        self.dieSprite.setFrame(frame // 10)
        self.is_dead = True
        if self.dieSprite.getFrame() == 1:
            self.despawn = True

    def checkCollision(self, character, frame=0):
        if self.is_dead:
            return
        global play
        if self.x - character.x + 72//2 - self.zombie.width//2 < 72//2 - self.zombie.width//2 + self.zombie.width and self.x - character.x + 72//2 - self.zombie.width//2 + self.zombie.width > 72//2 - self.zombie.width//2 and self.y - character.y + 40//2 - self.zombie.height//2 < 40//2 - self.zombie.height//2 + self.zombie.height and self.y - character.y + 40//2 - self.zombie.height//2 + self.zombie.height > 40//2 - self.zombie.height//2:
            character.die(frame)
            play = False


def handleInput():
    global play
    if not play:
        if thumby.buttonA.justPressed():
            play = True
    else:
        if thumby.buttonU.pressed():
            c.y -= 1
            c.is_facing_up = True
        if thumby.buttonD.pressed():
            c.y += 1
            c.is_facing_up = False
        if thumby.buttonL.pressed():
            c.x -= 1
            c.is_facing_right = False
        if thumby.buttonR.pressed():
            c.x += 1
            c.is_facing_right = True

while 1: # start screen loop
    display.fill(0)
    display.drawSprite(cover_screen)
    display.update()
    handleInput()

    if play:
        break

c = Char(0, 0)
zombies = []
for i in range(0, 10):
    z = Zombie(0, 0)
    z.spawn(c)
    zombies.append(z)
frameCount = 0

while 1: # game loop
    display.fill(0)
    handleInput()
    c.draw(frameCount)
    for z in zombies:
        if z.despawn:
            z.spawn(c)
        else:
            z.draw(c)
            z.move(c, frameCount)
            z.checkCollision(c, frameCount)
            c.weapon.checkCollision(z, frameCount)
    display.update()
    frameCount += 1