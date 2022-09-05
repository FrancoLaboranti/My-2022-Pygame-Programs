import pygame, sys, os, random
from pygame.locals import *

pygame.init()
pygame.display.set_caption('Pong')

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
windowSurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0 , 32)

grande = pygame.font.Font(None, 120)
normal = pygame.font.Font(None, 60)
chico = pygame.font.Font(None, 40)

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (128,128,128)

a_cuantos_puntos = ['A 5 puntos','A 10 puntos','A 20 puntos','A 40 puntos','Práctica']
puntos_victoria = [5,10,20,40,None]
opcion_puntos = 1
opcion_menu = 1
fire_mode = 'sí'
apretado = False

j1onfire = False
j2onfire = False
firenet = False

failure = False

gamestates = ['menu','juego','pausa']
gamestate = gamestates[0]

def crear_texto(fuente,texto,color,posx,posy):
	text = fuente.render(texto, True, color, BLACK)
	textRect = text.get_rect()
	textRect.center = (posx, posy)
	windowSurface.blit(text, textRect)

def crear_pelota(ancho_pantalla,alto_pantalla):
	radiopelota = 10
	pelota = [ancho_pantalla/2,
			 random.randint(radiopelota,alto_pantalla-radiopelota),
			 radiopelota,
			 random.randint(-1,1),
			 random.uniform(-0.75,0.75)]
	while pelota[3] == 0:
		pelota[3] = random.randint(-1,1)
	pelota[3] *= random.uniform(0.8,1.2)
	return pelota

def colision_rectangular(rect1_x,rect1_y,ancho1,alto1,rect2_x,rect2_y,ancho2,alto2):
	if rect1_x + ancho1 > rect2_x and rect1_x < rect2_x + ancho2:
		if rect1_y + alto1 > rect2_y and rect1_y < rect2_y + alto2:
			return True
	return False

pelota = crear_pelota(SCREEN_WIDTH,SCREEN_HEIGHT)

