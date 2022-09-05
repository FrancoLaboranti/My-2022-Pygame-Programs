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

class SnakePiece(Sprite):

    def __init__(self, n):

        self.id = self.z = n
        self.radius = sper(0.01)
        self.vel = sper(0.3)
        self.angVel = sper(0.01)
        self.ang = random.uniform(0,math.pi*2) if self.id == 0 else snake[self.id-1].ang
        self.x = xper(0.5) if self.id == 0 else snake[self.id-1].x - math.cos(self.ang)
        self.y = yper(0.5) if self.id == 0 else snake[self.id-1].y - math.sin(self.ang)

        snake.append(self)

    def process(self):

        if not manager[0].gameOver and not manager[0].pause:

            self.targetX = mouseX if self.id == 0 else snake[self.id-1].x
            self.targetY = mouseY if self.id == 0 else snake[self.id-1].y

            pointAng = getAngle2(self.ang,(self.x, self.y),(self.targetX, self.targetY))
            targetDist = getDist((self.targetX,self.targetY),(self.x,self.y))

            if self.id > 0:
                if targetDist > self.radius:
                    self.vel = sper(0.4)
                    self.angVel = sper(0.02)
                elif targetDist < self.radius:
                    self.vel = sper(0.2)
                    self.angVel = sper(0.02)
                else:
                    self.vel = sper(0.3)
                    self.angVel = sper(0.01)
            else:
                self.checkHeadCol()

            self.ang += self.angVel * deltaT if pointAng > self.ang else -self.angVel * deltaT
            self.ang %= math.pi*2
            self.x += math.cos(self.ang)*self.vel*deltaT
            self.y += math.sin(self.ang)*self.vel*deltaT

    def draw(self):

        pygame.draw.circle(windowSurface, (0,155,0), (self.x, self.y), self.radius)
        pygame.draw.circle(windowSurface, (0,255,0), (self.x, self.y), self.radius*0.9)
        # if not self.id % 5: createTextCenter(tFont,str(self.id),(255,255,255),None,self.x,self.y+self.radius*2)

    def checkHeadCol(self):

        for piece in snake:
            if piece.id > 4:
                if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*2:
                    manager[0].gameOver = True

        for piece in food:
            if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*2:
                if not piece.grabbed:
                    piece.grabbed = True
                    for n in range(3):
                        addSprite(SnakePiece(len(snake)))
                    manager[0].score += 33

class Food(Sprite):

    def __init__(self):

        self.z = -1
        self.ang = random.uniform(0,math.pi*2)
        self.angVel = sper(0.03)
        self.radius = sper(0.01)
        self.glowCD = 0
        self.grabbed = False

        reroll = True
        while reroll:
            self.x, self.y = random.randint(xper(0.1),screenX-xper(0.1)), random.randint(yper(0.1),screenY-yper(0.1))
            reroll = False
            for piece in snake:
                if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*2:
                    reroll = True
                    break

        food.append(self)

    def process(self):

        self.glowCD = max(self.glowCD - deltaT, 0)

        if self.glowCD == 0:
            self.glowCD = 0.5

        self.ang += self.angVel * deltaT

        if self.grabbed:
            self.radius -= deltaT*50
            if self.radius < sper(0.002):
                spritesToRemove.append(self)

    def draw(self):

        color = (125,0,0) if self.glowCD > 0.05 else (255,255,0)
        for i in range(10):
            pygame.draw.line(windowSurface, modifyColorPerc(color,2),(self.x + math.cos(self.ang - math.pi/2) * self.radius*(1-i*0.2), self.y + math.sin(self.ang - math.pi/2) * self.radius*(1-i*0.2)), (self.x + math.cos(self.ang) * self.radius*(1-i*0.2), self.y + math.sin(self.ang) * self.radius*(1-i*0.2)), int(self.radius/4))
        pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang) * self.radius, self.y + math.sin(self.ang) * self.radius), (self.x + math.cos(self.ang + math.pi/2) * self.radius, self.y + math.sin(self.ang + math.pi/2) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang + math.pi/2) * self.radius, self.y + math.sin(self.ang + math.pi/2) * self.radius), (self.x - math.cos(self.ang) * self.radius, self.y - math.sin(self.ang) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, color, (self.x - math.cos(self.ang) * self.radius, self.y - math.sin(self.ang) * self.radius), (self.x + math.cos(self.ang - math.pi/2) * self.radius, self.y + math.sin(self.ang - math.pi/2) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang - math.pi/2) * self.radius, self.y + math.sin(self.ang - math.pi/2) * self.radius), (self.x + math.cos(self.ang) * self.radius, self.y + math.sin(self.ang) * self.radius), int(self.radius/4))

