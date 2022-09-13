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
        self.x = xper(0.5) if self.id == 0 else snake[self.id-1].x
        self.y = yper(0.5) if self.id == 0 else snake[self.id-1].y
        self.color = (255,200,0) if self.id % 50 == 0 else (0,0,0) if self.id % 10 == 0 else randColorInRange(0,20,30,60,0,20)

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
            self.x += math.cos(self.ang)*self.vel*deltaT
            self.y += math.sin(self.ang)*self.vel*deltaT

    def draw(self):

        pygame.draw.circle(windowSurface, self.color, (self.x, self.y), self.radius)

        if self.id == 0:
            eye1 = self.x + math.cos(self.ang) * self.radius*0.4 + math.cos(self.ang + math.pi/2) * self.radius*0.5, self.y + math.sin(self.ang) * self.radius*0.4 + math.sin(self.ang + math.pi/2) * self.radius*0.5
            eye2 = self.x + math.cos(self.ang) * self.radius*0.4 - math.cos(self.ang + math.pi/2) * self.radius*0.5, self.y + math.sin(self.ang) * self.radius*0.4 - math.sin(self.ang + math.pi/2) * self.radius*0.5
            pupil1 = self.x + math.cos(self.ang) * self.radius*0.55 + math.cos(self.ang + math.pi/2) * self.radius*0.5, self.y + math.sin(self.ang) * self.radius*0.55 + math.sin(self.ang + math.pi/2) * self.radius*0.5
            pupil2 = self.x + math.cos(self.ang) * self.radius*0.55 - math.cos(self.ang + math.pi/2) * self.radius*0.5, self.y + math.sin(self.ang) * self.radius*0.55 - math.sin(self.ang + math.pi/2) * self.radius*0.5
            pygame.draw.circle(windowSurface, (255,255,255), eye1, self.radius*0.4)
            pygame.draw.circle(windowSurface, (100,0,0), pupil1, self.radius*0.2)
            pygame.draw.circle(windowSurface, (255,255,255), eye2, self.radius*0.4)
            pygame.draw.circle(windowSurface, (100,0,0), pupil2, self.radius*0.2)

    def checkHeadCol(self):

        for piece in snake:
            if piece.id > 5 and piece.id % 3 == 0:
                if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*2:
                    manager[0].gameOver = True

        for piece in food:
            if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*2:
                if not piece.grabbed:
                    piece.grabbed = True
                    manager[0].score += 100
                    for i in range(10):
                        addSprite(SnakePiece(len(snake)))

class Food(Sprite):

    def __init__(self):

        self.z = -1
        self.ang = random.uniform(0,math.pi*2)
        self.staticAng = random.uniform(0,math.pi*2)
        self.angVel = sper(0.03)
        self.vel = random.uniform(sper(0.01),sper(0.02))
        self.radius = sper(0.002)
        self.glowCD = 1
        self.grabbed = False
        self.timer = 10

        reroll = True
        while reroll:
            self.x, self.y = random.randint(xper(0.1),screenX-xper(0.1)), random.randint(yper(0.1),screenY-yper(0.1))
            reroll = False
            for piece in snake:
                if getDist((piece.x,piece.y),(self.x,self.y)) < self.radius*20:
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
                self.radius -= deltaT*25
            elif self.radius < sper(0.01):
                self.radius += deltaT*25

            if self.radius < sper(0.002):
                spritesToRemove.append(self)

            self.ang += self.angVel * deltaT
            self.x += math.cos(self.staticAng)*self.vel * deltaT
            self.y += math.sin(self.staticAng)*self.vel * deltaT

    def draw(self):

        color = (255,255,255) if self.glowCD <= 0.1 else (125,0,0)
        for i in range(10):
            pygame.draw.line(windowSurface, modifyColorPerc(color,1+i*0.11),(self.x + math.cos(self.ang - math.pi/2) * self.radius*(1-i*0.2), self.y + math.sin(self.ang - math.pi/2) * self.radius*(1-i*0.2)), (self.x + math.cos(self.ang) * self.radius*(1-i*0.2), self.y + math.sin(self.ang) * self.radius*(1-i*0.2)), int(self.radius/4))
        pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang) * self.radius, self.y + math.sin(self.ang) * self.radius), (self.x + math.cos(self.ang + math.pi/2) * self.radius, self.y + math.sin(self.ang + math.pi/2) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang + math.pi/2) * self.radius, self.y + math.sin(self.ang + math.pi/2) * self.radius), (self.x - math.cos(self.ang) * self.radius, self.y - math.sin(self.ang) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, color, (self.x - math.cos(self.ang) * self.radius, self.y - math.sin(self.ang) * self.radius), (self.x + math.cos(self.ang - math.pi/2) * self.radius, self.y + math.sin(self.ang - math.pi/2) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang - math.pi/2) * self.radius, self.y + math.sin(self.ang - math.pi/2) * self.radius), (self.x + math.cos(self.ang) * self.radius, self.y + math.sin(self.ang) * self.radius), int(self.radius/4))

