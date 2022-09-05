import datetime, time
import math
import pygame, sys
from pygame.locals import *

#Set up pygame
pygame.init()

SCREEN_WIDTH = 650
SCREEN_HEIGHT = 650

#Set up the window
windowSurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0 , 32)
pygame.display.set_caption('Clock')


#Set up the colors
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
DARKGREEN = (0,180,0)
BLUE = (0,0,255)
WHITE = (255,255,255)

radio = (SCREEN_WIDTH+SCREEN_HEIGHT) / 4.25
centro_x = SCREEN_WIDTH / 2
centro_y = SCREEN_HEIGHT / 2
pressed = False
segundero = 0
fuente = pygame.font.Font(None, 30)

def crear_texto(fuente,texto,color,posx,posy):
    text = fuente.render(texto, True, color, BLACK)
    textRect = text.get_rect()
    textRect.center = (posx, posy)
    windowSurface.blit(text, textRect)

#Run the game loop
while True:

    lmb = pygame.mouse.get_pressed()[0]

    if not pressed:
        if lmb:
            pressed = True
            if segundero == 0:
                segundero = 1
            elif segundero == 1:
                segundero = 0

    if not lmb:
        pressed = False

    time = datetime.datetime.now()

    ca_h = time.hour
    ca_m = time.minute
    ca_s = time.second
    ca_ms = time.microsecond

    windowSurface.fill(BLACK)
    for i in range(1,61):
        pygame.draw.line(windowSurface,DARKGREEN, (centro_x + math.cos(math.pi*2*i/60)*radio*0.83, centro_y + math.sin(math.pi*2*i/60)*radio*0.83),(centro_x + math.cos(math.pi*2*i/60)*radio*0.85, centro_y + math.sin(math.pi*2*i/60)*radio*0.85),3)
    for i in range(1,13):
        pygame.draw.line(windowSurface,GREEN, (centro_x + math.cos(math.pi*2*i/12)*radio*0.81, centro_y + math.sin(math.pi*2*i/12)*radio*0.81),(centro_x + math.cos(math.pi*2*i/12)*radio*0.86, centro_y + math.sin(math.pi*2*i/12)*radio*0.86),9)

    pygame.draw.circle(windowSurface, DARKGREEN, (centro_x, centro_y), radio, 30)

    crear_texto(fuente,time.strftime("%a, %d %b %Y"),DARKGREEN,centro_x,centro_y+SCREEN_HEIGHT*5/16*0.875)
    crear_texto(fuente,time.strftime("%H:%M:%S"),GREEN,centro_x,centro_y+SCREEN_HEIGHT*5/16)
    crear_texto(fuente,time.strftime("%a, %d %b %Y"),DARKGREEN,centro_x,centro_y-SCREEN_HEIGHT*5/16*0.875)
    crear_texto(fuente,time.strftime("%H:%M:%S"),GREEN,centro_x,centro_y-SCREEN_HEIGHT*5/16)

    pygame.draw.line(windowSurface,DARKGREEN, (centro_x, centro_y),(centro_x + math.cos(ca_m*math.pi*2/60-math.pi/2)*radio*0.70,centro_y + math.sin(ca_m*math.pi*2/60-math.pi/2)*radio*0.70),12)
    pygame.draw.line(windowSurface,DARKGREEN, (centro_x, centro_y),(centro_x + math.cos((ca_h*60+ca_m)*math.pi*2/720-math.pi/2)*radio*0.50,centro_y + math.sin((ca_h*60+ca_m)*math.pi*2/720-math.pi/2)*radio*0.50),20)

    pygame.draw.circle(windowSurface, GREEN, (centro_x, centro_y), radio*0.05)

    if segundero == 0:
        pygame.draw.line(windowSurface,GREEN, (centro_x-math.cos(ca_s*math.pi*2/60-math.pi/2)*radio*0.075, centro_y-math.sin(ca_s*math.pi*2/60-math.pi/2)*radio*0.075),(centro_x - math.cos(ca_s*math.pi*2/60-math.pi/2)*radio*0.15,centro_y - math.sin(ca_s*math.pi*2/60-math.pi/2)*radio*0.15),9)
        pygame.draw.line(windowSurface,GREEN, (centro_x-math.cos(ca_s*math.pi*2/60-math.pi/2)*radio*0.075, centro_y-math.sin(ca_s*math.pi*2/60-math.pi/2)*radio*0.075),(centro_x + math.cos(ca_s*math.pi*2/60-math.pi/2)*radio*0.75,centro_y + math.sin(ca_s*math.pi*2/60-math.pi/2)*radio*0.75),6)
    if segundero == 1:
        pygame.draw.line(windowSurface,GREEN, (centro_x-math.cos((ca_ms+ca_s*999999)*math.pi*2/(60*999999)-math.pi/2)*radio*0.075, centro_y-math.sin((ca_ms+ca_s*999999)*math.pi*2/(60*999999)-math.pi/2)*radio*0.075),(centro_x + math.cos((ca_ms+ca_s*999999)*math.pi*2/(60*999999)-math.pi/2)*radio*0.75,centro_y + math.sin((ca_ms+ca_s*999999)*math.pi*2/(60*999999)-math.pi/2)*radio*0.75),6)
        pygame.draw.line(windowSurface,GREEN, (centro_x-math.cos((ca_ms+ca_s*999999)*math.pi*2/(60*999999)-math.pi/2)*radio*0.075, centro_y-math.sin((ca_ms+ca_s*999999)*math.pi*2/(60*999999)-math.pi/2)*radio*0.075),(centro_x - math.cos((ca_ms+ca_s*999999)*math.pi*2/(60*999999)-math.pi/2)*radio*0.15,centro_y - math.sin((ca_ms+ca_s*999999)*math.pi*2/(60*999999)-math.pi/2)*radio*0.15),9)
   
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