while True:

	while gamestate == gamestates[0]:

		altojugador = 110
		jugador1_y = SCREEN_HEIGHT/2-altojugador/2
		jugador2_y = SCREEN_HEIGHT/2-altojugador/2
		veljugador1_y = 0
		veljugador2_y = 0
		j1score = 0
		j1racha = 0
		j2score = 0
		j2racha = 0
		fireball = False
		firetrail = False
		if pelota[0] != SCREEN_WIDTH/2:
			pelota = crear_pelota(SCREEN_WIDTH,SCREEN_HEIGHT)

		windowSurface.fill(BLACK)
		FIRE = (255, random.randint(128,255), 0)
		keys = pygame.key.get_pressed()

		if not apretado:
			if keys[pygame.K_UP] and opcion_menu >1:
				apretado = True

				opcion_menu -= 1

			if keys[pygame.K_DOWN] and opcion_menu <5:
				apretado = True

				opcion_menu += 1

			if keys[pygame.K_RIGHT]:
				apretado = True

				if opcion_menu == 3:
					if opcion_puntos < 4: #para llegar a la ultima y saltear a la primera con el enter opcion_puntos = (opcion_puntos+1) % len(a_cuantos_puntos)
						opcion_puntos += 1
				
				if opcion_menu == 4:
					fire_mode = 'no'

			if keys[pygame.K_LEFT]:
				apretado = True

				if opcion_menu == 3:
					if opcion_puntos > 0:
						opcion_puntos -= 1

				if opcion_menu == 4:
					fire_mode = 'sí'

			if keys[pygame.K_RETURN]:
				apretado = True

				if opcion_menu == 1 or opcion_menu == 2:
					gamestate = gamestates[1]

				if opcion_menu == 5:
					pygame.quit()
					sys.exit()

		if not keys[pygame.K_UP] and not keys[pygame.K_DOWN] and not keys[pygame.K_RETURN] and not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
			apretado = False

		crear_texto(grande,'pong',(random.randint(0,255), random.randint(0,255), random.randint(0,255)),SCREEN_WIDTH/2,SCREEN_HEIGHT*3/24)
		crear_texto(normal,'1 jugador',WHITE if opcion_menu == 1 else GRAY,SCREEN_WIDTH/2,SCREEN_HEIGHT*9/24)
		crear_texto(normal,'2 jugadores',WHITE if opcion_menu == 2 else GRAY,SCREEN_WIDTH/2,SCREEN_HEIGHT*12/24)
		crear_texto(normal,a_cuantos_puntos[opcion_puntos],WHITE if opcion_menu == 3 else GRAY,SCREEN_WIDTH/2,SCREEN_HEIGHT*15/24)
		crear_texto(normal,'Modo Fuego: %s' %(fire_mode),FIRE if fire_mode == 'sí' else WHITE if opcion_menu == 4 and fire_mode == 'no' else GRAY,SCREEN_WIDTH/2,SCREEN_HEIGHT*18/24)
		crear_texto(normal,'Salir',WHITE if opcion_menu == 5 else GRAY,SCREEN_WIDTH/2,SCREEN_HEIGHT*21/24)

		cond_victoria = puntos_victoria[opcion_puntos]

		pygame.display.update()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

	while gamestate == gamestates[1]:

		clock = pygame.time.Clock()
		dt = clock.tick(200)
		windowSurface.fill(BLACK)
		FIRE = (255, random.randint(128,255), 0)
		
	# CONTROLES----------------------------------------------------------------------------------------------------------------------------

		keys = pygame.key.get_pressed()

		if keys[pygame.K_ESCAPE]:
			gamestate = gamestates[0]

		if not apretado:		
			if keys[pygame.K_p] and j1score != cond_victoria and j2score != cond_victoria:
				apretado = True

				gamestate = gamestates[2]

		if keys[pygame.K_UP]:
			veljugador1_y -= 0.1
			if j1onfire:
				veljugador1_y -= 0.2

		if keys[pygame.K_DOWN]:
			veljugador1_y += 0.1
			if j1onfire:
				veljugador1_y += 0.2

		if opcion_menu == 2:
			if keys[pygame.K_w]:
				veljugador2_y -= 0.1
				if j2onfire:
					veljugador2_y -= 0.2

			if keys[pygame.K_s]:
				veljugador2_y += 0.1
				if j2onfire:
					veljugador2_y += 0.2

		if not keys[pygame.K_p]:
			apretado = False

	# AI-----------------------------------------------------------------------------------------------------------------------------------	

		if opcion_menu == 1:

			failtest = random.random()

			if failtest < 0.2:
				failure = False
			if failtest > 0.6:
				failure = True

			if not failure:
				if pelota[1] < jugador2_y + altojugador/2:
					veljugador2_y -= 0.1
					if j2onfire:
						veljugador2_y -= 0.2

				if pelota[1] > jugador2_y + altojugador/2:
					veljugador2_y += 0.1
					if j2onfire:
						veljugador2_y += 0.2

			if failure:
				if pelota[1] < jugador2_y + altojugador/2 - 125:
					veljugador2_y -= 0.1
					if j2onfire:
						veljugador2_y -= 0.2
				if pelota[1] > jugador2_y + altojugador/2 + 125:
					veljugador2_y += 0.1
					if j2onfire:
						veljugador2_y += 0.2

	# MOVIMIENTO/PUNTOS---------------------------------------------------------------------------------------------------------------------

		pelota[0] += pelota[3] * dt
		pelota[1] += pelota[4] * dt
		jugador1_y += veljugador1_y * dt
		jugador2_y += veljugador2_y * dt

		if jugador1_y < 0:
			jugador1_y = 0
			veljugador1_y = 0
		if jugador1_y > SCREEN_HEIGHT - altojugador:
			jugador1_y = SCREEN_HEIGHT - altojugador
			veljugador1_y = 0

		if jugador2_y < 0:
			jugador2_y = 0
			veljugador2_y = 0
		if jugador2_y > SCREEN_HEIGHT - altojugador:
			jugador2_y = SCREEN_HEIGHT - altojugador
			veljugador2_y = 0

		if colision_rectangular(SCREEN_WIDTH-20,jugador1_y, 15, altojugador,pelota[0]-pelota[2],pelota[1]-pelota[2],pelota[2]*2,pelota[2]*2):
			if j1onfire:
				pelota[3] *= 1.25
				pelota[4] += veljugador1_y/4
				fireball = True
				firetrail = True
			if not j1onfire:
				firetrail = False
			if pelota[0] > SCREEN_WIDTH-20 - pelota[2]:
				pelota[0] = SCREEN_WIDTH-20 - pelota[2] #correccion bug que se trababa la pelota en la paleta dandole justo con el borde
			if veljugador1_y < 1:
				pelota[4] *= 0.5
			pelota[3] = -pelota[3] * 1.05
			pelota[4] += veljugador1_y/3

		if colision_rectangular(5,jugador2_y, 15, altojugador,pelota[0]-pelota[2],pelota[1]-pelota[2],pelota[2]*2,pelota[2]*2):
			if j2onfire:
				pelota[3] *= 1.25
				pelota[4] += veljugador1_y/4 #le damos jugabilidad al movimiento de la pelota cuando rebotan con las paletas
				fireball = True
				firetrail = True
			if not j2onfire:
				firetrail = False				
			if pelota[0] < 20 + pelota[2]:
				pelota[0] = 20 + pelota[2]		
			if veljugador2_y < 1:
				pelota[4] *= 0.5		
			pelota[3] = -pelota[3] * 1.05
			pelota[4] += veljugador2_y/3

		if pelota[1] > SCREEN_HEIGHT - pelota[2]:
			pelota[1] = SCREEN_HEIGHT - pelota[2]
			pelota[4] *= 1.10	#modificador a vel_y de pelota para evitar que se estanque en los bordes sup e inf de la pantalla
			pelota[4] = -pelota[4]
		if pelota[1] < pelota[2]:
			pelota[1] = pelota[2]
			pelota[4] *= 1.10
			pelota[4] = -pelota[4]

		if pelota[0] > SCREEN_WIDTH + 200 - pelota[2]:
			pelota = crear_pelota(SCREEN_WIDTH,SCREEN_HEIGHT)
			j2score += 1
			j2racha += 1
			j1racha = 0
			fireball = False
			firetrail = False

		if pelota[0] < - 200  + pelota[2]:
			pelota = crear_pelota(SCREEN_WIDTH,SCREEN_HEIGHT)
			j1score += 1
			j1racha += 1
			j2racha = 0
			fireball = False
			firetrail = False

		if j1racha >= 3 and fire_mode == 'sí':
			j1onfire = True
		if j1racha < 3:
			j1onfire = False
		if j2racha >= 3 and fire_mode == 'sí':
			j2onfire = True
		if j2racha < 3:
			j2onfire = False

		if pelota[3] > 2:
			pelota[3] = 2
		elif pelota[3] < -2:
			pelota[3] = -2
		
		if pelota[4] > 1.25:
			pelota[4] = 1.25
		elif pelota[4] < -1.25:
			pelota[4] = -1.25  #limitamos la velocidad maxima de la pelota

		veljugador1_y *= 0.97
		if j1onfire:
			veljugador1_y *= 0.93
		
		veljugador2_y *= 0.97
		if j2onfire:
			veljugador2_y *= 0.93

	# DIBUJO--------------------------------------------------------------------------------------------------------------------------------

		pygame.draw.rect(windowSurface, FIRE if j1onfire else WHITE, pygame.Rect(SCREEN_WIDTH-20,jugador1_y, 15, altojugador))
		if j1onfire:
			crear_texto(chico,'ON FIRE!',FIRE,SCREEN_WIDTH-85,20)

		pygame.draw.rect(windowSurface, FIRE if j2onfire else WHITE, pygame.Rect(5,jugador2_y, 15, altojugador))
		if j2onfire:
			crear_texto(chico,'ON FIRE!',FIRE,85,20)

		if fireball and pelota[0] > SCREEN_WIDTH/2-10 and pelota[0] < SCREEN_WIDTH/2+10:
			firenet = True
		if not fireball:
			firenet = False

		if opcion_puntos != 4:
			crear_texto(chico,str(j1score),FIRE if firenet else WHITE,SCREEN_WIDTH/2+30,20)
			crear_texto(chico,str(j2score),FIRE if firenet else WHITE,SCREEN_WIDTH/2-30,20)

		if j1score == cond_victoria:
			crear_texto(grande,'¡GANA JUGADOR 1!',(random.randint(0,255), random.randint(0,255), random.randint(0,255)),SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
			pelota[0] = SCREEN_WIDTH/2 + 40
			pelota[1] = 60

		if j2score == cond_victoria:
			crear_texto(grande,'¡GANA JUGADOR 2!',(random.randint(0,255), random.randint(0,255), random.randint(0,255)),SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
			pelota[0] = SCREEN_WIDTH/2 - 40
			pelota[1] = 60

		pygame.draw.line(windowSurface, FIRE if firenet else WHITE,(SCREEN_WIDTH/2-1, 0),(SCREEN_WIDTH/2-1, SCREEN_HEIGHT), 6 if firenet else 2)

		pygame.draw.circle(windowSurface, FIRE if fireball else WHITE, (pelota[0], pelota[1]), pelota[2])
		if firetrail:
			for i in range(1,5):
				pygame.draw.circle(windowSurface, FIRE, (pelota[0]-pelota[3]*8*i, pelota[1]-pelota[4]*8*i), pelota[2]-(2*i))

		while gamestate == gamestates[2]:

			keys = pygame.key.get_pressed()

			if keys[pygame.K_ESCAPE]:
				gamestate = gamestates[0]

			if not apretado:
				if keys[pygame.K_p]:
					apretado = True

					gamestate = gamestates[1]

			if not keys[pygame.K_p]:
				apretado = False

			crear_texto(grande,'PAUSA',WHITE,SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
			
			pygame.display.update()

			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()

		pygame.display.update()

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()