class Explosion(Sprite):

    def __init__(self,x,y,radius,isChild):

        self.z = -2
        self.x = x
        self.y = y
        self.startRadius = radius
        self.radius = self.startRadius
        self.isChild = isChild
        self.type = random.randint(0,1)
        self.color = randColorInRange(155,255,155,255,155,255)

    def process(self):

        if not manager[0].gameOver and not manager[0].pause:
            self.radius += deltaT*60
            if self.radius > self.startRadius*13:
                spritesToRemove.append(self)
                if not self.isChild:
                    for i in range(3):
                        addSprite(Explosion(self.x+random.uniform(-sper(0.15),sper(0.15)),self.y+random.uniform(-sper(0.15),sper(0.15)),self.startRadius*(random.uniform(0.5,0.7)),True))

    def draw(self):

        e1 = random.uniform(0,3)
        for i in range(1,31):
            e2 = random.uniform(0,3)
            e = (e1 if self.type == 0 else e2)
            lineStart = self.x + math.cos(math.pi*2*((i+10)/30)) * self.radius*e, self.y + math.sin(math.pi*2*((i+10)/30)) * self.radius*e
            lineEnd = self.x + math.cos(math.pi*2*i/30) * self.radius*e, self.y + math.sin(math.pi*2*i/30) * self.radius*e
            pygame.draw.line(windowSurface,self.color,lineStart,lineEnd, int(self.radius/7))

class Manager(Sprite):

    def __init__(self):

        self.z = -3
        self.showFPS = False
        self.fPressed = False
        self.pPressed = False
        self.gameOver = False
        self.score = 0
        self.pause = False
        self.pauseBlinkCD = 0
        self.roundStartCD = 2

        manager.append(self)

    def process(self):

        self.roundStartCD = max(self.roundStartCD - deltaT, 0)

        if not snake:
            for i in range(5):
                addSprite(SnakePiece(i))

        if len(food) < 3 and self.roundStartCD == 0:
            addSprite(Food())

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

        if self.gameOver and (mouseLeft or keys[pygame.K_RETURN]):
            self.reset()

        if not keys[pygame.K_f]: self.fPressed = False
        if not keys[pygame.K_p]: self.pPressed = False

    def draw(self):

        createTextLeft(tFont,'Score: %s' %(self.score),(255,255,255),None,xper(0.01),yper(0.02))
        for i in range(5):
            pygame.draw.circle(windowSurface,(100*(1+i*0.2),100*(1+i*0.2),min(255*(1+i*0.2),255)),(mouseX,mouseY),sper(0.0075)*(1-i*0.2))

        if self.gameOver:
            createTextCenter(bFont,'GAME OVER',(255,255,255),None,xper(0.5),yper(0.45))
            createTextCenter(mFont,'Click to Restart',(0,255,255),None,xper(0.5),yper(0.55))

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
        self.roundStartCD = 2

def xper(percentage):
    return percentage * screenX

def yper(percentage):
    return percentage * screenY

def sper(percentage):
    return percentage * (screenX+screenY)/2

def randColor():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

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
                if sprite.grabbed:
                    addSprite(Explosion(sprite.x,sprite.y,sprite.radius,False))
            sprites.remove(sprite)
            spritesToRemove.remove(sprite)

# INITIALIZATION .....................................................................

pygame.init()

screenX = 1280
screenY = 720
windowSurface = pygame.display.set_mode((screenX, screenY), depth=32, display=0)
# windowSurface = pygame.display.set_mode((screenX, screenY), depth=32, display=0, flags=pygame.FULLSCREEN)
pygame.display.set_caption('Snake')

bFont = pygame.font.Font(None, int(sper(0.128)))
mFont = pygame.font.Font(None, int(sper(0.0512)))
tFont = pygame.font.Font(None, int(sper(0.0192)))

pygame.mouse.set_visible(False)

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

    windowSurface.fill((0,5,0))

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