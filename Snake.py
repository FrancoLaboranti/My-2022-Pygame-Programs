import math
import time
import random
import pygame, sys
import pygame.freetype
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
        self.x = xper(0.5) if self.id == 0 else snake[self.id-1].x
        self.y = yper(0.5) if self.id == 0 else snake[self.id-1].y
        self.wave_time = 0
        self.wave_time_total = 0.2
        self.color = randColorInRange(10,40,225,255,10,40) if self.id % 4 == 0 else randColorInRange(10,40,75,125,10,40)

        snake.append(self)

    def process(self):

        if not manager[0].gameOver and not manager[0].pause:

            self.targetX = mouseX if self.id == 0 else snake[self.id-1].x
            self.targetY = mouseY if self.id == 0 else snake[self.id-1].y

            targetAng = getAngle2(self.ang,(self.x, self.y),(self.targetX, self.targetY))
            targetDist = getDist((self.x,self.y),(self.targetX,self.targetY))

            if self.id == 0:
                self.checkHeadCol()
            else:
                self.vel = sper(0.4) if targetDist > self.radius*0.75 else sper(0.2) if targetDist < self.radius*0.75 else sper(0.3)
                self.angVel = sper(0.02) if targetDist > self.radius*0.75 or targetDist < self.radius*0.75 else sper(0.01)

            self.ang += self.angVel * deltaT if targetAng > self.ang else -self.angVel * deltaT
            self.ang %= math.pi*2
            self.x += math.cos(self.ang)*self.vel*deltaT*(1.5 if mouseLeft else 1)
            self.y += math.sin(self.ang)*self.vel*deltaT*(1.5 if mouseLeft else 1)

            if self.wave_time > 0:
                self.wave_time = max(self.wave_time - deltaT, 0)
                if self.wave_time < self.wave_time_total * 0.97 and self.wave_time > self.wave_time_total * 0.5 and self.id+1 < len(snake) and snake[self.id+1].wave_time == 0:
                    snake[self.id+1].wave_time = self.wave_time_total

    def draw(self):

        color = self.color

        if self.id == 0 and len(snake) > 80:
            radius = self.radius * 1.4
        elif self.id == 0 and len(snake) > 40:
            radius = self.radius * 1.2
        else:
            radius = self.radius

        limit = len(snake) - min(len(snake) / 2, 20)
        if self.id > limit:
            radius -= radius * ((self.id - limit) / (snake[-1].id - limit) * 0.6)

        if self.wave_time > 0:
            wave_factor = (self.wave_time_total - self.wave_time) / self.wave_time_total
            radius += self.radius * (math.sin(math.pi * wave_factor) * (3 if self.id == 0 else 1))
            color = modifyColorPerc(color , 1 + (math.sin(math.pi * wave_factor)*3))

        pygame.draw.circle(windowSurface, color, (self.x, self.y), radius)

        if self.id == 0:
            pygame.draw.circle(windowSurface, (255,255,255), (self.x + math.cos(self.ang) * radius*0.4 + math.cos(self.ang + math.pi/2) * radius*0.5, self.y + math.sin(self.ang) * radius*0.4 + math.sin(self.ang + math.pi/2) * radius*0.5), radius*0.4)
            pygame.draw.circle(windowSurface, (255,255,255), (self.x + math.cos(self.ang) * radius*0.4 - math.cos(self.ang + math.pi/2) * radius*0.5, self.y + math.sin(self.ang) * radius*0.4 - math.sin(self.ang + math.pi/2) * radius*0.5), radius*0.4)
            pygame.draw.circle(windowSurface, (100,0,0), (self.x + math.cos(self.ang) * radius*0.55 + math.cos(self.ang + math.pi/2) * radius*0.5, self.y + math.sin(self.ang) * radius*0.55 + math.sin(self.ang + math.pi/2) * radius*0.5), radius*0.2)
            pygame.draw.circle(windowSurface, (100,0,0), (self.x + math.cos(self.ang) * radius*0.55 - math.cos(self.ang + math.pi/2) * radius*0.5, self.y + math.sin(self.ang) * radius*0.55 - math.sin(self.ang + math.pi/2) * radius*0.5), radius*0.2)

    def checkHeadCol(self):

        for piece in snake:
            if piece.id > 5 and piece.id % 4 == 0:
                if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*2:
                    manager[0].gameOver = True

        for piece in food:
            if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*2:
                if not piece.grabbed:
                    piece.grabbed = True
                    manager[0].score += 110
                    for i in range(10):
                        addSprite(SnakePiece(len(snake)))
                    self.wave_time = self.wave_time_total

