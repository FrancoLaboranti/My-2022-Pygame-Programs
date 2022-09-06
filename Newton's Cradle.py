import random
import math
import pygame, sys
from pygame.locals import *

#Set up pygame
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

#Set up the window
windowSurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0 , 32)
pygame.display.set_caption('Newton´s Cradle')

#Set up the colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (180,180,180)
DARKGRAY = (30,30,30)
BROWN = (43,19,0)

def getangle(point1, point2):
    return math.atan2(point2[1]-point1[1], point2[0]-point1[0])

def colision_ryp(caja_x,caja_y,ancho,alto,x,y):
    if x > caja_x and x < caja_x + ancho and y > caja_y and y < caja_y + alto:
        return True
    return False

def colision_circulos(x1, y1, radio1, x2, y2, radio2):
    if math.sqrt((x2-x1)**2 + (y2-y1)**2) < radio1 + radio2:
        return True
    return False


class Ball:
    def __init__(self, nro):
        self.nro = nro
        self.radio = radio
        self.orig_x = SCREEN_WIDTH/2 - total_width/2 + self.radio*2*self.nro
        self.orig_y = SCREEN_HEIGHT/4
        self.angulo = math.pi/2
        self.velocidad = 0
        self.x = self.orig_x
        self.y = self.orig_y + self.radio*15
        self.grabbed = False

    def colisiona(self, ball):
        return self != ball and colision_circulos(self.x, self.y, self.radio, ball.x, ball.y, ball.radio)


balls = []
nro_balls = 5
radio = 30
total_width = (nro_balls - 1) * radio * 2
keypressed = False
mpressed = False
holding = False
ghosted = False

for i in range(nro_balls):
    balls.append(Ball(i))

#Run the game loop
while True:
    
    clock = pygame.time.Clock()
    dt = clock.tick(200)
    windowSurface.fill(BLACK)

    keys = pygame.key.get_pressed()
    mx, my = pygame.mouse.get_pos()
    mleft, mbutton, mright = pygame.mouse.get_pressed()

    if not keypressed:

        if keys[pygame.K_DOWN] and nro_balls > 1:
            nro_balls -= 1
            total_width = (nro_balls - 1) * radio * 2
            balls.clear()
            for i in range(nro_balls):
                balls.append(Ball(i))
            keypressed = True

        if keys[pygame.K_UP] and nro_balls < 10:
            nro_balls += 1
            total_width = (nro_balls - 1) * radio * 2
            balls.clear()
            for i in range(nro_balls):
                balls.append(Ball(i))
            keypressed = True

    if not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
        keypressed = False

    if mright:
        holding = True
    else:
        holding = False

    if mbutton:
        if not mpressed:
            ghosted = not ghosted
            mpressed = True
    else:
        mpressed = False

    for ball in balls:
        if colision_ryp(ball.x-ball.radio,ball.y-ball.radio,ball.radio*2,ball.radio*2,mx,my) and mleft:
            ball.grabbed = True

        if not mleft:
            ball.grabbed = False

        if ball.grabbed:
            ball.angulo = getangle((ball.orig_x, ball.orig_y), (mx, my))
            ball.velocidad = 0

        if not ball.grabbed and not holding:
            if ball.angulo < math.pi/2*1.02:
                ball.velocidad += 0.0002
            if ball.angulo > math.pi/2*0.98:
                ball.velocidad -= 0.0002
            if ball.angulo > math.pi/2*0.95 and ball.angulo < math.pi/2*1.05:
                ball.velocidad *= 0.995
            if ball.angulo > math.pi*255/512 and ball.angulo < math.pi*257/512 and ball.velocidad < 0.0001 and ball.velocidad > -0.0001:
                ball.angulo = math.pi/2
                ball.velocidad = 0
            ball.velocidad *= 0.9999
            ball.angulo += ball.velocidad * dt

        if ball.angulo < 0 and ball.angulo >= -math.pi/2:
            ball.angulo = 0
            ball.velocidad = 0
        if ball.angulo > -math.pi and ball.angulo < -math.pi/2:
            ball.angulo = math.pi
            ball.velocidad = 0

        ball.x = ball.orig_x + math.cos(ball.angulo)*ball.radio*15
        ball.y = ball.orig_y + math.sin(ball.angulo)*ball.radio*15

        if not ghosted:
            for ball2 in balls:
                if ball.colisiona(ball2):
                    vel_ball = ball.velocidad
                    ball.velocidad = ball2.velocidad * 0.99
                    ball2.velocidad = vel_ball * 0.99
                    if ball.nro < ball2.nro:
                        ball.angulo += math.pi * 0.001
                        ball2.angulo -= math.pi * 0.001
                    else:
                        ball.angulo -= math.pi * 0.001
                        ball2.angulo += math.pi * 0.001
        #BALL
        pygame.draw.line(windowSurface, DARKGRAY, (ball.orig_x, ball.orig_y), (ball.x, ball.y), 3)
        pygame.draw.line(windowSurface, DARKGRAY, (ball.orig_x*1.008, ball.orig_y), (ball.x, ball.y), 3)
        pygame.draw.circle(windowSurface, DARKGRAY if ghosted else GRAY, (ball.x, ball.y), ball.radio)
        pygame.draw.circle(windowSurface, GRAY if ghosted else WHITE, (ball.x*1.01, ball.y-(ball.y*0.01)), ball.radio*0.3)

    #ARCH
    pygame.draw.line(windowSurface, BROWN, (SCREEN_WIDTH*1/4, SCREEN_HEIGHT/4), (SCREEN_WIDTH*3/4, SCREEN_HEIGHT/4), 7)
    pygame.draw.line(windowSurface, BROWN, (SCREEN_WIDTH*1/4, SCREEN_HEIGHT/4), (SCREEN_WIDTH*1/4, SCREEN_WIDTH*2/4*1.05), 7)
    pygame.draw.line(windowSurface, BROWN, (SCREEN_WIDTH*3/4, SCREEN_HEIGHT/4), (SCREEN_WIDTH*3/4, SCREEN_WIDTH*2/4*1.05), 7)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
