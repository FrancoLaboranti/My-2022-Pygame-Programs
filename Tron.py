import math
import time
import random
import pygame, sys
from pygame.locals import *

class Sprite:
    def process(self):
        pass
    def draw(self):
        pass

class Player(Sprite):
    def __init__(self, i, totalplayers,mode):
        self.id = i
        self.direction = 0
        self.directions = {
            0: [0,-150, 0,-2, 0,0],
            1: [150,0, 1,0, 0,0],
            2: [0,150, 0,1, 0,0],
            3: [-150,0, -2,0, 0,0]
        }
        self.mode = mode
        self.leftpressed = False
        self.rightpressed = False
        self.stop = False
        self.aiturn_cdtime = 0.001
        self.aiturn_incd = 0
        self.dire_cdtime = 2
        self.dire_incd = 2

        colors = {
            0: (255,100,100),
            1: (10,255,155),
            2: (225,10,255),
            3: (225,155,10)
        }

        startpos = {
            0: (xper(0.75) if totalplayers < 4 else xper(0.8),yper(0.95)),
            1: (xper(0.25) if totalplayers < 4 else xper(0.2),yper(0.65) if totalplayers == 4 else yper(0.95)),
            2: (xper(0.5) if totalplayers < 4 else xper(0.6),yper(0.85) if totalplayers == 4 else yper(0.95)),
            3: (xper(0.4),yper(0.75))
        }

        controls = {
            0: (pygame.K_LEFT,pygame.K_DOWN),
            1: (pygame.K_q,pygame.K_w),
            2: (pygame.K_o,pygame.K_p),
            3: (pygame.K_v,pygame.K_b)
        }

        self.color = colors[self.id]
        self.x, self.y = startpos[self.id]
        self.left, self.right = controls[self.id]

    def process(self):

        if self.id == 0 or self.mode == 1:
            if not self.leftpressed:

                if keys[self.left]:
                    self.direction = (self.direction-1) % len(self.directions)
                    self.leftpressed = True

            if not self.rightpressed:

                if keys[self.right]:
                    self.direction = (self.direction+1) % len(self.directions)
                    self.rightpressed = True

            if not keys[self.left]:
                self.leftpressed = False

            if not keys[self.right]:
                self.rightpressed = False

        else:

            self.dire_incd += deltaT
            self.aiturn_incd += deltaT

            if self.dire_incd > self.dire_cdtime:

                self.directions[0][5] = random.randint(-50,-5)
                self.directions[1][4] = random.randint(5,50)
                self.directions[2][5] = random.randint(5,50)
                self.directions[3][4] = random.randint(-50,-5)

                self.dire_incd = 0

            if self.aiturn_incd > self.aiturn_cdtime:
                if windowSurface.get_at((int((self.x+self.directions[self.direction][2]) % SCREEN_X), int((self.y+self.directions[self.direction][3]) % SCREEN_Y))) != BLACK or windowSurface.get_at((int((self.x+self.directions[self.direction][4]) % SCREEN_X), int((self.y+self.directions[self.direction][5]) % SCREEN_Y))) != BLACK:
                    if random.randint(0,1) == 0 and windowSurface.get_at((int((self.x+self.directions[(self.direction-1)%len(self.directions)][2]) % SCREEN_X), int((self.y+self.directions[(self.direction-1)%len(self.directions)][3]) % SCREEN_Y))) == BLACK:
                        self.direction = (self.direction-1) % len(self.directions)
                        self.aiturn_incd = 0
                    elif windowSurface.get_at((int((self.x+self.directions[(self.direction+1)%len(self.directions)][2]) % SCREEN_X), int((self.y+self.directions[(self.direction+1)%len(self.directions)][3]) % SCREEN_Y))) == BLACK:
                        self.direction = (self.direction+1) % len(self.directions)
                        self.aiturn_incd = 0

            if self.aiturn_incd > self.aiturn_cdtime:
                if random.randint(0,1500) == 0:
                    if random.randint(0,1) == 0 and windowSurface.get_at((int((self.x+self.directions[(self.direction-1)%len(self.directions)][2]) % SCREEN_X), int((self.y+self.directions[(self.direction-1)%len(self.directions)][3]) % SCREEN_Y))) == BLACK:
                            self.direction = (self.direction-1) % len(self.directions)
                            self.aiturn_incd = 0
                    elif windowSurface.get_at((int((self.x+self.directions[(self.direction+1)%len(self.directions)][2]) % SCREEN_X), int((self.y+self.directions[(self.direction+1)%len(self.directions)][3]) % SCREEN_Y))) == BLACK:
                        self.direction = (self.direction+1) % len(self.directions)
                        self.aiturn_incd = 0

        if self.x > SCREEN_X:
            self.x = 0
        if self.x < 0:
            self.x = SCREEN_X

        if self.y > SCREEN_Y:
            self.y = 0
        if self.y < 0:
            self.y = SCREEN_Y

        if windowSurface.get_at((int((self.x+self.directions[self.direction][2]) % SCREEN_X), int((self.y+self.directions[self.direction][3]) % SCREEN_Y))) != BLACK:
            sprites.remove(self)

        if not self.stop:
            self.x += self.directions[self.direction][0] * deltaT
            self.y += self.directions[self.direction][1] * deltaT

    def draw(self):
        pygame.draw.circle(windowSurface, self.color, (self.x, self.y), 1)