class Manager(Sprite):

    def __init__(self):

        self.z = -2
        self.showFPS = False
        self.escPressed = False
        self.fPressed = False
        self.pPressed = False
        self.gameOver = False
        self.score = 0
        self.pause = False
        self.pauseBlinkCD = 0

        manager.append(self)

    def process(self):

        if not snake:
            for i in range(5):
                addSprite(SnakePiece(i))

        if not food:
            addSprite(Food())

        if not self.escPressed:
            if keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

        if not self.fPressed:
            if keys[pygame.K_f]:
                self.showFPS = not self.showFPS
                self.fPressed = True

        if not self.pPressed and not self.gameOver:
            if keys[pygame.K_p]:
                self.pause = not self.pause
                self.pauseBlinkCD = 0
                self.pPressed = True

        if self.gameOver and mouseLeft:
            self.reset()

        if not keys[pygame.K_ESCAPE]: self.escPressed = False
        if not keys[pygame.K_f]: self.fPressed = False
        if not keys[pygame.K_p]: self.pPressed = False        

    def draw(self):

        createTextLeft(tFont,'Score: %s' %(self.score),(255,255,255),None,xper(0.01),yper(0.02))

        if self.gameOver:
            createTextCenter(bFont,'GAME OVER',(255,255,255),None,xper(0.5),yper(0.45))
            createTextCenter(mFont,'Press LMB to Restart',(0,255,125),None,xper(0.5),yper(0.55))

        if self.pause:
            self.pauseBlinkCD += deltaT
            createTextCenter(bFont,'PAUSE' if self.pauseBlinkCD > 0.25 else '',(255,255,255),None,xper(0.5),yper(0.5))
            if self.pauseBlinkCD > 0.5: self.pauseBlinkCD = 0

        if self.showFPS: createTextLeft(tFont,'FPS: %s' %(str(round(clock.get_fps()))),(255,255,255),None,xper(0.95),yper(0.01))

    def reset(self):
        while len(sprites) > 1:
            for sprite in sprites:
                if sprite != self:
                    spritesToRemove.append(sprite)
            removeSprites()
        self.gameOver = False
        self.score = 0

def xper(percentage):
    return percentage * screenX

def yper(percentage):
    return percentage * screenY

def sper(percentage):
    return percentage * (screenX+screenY)/2

def modifyColorPerc(color, offset):
    return tuple(int(max(min(c*offset, 255), 0)) for c in color)

def getAngle2(prevAng, point1, point2):
    angle = math.atan2(point2[1]-point1[1], point2[0]-point1[0])
    if angle - prevAng < -math.pi: angle += math.pi*2
    if angle - prevAng >  math.pi: angle -= math.pi*2
    return angle

def getDist(point1, point2):
    return math.sqrt(abs(point1[0]-point2[0])**2+abs(point1[1]-point2[1])**2)

def createTextLeft(font, content, colorText, colorRect, posX, posY):
    text = font.render(content, True, colorText, colorRect)
    textRect = text.get_rect()
    textRect = (posX, posY)
    windowSurface.blit(text, textRect)

def createTextCenter(font, content, colorText, colorRect, posX, posY):
    text = font.render(content, True, colorText, colorRect)
    textRect = text.get_rect()
    textRect.center = (posX, posY)
    windowSurface.blit(text, textRect)

def addSprite(sprite):
    sprites.append(sprite)
    return sprite

def removeSprites():
    for sprite in sprites:
        if sprite in spritesToRemove:
            if sprite in snake:
                snake.remove(sprite)
            if sprite in food:
                food.remove(sprite)
            sprites.remove(sprite)
            spritesToRemove.remove(sprite)

# INITIALIZATION .....................................................................

pygame.init()

screenX = 1280
screenY = 720
windowSurface = pygame.display.set_mode((screenX, screenY), depth=32, display=0)
pygame.display.set_caption('Snake')

bFont = pygame.font.Font(None, int(sper(0.128)))
mFont = pygame.font.Font(None, int(sper(0.0512)))
sFont = pygame.font.Font(None, int(sper(0.0256)))
tFont = pygame.font.Font(None, int(sper(0.0192)))

deltaT = 0
iniT = time.time()
clock = pygame.time.Clock()
keys = None
mouseX = mouseY = 0
mouseLeft = mouseRight = False
background = (0,0,0)
sprites = []
manager = []
snake = []
food = []
spritesToRemove = []

addSprite(Manager())

# MAIN LOOP ..........................................................................

while True:

    now = time.time()
    deltaT = min(now - iniT, 0.05)
    iniT = now
    clock.tick()

    keys = pygame.key.get_pressed()
    mouseX, mouseY = pygame.mouse.get_pos()
    mouseLeft, mouseMiddle, mouseRight = pygame.mouse.get_pressed()

    windowSurface.fill(background)

    sprites.sort(key=lambda x: x.z, reverse=True)

    for sprite in sprites:
        sprite.process()
        sprite.draw()

    removeSprites()

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()