class Food(Sprite):

    def __init__(self):

        self.z = -1
        self.ang = random.uniform(0,math.pi*2)
        self.angVel = sper(0.03)
        self.radius = sper(0.01)
        self.glowCD = 1
        self.grabbed = False
        self.timer = 10

        reroll = True
        while reroll:
            self.x, self.y = random.randint(xper(0.1),screenX-xper(0.1)), random.randint(yper(0.1),screenY-yper(0.1))
            reroll = False
            for piece in snake:
                if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*10:
                    reroll = True
                    break

        food.append(self)

    def process(self):

        if not manager[0].gameOver and not manager[0].pause:
            self.timer = max(self.timer - deltaT, 0)
        self.glowCD = max(self.glowCD - deltaT, 0)

        if self.glowCD == 0:
            self.glowCD = 0.2 if self.timer <= 2 else 0.5 if self.timer <= 5 else 1

        if self.timer == 0 or self.grabbed:
            spritesToRemove.append(self)

        self.ang += self.angVel * deltaT

    def draw(self):

        color = (255,255,255) if self.glowCD <= 0.1 else (100,0,0)
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
        self.fPressed = False
        self.pPressed = False
        self.mPressed = False
        self.altEnterPressed = False
        self.gameOver = False
        self.score = 0
        self.pause = False
        self.pauseBlinkCD = 0
        self.initCD = 4
        self.fullScreen = False

        manager.append(self)

    def process(self):

        if self.initCD > 0:
            self.initCD = max(self.initCD - deltaT, 0)

        if not snake:
            for i in range(5):
                addSprite(SnakePiece(i))

        if len(food) < 3 and self.initCD == 0:
            addSprite(Food())

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if not self.altEnterPressed:
            if keys[pygame.K_LALT] and keys[pygame.K_RETURN]:
                self.fullScreen = not self.fullScreen
                windowSurface = pygame.display.set_mode((screenX, screenY), depth=32, display=0, flags=pygame.FULLSCREEN if self.fullScreen else pygame.SHOWN)
                self.altEnterPressed = True

        if not self.fPressed:
            if keys[pygame.K_f]:
                self.showFPS = not self.showFPS
                self.fPressed = True

        if not self.pPressed and not self.gameOver:
            if keys[pygame.K_p]:
                self.pause = not self.pause
                self.pauseBlinkCD = 0
                self.pPressed = True

        if not self.mPressed:
            if self.gameOver and mouseLeft:
                self.reset()

        if not keys[pygame.K_f]: self.fPressed = False
        if not keys[pygame.K_p]: self.pPressed = False
        if not keys[pygame.K_LALT] and not keys[pygame.K_RETURN]: self.altEnterPressed = False
        self.mPressed = mouseLeft

    def draw(self):

        if self.gameOver:
            createText(100,'GAME OVER', 'center',(255,255,255),xper(0.5),yper(0.47))
            createText(50, 'SCORE: %s' %(self.score),'center',(255,255,255),xper(0.5),yper(0.6))
            createText(24,'CLICK TO RESTART','center',(255,0,0),xper(0.5),yper(0.67))
        else:
            createText(24, str(self.score),'topleft',(0,255,0),xper(0.01),yper(0.015))

        if self.pause:
            self.pauseBlinkCD += deltaT
            createText(100,'PAUSE' if self.pauseBlinkCD > 0.25 else '', 'center',(255,255,255),xper(0.5),yper(0.5))
            if self.pauseBlinkCD > 0.5: self.pauseBlinkCD = 0

        if self.showFPS:
            createText(14,'FPS: %s' %(str(round(clock.get_fps()))),'topleft',(255,255,255),xper(0.95),yper(0.01))

    def reset(self):
        while len(sprites) > 1:
            for sprite in sprites:
                if sprite != self:
                    spritesToRemove.append(sprite)
            removeSprites()
        self.gameOver = False
        self.score = 0
        self.initCD = 4

def xper(percentage):
    return percentage * screenX

def yper(percentage):
    return percentage * screenY

def sper(percentage):
    return percentage * (screenX+screenY)/2

def randColorInRange(redLow, redHigh, greenLow, greenHigh, blueLow, blueHigh):
    return (random.randint(redLow,redHigh), random.randint(greenLow,greenHigh), random.randint(blueLow,blueHigh))

def modifyColorPerc(color, offset):
    return tuple(int(max(min(c*offset, 255), 0)) for c in color)

def getAngle2(prevAng, point1, point2):
    angle = math.atan2(point2[1]-point1[1], point2[0]-point1[0])
    if angle - prevAng < -math.pi: angle += math.pi*2
    if angle - prevAng >  math.pi: angle -= math.pi*2
    return angle

def getDist(point1, point2):
    return math.sqrt(abs(point1[0]-point2[0])**2+abs(point1[1]-point2[1])**2)

def createText(size, content, alignment, colorText, posX, posY):
    text_rect = font.get_rect(content, size=size)
    text_rect.midtop = (posX, posY)
    setattr(text_rect, alignment, (posX, posY))
    font.render_to(windowSurface, text_rect, content, colorText, size=size)

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
pygame.mouse.set_visible(False)

font = pygame.freetype.SysFont('Century Gothic', 0)

deltaT = 0
iniT = time.time()
clock = pygame.time.Clock()
keys = None
mouseX = mouseY = 0
mouseLeft = mouseRight = False
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

    windowSurface.fill((0,0,0))
    pygame.draw.circle(windowSurface, (255,255,255), (mouseX, mouseY), 5)

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