class Driver(Sprite):

    def __init__(self):
        self.menu = True
        self.option = 0
        self.players = 0
        self.mode = 0
        self.choose_option = (0,1,2)
        self.choose_players = (0,1,2)
        self.choose_mode = (0,1)
        self.keypressed = False

    def process(self):
        
        if self.menu:
            if not self.keypressed:

                if keys[pygame.K_UP]:
                    self.option = (self.option-1) % len(self.choose_option)

                    self.keypressed = True

                if keys[pygame.K_DOWN]:
                    self.option = (self.option+1) % len(self.choose_option)

                    self.keypressed = True

                if keys[pygame.K_LEFT]:
                    if self.option == 1:
                        self.players = (self.players-1) % len(self.choose_players)

                    if self.option == 2:
                        self.mode = (self.mode-1) % len(self.choose_mode)

                    self.keypressed = True

                if keys[pygame.K_RIGHT]:
                    if self.option == 1:
                        self.players = (self.players+1) % len(self.choose_players)

                    if self.option == 2:
                        self.mode = (self.mode+1) % len(self.choose_mode)

                    self.keypressed = True

                if keys[pygame.K_RETURN] and self.option == 0:
                    windowSurface.fill(BLACK)
                    for i in range(self.players+2):
                        add_sprite(Player(i,self.players+2,self.mode))

                        self.menu = False

                if keys[pygame.K_ESCAPE]:
                    pygame.quit()
                    sys.exit()

        if len(sprites) <= 2:
            for sprite in sprites:
                sprite.stop = True

            if keys[pygame.K_RETURN] and not self.menu:
                for sprite in sprites:
                    if sprite != self:
                        sprites.remove(sprite)

                windowSurface.fill(BLACK)
                for i in range(self.players+2):
                    add_sprite(Player(i,self.players+2,self.mode))

        if keys[pygame.K_ESCAPE]:
            for sprite in sprites:
                if sprite != self:
                    sprites.remove(sprite)

            windowSurface.fill(BLACK)
            self.menu = True
            self.keypressed = True

        if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN] and not keys[pygame.K_ESCAPE]:
            self.keypressed = False

    def draw(self):
        if self.menu:
            windowSurface.fill(BLACK)
            create_text(B_font,'TRON',randcolor_in_range(100,255,100,255,100,255),BLACK,xper(0.5),yper(0.15))
            create_text(S_font,'Enter to Start',WHITE if self.option == 0 else GRAY,BLACK,xper(0.5),yper(0.38))
            create_text(S_font,'%s Players' % (self.players+2),WHITE if self.option == 1 else GRAY,BLACK,xper(0.5),yper(0.5))
            create_text(S_font,'Player vs AI' if self.mode == 0 else 'Player vs Player',WHITE if self.option == 2 else GRAY,BLACK,xper(0.5),yper(0.62))
            create_text(S_font,'ESC to Exit',(75,75,75),BLACK,xper(0.5),yper(0.85))

        else:

            if len(sprites) == 2:
                for sprite in sprites:
                    if sprite != self:
                        winner = sprite.id
                        color = sprite.color

                create_text(S_font,'%s Wins!' % ('Player 1' if winner == 0 else 'Player 2' if winner == 1 else 'Player 3' if winner == 2 else 'Player 4'),color,None,xper(0.5),yper(0.5))
                create_text(S_font,'Enter to Restart',(75,75,75),None,xper(0.5),yper(0.55))

#Set up pygame
pygame.init()

SCREEN_X = 1280
SCREEN_Y = 720

#Set up the window
windowSurface = pygame.display.set_mode((SCREEN_X, SCREEN_Y), depth=32, display=0)
pygame.display.set_caption('Tron')
B_font = pygame.font.Font(None, 150)
S_font = pygame.font.Font(None, 60)

#Set up the colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (128,128,128)

def xper(percentage):
    return percentage * SCREEN_X

def yper(percentage):
    return percentage * SCREEN_Y

def randcolor():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

def randcolor_in_range(rmin,rmax,gmin,gmax,bmin,bmax):
    return (random.randint(rmin,rmax), random.randint(gmin,gmax), random.randint(bmin,bmax))

def modify_color(color, offset):
    return tuple(max(min(c+offset, 255), 0) for c in color)

def getangle(point1, point2):
    return math.atan2(point2[1]-point1[1], point2[0]-point1[0])

def getdist(point1, point2):
    return math.sqrt(abs(point1[0]-point2[0])**2+abs(point1[1]-point2[1])**2)

def rect_colision(r1, r2):
    if r1[0] + r1[2] > r2[0] and r1[0] < r2[0] + r2[2]:
        if r1[1] + r1[3] > r2[1] and r1[1] < r2[1] + r2[3]:
            return True
    return False

def create_text(font,content,colortext,colorrect,posx,posy):
    text = font.render(content, True, colortext, colorrect)
    textRect = text.get_rect()
    textRect.center = (posx, posy)
    windowSurface.blit(text, textRect)

def add_sprite(sprite):
    sprites.append(sprite)
    return sprite

# INITIALIZATION .....................................................................

deltaT = 0
iniT = time.time()
keys = None
mouse_x = mouse_y = 0
mouse_left = mouse_right = False
sprites = []

add_sprite(Driver())

# MAIN LOOP ..........................................................................

while True:

    now = time.time()
    deltaT = min(now - iniT, 0.01)
    iniT = now

    keys = pygame.key.get_pressed()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_left, _, mouse_right = pygame.mouse.get_pressed()

    for sprite in sprites:
        sprite.process()
        sprite.draw()

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()