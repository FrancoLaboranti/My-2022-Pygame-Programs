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

class Tank(Sprite):

    def __init__(self, i, playermode, track, racelength, difficulty):
        self.id = i
        self.radius = xper(0.01)
        self.vel = 0
        self.ang_vel = 0
        self.shoot_cooling = 0
        self.lap_progress = 0
        self.lap_checkpoint = 0
        self.laps = 0
        self.track = track
        self.rank = 0
        self.racetime = 0
        self.racelength = 10 if racelength == 0 else 20 if racelength == 1 else 40
        self.start = False
        self.pause = False
        self.finished = False
        self.wrongway = False
        self.wrongwayalert_timer = 1 
        self.wrongwayalert_cooling = 0
        self.wrongwayalert_showing = 0
        self.ai = False if self.id == 0 else False if self.id == 1 and playermode == 1 else True
        self.ai_difficulty = difficulty
        self.ai_timer = 1
        self.ai_cooling = 1
        self.ai_acel = 0
        self.ai_turn = 0
        self.ai_shoot = 0
        self.showhitbox = False

        startpos = (
            ((xper(0.25),yper(0.07),0),(xper(0.21),yper(0.11),0),(xper(0.25),yper(0.15),0),(xper(0.21),yper(0.19),0)),
            ((xper(0.68),yper(0.83),0),(xper(0.64),yper(0.87),0),(xper(0.68),yper(0.91),0),(xper(0.64),yper(0.95),0)),
            ((xper(0.97),yper(0.4),math.pi/2),(xper(0.95),yper(0.34),math.pi/2),(xper(0.93),yper(0.4),math.pi/2),(xper(0.91),yper(0.34),math.pi/2)),
            ((xper(0.54),yper(0.57),-math.pi/2),(xper(0.56),yper(0.63),-math.pi/2),(xper(0.58),yper(0.57),-math.pi/2),(xper(0.6),yper(0.63),-math.pi/2)),
            ((xper(0.56),yper(0.05),math.pi),(xper(0.6),yper(0.09),math.pi),(xper(0.56),yper(0.13),math.pi),(xper(0.6),yper(0.17),math.pi)),
            ((xper(0.36),yper(0.86),math.pi),(xper(0.4),yper(0.89),math.pi),(xper(0.36),yper(0.92),math.pi),(xper(0.4),yper(0.95),math.pi)),
            ((xper(0.05),yper(0.65),-math.pi/2),(xper(0.07),yper(0.72),-math.pi/2),(xper(0.09),yper(0.65),-math.pi/2),(xper(0.11),yper(0.72),-math.pi/2)),
            ((xper(0.46),yper(0.32),0),(xper(0.42),yper(0.36),0),(xper(0.46),yper(0.4),0),(xper(0.42),yper(0.44),0)),
            ((xper(0.9),yper(0.07),math.pi),(xper(0.94),yper(0.11),math.pi),(xper(0.9),yper(0.15),math.pi),(xper(0.94),yper(0.19),math.pi)),
            ((xper(0.75),yper(0.72),math.pi),(xper(0.79),yper(0.72),math.pi),(xper(0.83),yper(0.72),math.pi),(xper(0.87),yper(0.72),math.pi))
        )

        self.start_x, self.start_y, self.start_ang = startpos[self.track][self.id]
        self.x, self.y, self.ang = self.start_x, self.start_y, self.start_ang

        colors = (
            (150,0,0),
            (50,50,255),
            (75,0,75),
            (200,155,0)
        )

        self.color = colors[self.id]

        controls = (
            (pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT,pygame.K_SPACE),
            (pygame.K_w,pygame.K_s,pygame.K_a,pygame.K_d,pygame.K_LCTRL)
        )

        if not self.ai: self.forward, self.reverse, self.left, self.right, self.shoot = controls[self.id]

        tanks.append(self)

    def process(self):

        if self.start and not self.pause:

            self.pre_lap_progress = self.lap_progress
            self.shoot_cooling = max(self.shoot_cooling - deltaT, 0)

            if not self.finished:
                self.rank = len(tanks)
                self.racetime += deltaT

            if not self.ai:
                if keys[self.forward]: self.vel += 2.5
                if keys[self.reverse]: self.vel -= 1.5
                if keys[self.left]: self.ang_vel -= 0.2
                if keys[self.right]: self.ang_vel += 0.2
                if keys[self.shoot] and self.shoot_cooling == 0:
                    add_sprite(Bomb(self.color, self.radius, self.x, self.y, self.ang, self.vel))
                    self.shoot_cooling = 2

            else:
                self.ai_cooling += deltaT
                if self.ai_cooling > self.ai_timer:
                    self.ai_acel = random.uniform(2,2.15) if self.ai_difficulty == 0 else random.uniform(2.15,2.35) if self.ai_difficulty == 1 else random.uniform(2.35,2.5) if self.ai_difficulty == 2 else random.uniform(2.5,2.65)
                    self.ai_turn = random.uniform(0.1,0.125) if self.ai_difficulty == 0 else random.uniform(0.125,0.175) if self.ai_difficulty == 1 else random.uniform(0.175,0.2) if self.ai_difficulty == 2 else random.uniform(0.2,0.225)
                    self.ai_shoot = random.randint(0,19) if self.ai_difficulty == 0 else random.randint(0,9) if self.ai_difficulty == 1 else random.randint(0,4) if self.ai_difficulty == 2 else random.randint(0,1)
                    self.ai_cooling = 0

            closest_point = None
            closest_dist = xper(0.3)

            if trackpoints:

                for point in trackpoints:
                    point_dist = getdist((self.x,self.y),(point.x,point.y))
                    if point_dist < closest_dist:
                        closest_dist = point_dist
                        closest_point = point

                closest_point.color = modify_color_perc(self.color,1.5)
                self.lap_progress = closest_point.id*100/len(trackpoints)

                if self.ai:
                    target_point = trackpoints[(closest_point.id+8)%len(trackpoints)]
                    target_point.color = (0,150,0)
                    point_ang = getangle2(self.ang,(self.x,self.y),(target_point.x,target_point.y))

                    if point_ang - self.ang > -math.pi/12 and point_ang - self.ang < math.pi/12:
                        self.vel += self.ai_acel if not self.finished else self.ai_acel*0.6
                    if point_ang < self.ang: self.ang_vel -= self.ai_turn
                    if point_ang > self.ang: self.ang_vel += self.ai_turn
                    if self.ai_shoot == 0 and self.shoot_cooling == 0 and not self.finished:
                        add_sprite(Bomb(self.color, self.radius, self.x, self.y, self.ang, self.vel))
                        self.shoot_cooling = 2

            self.ang += self.ang_vel * deltaT if SCREEN_X >= 1000 else self.ang_vel * xper(0.0017) * deltaT
            self.x += math.cos(self.ang)*self.vel * deltaT if SCREEN_X >= 1400 else math.cos(self.ang)*self.vel * xper(0.0007) * deltaT if SCREEN_X >= 1000 else math.cos(self.ang)*self.vel * xper(0.0003) * deltaT
            self.y += math.sin(self.ang)*self.vel * deltaT if SCREEN_X >= 1400 else math.sin(self.ang)*self.vel * xper(0.0007) * deltaT if SCREEN_X >= 1000 else math.sin(self.ang)*self.vel * xper(0.0003) * deltaT
            self.ang_vel *= 0.95 if SCREEN_X >= 1000 else 0.92 if SCREEN_X >= 500 else 0.9
            self.vel *= 0.9975 if SCREEN_X >= 1000 else 0.999

            if self.ang > math.pi*2 or self.ang < -math.pi*2: self.ang = 0
            if self.x > SCREEN_X+self.radius: self.x = 0-self.radius
            if self.x < 0-self.radius: self.x = SCREEN_X+self.radius
            if self.y > SCREEN_Y+self.radius: self.y = 0-self.radius
            if self.y < 0-self.radius: self.y = SCREEN_Y+self.radius

            if self.lap_progress > 0 and self.lap_progress < 5: self.lap_checkpoint = 1
            if self.lap_progress > 95 and self.lap_progress < 100 and self.lap_checkpoint == 1: self.lap_checkpoint = 2
            if self.lap_progress == 0:
                if self.lap_checkpoint == 2:
                    if not self.finished: self.laps += 1
                self.lap_checkpoint = 0

            for tank in tanks:
                if tank != self:
                    if not self.finished and not tank.finished:
                        if rect_colision((tank.x-tank.radius*0.75, tank.y-tank.radius*0.75, tank.radius*1.5, tank.radius*1.5),(self.x-self.radius*0.75, self.y-self.radius*0.75, self.radius*1.5, self.radius*1.5)):

                            hit_ang = getangle((self.x,self.y),(tank.x,tank.y))

                            self.x -= math.cos(hit_ang)*2
                            self.y -= math.sin(hit_ang)*2
                            self.vel *= 0.9
                            
                            tank.x += math.cos(hit_ang)*2
                            tank.y += math.sin(hit_ang)*2

                        if self.laps > tank.laps: self.rank -= 1
                        elif self.laps == tank.laps and self.lap_progress > tank.lap_progress and self.lap_checkpoint != 0: self.rank -= 1
                        elif self.laps == tank.laps and self.lap_progress <= tank.lap_progress and tank.lap_checkpoint == 0: self.rank -= 1
            
            if closest_point != None and closest_point.id != 0:
                if self.lap_progress < self.pre_lap_progress: 
                    self.wrongway = True
                if self.lap_progress > self.pre_lap_progress: 
                    self.wrongway = False

            if self.laps == self.racelength:
                self.finished = True
                self.ai = True

    def draw(self):

        lines = 17
        for layer in range(2):
            for i in range(lines):
                x = self.x + math.cos(self.ang + math.pi/2) * (-self.radius + 2*self.radius*(i/lines) + ((self.radius*2) / lines-1)/2)
                y = self.y + math.sin(self.ang + math.pi/2) * (-self.radius + 2*self.radius*(i/lines) + ((self.radius*2) / lines-1)/2)
                length = self.radius * 0.7 if abs(i - lines // 2) < lines * 0.2 else self.radius
                if layer == 0:
                    pygame.draw.line(windowSurface, modify_color_perc(modify_color(self.color, -50), 0.35) if self.finished else modify_color(self.color, -50), (x + math.cos(self.ang) * -length, y + math.sin(self.ang) * -length), (x + math.cos(self.ang) * length, y + math.sin(self.ang) * length), max(int((self.radius*5) / lines-1), 1))
                else:
                    pygame.draw.line(windowSurface, modify_color_perc(self.color, 0.35) if self.finished else self.color, (x + math.cos(self.ang) * -length, y + math.sin(self.ang) * -length), (x + math.cos(self.ang) * length, y + math.sin(self.ang) * length), max(int((self.radius*2) / lines-1), 1))

        pygame.draw.circle(windowSurface, modify_color_perc(modify_color(self.color, -25), 0.35) if self.finished else modify_color(self.color, -25), (self.x, self.y), self.radius * 0.7)
        pygame.draw.line(windowSurface, modify_color_perc(modify_color(self.color, 25), 0.35) if self.finished else modify_color(self.color, 25), (self.x, self.y), (self.x + math.cos(self.ang) * self.radius * 1.5, self.y + math.sin(self.ang) * self.radius * 1.5), int(self.radius * 0.3))
        pygame.draw.circle(windowSurface, modify_color_perc(modify_color(self.color, 75), 0.35) if self.finished else modify_color(self.color, 75), (self.x, self.y), self.radius * 0.5)
        pygame.draw.circle(windowSurface, modify_color_perc(modify_color(self.color, 25), 0.35) if self.finished else modify_color(self.color, 25), (self.x, self.y), self.radius * 0.5, 1)

        if self.showhitbox: pygame.draw.rect(windowSurface, (255,255,0), pygame.Rect(self.x-self.radius*0.75, self.y-self.radius*0.75, self.radius*1.5, self.radius*1.5))
        if self.racetime > 1: create_text(RS_font if SCREEN_X < 1000 else S_font,'%s - %s/%s'%("1st" if self.rank == 1 else "2nd" if self.rank == 2 else "3rd" if self.rank == 3 else "4th",min(self.laps+1,self.racelength),self.racelength),modify_color(self.color,100),modify_color(self.color,-50),xper(0.03) if self.rank == 1 else xper(0.09) if self.rank == 2 else xper(0.15) if self.rank == 3 else xper(0.21),yper(0.01))
        if self.finished: create_text(RS_font if SCREEN_X < 1000 else S_font,'%s'%("1st!" if self.rank == 1 else "2nd!" if self.rank == 2 else "3rd" if self.rank == 3 else "4th"),modify_color(self.color,150),None,self.x,self.y-self.radius*2)

        if self.wrongway:
            if not self.pause: self.wrongwayalert_cooling += deltaT

            if self.wrongwayalert_cooling > self.wrongwayalert_timer:
                create_text(RS_font if SCREEN_X < 1000 else S_font,'Wrong Way!',modify_color(self.color,150),None,self.x,self.y+self.radius*1.5)
                if not self.pause: self.wrongwayalert_showing += deltaT

                if self.wrongwayalert_showing > self.wrongwayalert_timer:
                    self.wrongwayalert_cooling = 0
                    self.wrongwayalert_showing = 0

class Bomb(Sprite):

    def __init__(self, tank_color, tank_radius, tank_x, tank_y, tank_ang, tank_vel):
        self.color, self.radius, self.x, self.y, self.ang, self.vel = tank_color, tank_radius*0.3, tank_x, tank_y, tank_ang, max(tank_vel*2,1000)
        self.pause = False
        bombs.append(self)

    def process(self):

        if not self.pause:
            self.x += math.cos(self.ang)*self.vel*deltaT
            self.y += math.sin(self.ang)*self.vel*deltaT

            for tank in tanks:
                if tank.color != self.color and not tank.finished and rect_colision((self.x-self.radius*0.75, self.y-self.radius*0.75, self.radius*1.5, self.radius*1.5),(tank.x-tank.radius*0.75, tank.y-tank.radius*0.75, tank.radius*1.5, tank.radius*1.5)):
                    if random.randint(0,1) == 0:
                        tank.ang_vel -= 300
                    else:
                        tank.ang_vel += 300
                    tank.vel *= 0.1
                    bombs.remove(self)
                    sprites.remove(self)

            if self.x > SCREEN_X+self.radius or self.x < 0-self.radius or self.y > SCREEN_Y+self.radius or self.y < 0-self.radius:
                bombs.remove(self)
                sprites.remove(self)

    def draw(self):

        pygame.draw.circle(windowSurface,modify_color_perc(self.color,1.5),(self.x,self.y),self.radius)

class Wall(Sprite):

    def __init__(self, i, track, color):
        self.id = i
        self.track = track
        self.color = color

        maps = (
            ((0,0,xper(0.01),yper(1)),(0,0,xper(1),xper(0.01)),(xper(1)-xper(0.01),0,xper(0.02),yper(1)),(0,yper(1)-xper(0.01),xper(1),xper(0.02)),(xper(0.15),yper(0.25),xper(0.7),yper(0.5))),

            ((0,0,xper(0.01),yper(1)),(0,0,xper(1),xper(0.01)),(xper(1)-xper(0.01),0,xper(0.02),yper(1)),(0,yper(1)-xper(0.01),xper(1),xper(0.02)),(xper(0.15),yper(0.25),xper(0.02),yper(0.5)),
            (xper(0.15),yper(0.23),xper(0.7),xper(0.02)),(xper(0.3),yper(0.49),xper(0.7),xper(0.02)),(xper(0.15),yper(0.75),xper(0.7),xper(0.02))),

            ((0,0,xper(0.01),yper(1)),(0,0,xper(1),xper(0.01)),(xper(1)-xper(0.01),0,xper(0.02),yper(1)),(0,yper(1)-xper(0.01),xper(1),xper(0.02)),(xper(0.15),yper(0.8),xper(0.7),xper(0.02)),
            (xper(0.1),yper(0.6),xper(0.1),xper(0.05)),(xper(0.12),yper(0.22),xper(0.03),yper(0.2)),(xper(0.34),yper(0.38),xper(0.03),yper(0.4)),(xper(0.28),yper(0.08),xper(0.07),yper(0.15)),
            (xper(0.49),yper(0.1),xper(0.03),yper(0.35)),(xper(0.52),yper(0.6),xper(0.2),xper(0.03)),(xper(0.71),yper(0.03),xper(0.06),yper(0.56)),(xper(0.83),yper(0.2),xper(0.05),yper(0.59))),

            ((-(xper(0.02)),0,xper(0.03),yper(0.4)),(-(xper(0.02)),yper(0.6),xper(0.03),yper(0.4)),(0,0,xper(1),xper(0.01)),(xper(1)-xper(0.01),0,xper(0.03),yper(0.4)),(xper(1)-xper(0.01),yper(0.6),xper(0.03),yper(0.4)),
            (0,yper(1)-xper(0.01),xper(1),xper(0.02)),(0,yper(0.6),xper(0.12),xper(0.01)),(xper(0.12),yper(0.22),xper(0.01),yper(0.398)),(xper(0.5),0,xper(0.01),yper(0.8)),(xper(0.12),yper(0.22),xper(0.26),xper(0.01)),
            (xper(0.38),yper(0.22),xper(0.01),yper(0.2)),(xper(0.25),yper(0.6),xper(0.25),xper(0.01)),(xper(0.25),yper(0.4),xper(0.01),yper(0.4)),(xper(0.12),yper(0.785),xper(0.14),xper(0.01)),
            (xper(0.38),yper(0.77),xper(0.01),yper(0.3)),(xper(0.63),yper(0.2),xper(0.01),yper(0.8)),(xper(0.63),yper(0.2),xper(0.23),xper(0.01)),(xper(0.8),yper(0.4),xper(0.3),xper(0.01)),
            (xper(0.8),yper(0.4),xper(0.01),yper(0.4))),

            ((0,0,xper(0.01),yper(1)),(0,0,xper(1),xper(0.01)),(xper(1)-xper(0.01),0,xper(0.02),yper(1)),(0,yper(1)-xper(0.01),xper(1),xper(0.02)),(xper(0.2),yper(0.2),xper(0.6),xper(0.01)),
            (xper(0.2),yper(0.2),xper(0.01),yper(0.6)),(xper(0.35),yper(0.4),xper(0.01),yper(0.6)),(xper(0.5),yper(0.2),xper(0.01),yper(0.6)),(xper(0.65),yper(0.4),xper(0.01),yper(0.6)),(xper(0.8),yper(0.2),xper(0.01),yper(0.6))),

            ((0,0,xper(0.01),yper(1)),(0,0,xper(1),xper(0.01)),(xper(1)-xper(0.01),0,xper(0.02),yper(1)),(0,yper(1)-xper(0.01),xper(1),xper(0.02)),(xper(0.1),yper(0.19),xper(0.2),xper(0.02)),
            (xper(0.3),yper(0.19),xper(0.02),yper(0.6)),(xper(0.49),0,xper(0.02),yper(0.5)),(xper(0.3),yper(0.79),xper(0.4),xper(0.02)),(xper(0.68),yper(0.19),xper(0.02),yper(0.6)),
            (xper(0.7),yper(0.19),xper(0.2),xper(0.02)),(xper(0.11),yper(0.45),xper(0.08),xper(0.08)),(xper(0.81),yper(0.45),xper(0.08),xper(0.08))),

            ((-(xper(0.01)),yper(0.15),xper(0.02),yper(0.85)),(-(xper(0.01)),-(xper(0.01)),xper(0.48),xper(0.02)),(xper(1)-xper(0.01),yper(0.15),xper(0.04),yper(0.85)),(0,yper(1)-xper(0.01),xper(0.45),xper(0.06)),
            (xper(0.55),yper(1)-xper(0.01),xper(0.45),xper(0.04)),(xper(0.55),(-xper(0.01)),xper(0.5),xper(0.02)),(xper(0.15),0,xper(0.01),yper(0.4)),(xper(0.15),yper(0.4),xper(0.2),yper(0.4)),(xper(0.3),yper(0.15),xper(0.25),xper(0.01)),
            (xper(0.55),0,xper(0.01),yper(0.4)),(xper(0.45),yper(0.25),xper(0.02),yper(0.85)),(xper(0.47),yper(0.4),xper(0.38),xper(0.01)),(xper(0.7),yper(0.15),xper(0.3),xper(0.01)),(xper(0.85),yper(0.4),xper(0.01),yper(0.4)),
            (xper(0.7),yper(0.57),xper(0.01),yper(0.43)),(xper(0.58),yper(0.57),xper(0.13),xper(0.01)),(xper(0.47),yper(0.8),xper(0.09),xper(0.01))),

            ((0,0,xper(0.01),yper(1)),(0,0,xper(1),xper(0.01)),(xper(1)-xper(0.01),0,xper(0.02),yper(1)),(0,yper(1)-xper(0.01),xper(1),xper(0.02)),(xper(0.15),yper(0.24),xper(0.7),xper(0.02)),(xper(0.14),yper(0.24),xper(0.02),yper(0.6)),
            (xper(0.29),yper(0.5),xper(0.02),yper(0.5)),(xper(0.29),yper(0.5),xper(0.4),xper(0.02)),(xper(0.84),yper(0.24),xper(0.02),yper(0.5)),(xper(0.46),yper(0.74),xper(0.4),xper(0.02))),

            ((0,0,xper(0.01),yper(1)),(0,-(xper(0.01)),xper(0.9),xper(0.02)),(xper(1)-xper(0.01),-(xper(0.05)),xper(0.04),yper(1.2)),(0,yper(1)-xper(0.01),xper(0.9),xper(0.03)),(xper(0.2),yper(0.25),xper(0.8),xper(0.01)),
            (0,yper(0.50),xper(0.4),xper(0.01)),(xper(0.55),yper(0.25),xper(0.01),yper(0.5)),(xper(0.2),yper(0.75),xper(0.6),xper(0.01)),(xper(0.7),yper(0.5),xper(0.2),xper(0.01)),(xper(0.9),yper(0.50),xper(0.01),yper(0.5)),
            (xper(0.2),yper(0.75),xper(0.01),yper(0.12)),(xper(0.35),yper(0.87),xper(0.01),yper(0.13)),(xper(0.5),yper(0.75),xper(0.01),yper(0.12)),(xper(0.65),yper(0.87),xper(0.01),yper(0.13)),(xper(0.8),yper(0.75),xper(0.01),yper(0.12))),

            ((0,0,xper(0.01),yper(1)),(0,0,xper(1),xper(0.01)),(xper(1)-xper(0.01),0,xper(0.02),yper(1)),(0,yper(1)-xper(0.01),xper(1),xper(0.02)),(xper(0.15),yper(0.3),xper(0.15),yper(0.2)),(xper(0.31),yper(0.35),xper(0.15),yper(0.2)),
            (xper(0.47),yper(0.4),xper(0.15),yper(0.2)),(xper(0.63),yper(0.45),xper(0.15),yper(0.2)),(xper(0.5),yper(0.02),xper(0.15),yper(0.2)),(xper(0.1),yper(0.72),xper(0.15),yper(0.2)),(xper(0.65),yper(0.78),xper(0.15),yper(0.2)),(xper(0.75),yper(0.23),xper(0.15),yper(0.2)),)
        )

        self.x, self.y, self.width, self.height = maps[self.track][self.id]

        walls.append(self)

    def process(self):

        for tank in tanks:
            if not tank.finished and rect_colision((self.x, self.y, self.width, self.height),(tank.x-tank.radius*0.75, tank.y-tank.radius*0.75, tank.radius*1.5, tank.radius*1.5)):

                wleft_border = abs(tank.x+tank.radius*1.5-self.x)
                wright_border = abs(tank.x-tank.radius*1.5-(self.x+self.width))
                wtop_border = abs(tank.y+tank.radius*1.5-self.y)
                wbottom_border = abs(tank.y-tank.radius*1.5-(self.y+self.height))
                wclosest_border = min(wleft_border,wright_border,wtop_border,wbottom_border)

                if wclosest_border == wleft_border: tank.x = self.x-tank.radius*0.75
                if wclosest_border == wright_border: tank.x = self.x+self.width+tank.radius*0.75
                if wclosest_border == wtop_border: tank.y = self.y-tank.radius*0.75
                if wclosest_border == wbottom_border: tank.y = self.y+self.height+tank.radius*0.75

                tank.vel *= 0.95

    def draw(self):

        lvlcolors = (
            (11,102,35),
            (215,199,100),
            (255,255,255),
            randcolor_in_range(0,0,30,75,100,150),
            randcolor_in_range(200,255,40,70,0,0)
        )
        pygame.draw.rect(windowSurface, lvlcolors[self.color], pygame.Rect(self.x, self.y, self.width, self.height))

class TrackPoint(Sprite):

    def __init__(self, i, track):
        self.id = i
        self.track = track
        self.color = (50,50,50)
        self.show = False
        self.finishlines = (
            ((yper(0.15),xper(0.0135),yper(0.12),xper(0.006),xper(0.012),xper(0.00625))),
            ((yper(0.2),xper(0.0135),yper(0.2),xper(0.006),xper(0.012),xper(0.00625))),
            ((xper(0.1),yper(0.013),xper(0.1),yper(0.012),xper(0.00725))),
            ((xper(0.06),yper(0.013),xper(0.06),yper(0.012),xper(0.00725))),
            ((yper(0.11),xper(0.013),yper(0.11),xper(0.006),xper(0.012),xper(0.00625))),
            ((yper(0.11),xper(0.013),yper(0.11),xper(0.006),xper(0.012),xper(0.00625))),
            ((xper(0.1),yper(0.013),xper(0.08),yper(0.012),xper(0.00725))),
            ((yper(0.13),xper(0.0135),yper(0.12),xper(0.006),xper(0.012),xper(0.00625))),
            ((yper(0.13),xper(0.0135),yper(0.12),xper(0.006),xper(0.012),xper(0.00625))),
            ((yper(0.13),xper(0.0135),yper(0.12),xper(0.006),xper(0.012),xper(0.00625)))
        )
        xConst = 0.02
        yConst = 0.035

        maps = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            []
        )

        # PARK
        for i in range(30): maps[0].append((xper(0.32+(i*xConst)),yper(0.13)))
        for i in range(22): maps[0].append((xper(0.92),yper(0.13+(i*yConst))))
        for i in range(42): maps[0].append((xper(0.92-(i*xConst)),yper(0.87)))
        for i in range(22): maps[0].append((xper(0.08),yper(0.87-(i*yConst))))
        for i in range(12): maps[0].append((xper(0.08+(i*xConst)),yper(0.13)))

        # HALLWAYS
        for i in range(10): maps[1].append((xper(0.74+(i*xConst)),yper(0.95)))
        for i in range(8): maps[1].append((xper(0.92),yper(0.92-(i*yConst))))
        for i in range(16): maps[1].append((xper(0.92-(i*xConst)),yper(0.64)))
        for i in range(20): maps[1].append((xper(0.6-(i*xConst)),yper(0.7)))
        for i in range(8): maps[1].append((xper(0.22),yper(0.66-(i*yConst))))
        for i in range(16): maps[1].append((xper(0.22+(i*xConst)),yper(0.37)))
        for i in range(20): maps[1].append((xper(0.54+(i*xConst)),yper(0.43)))
        for i in range(8): maps[1].append((xper(0.92),yper(0.4-(i*yConst))))
        for i in range(43): maps[1].append((xper(0.92-(i*xConst)),yper(0.12)))
        for i in range(22): maps[1].append((xper(0.08),yper(0.15+(i*yConst))))
        for i in range(23): maps[1].append((xper(0.08+(i*xConst)),yper(0.92)))
        for i in range(10): maps[1].append((xper(0.54+(i*xConst)),yper(0.95)))

        # MESSY
        for i in range(13): maps[2].append((xper(0.96),yper(0.51+(i*yConst))))
        for i in range(45): maps[2].append((xper(0.94-(i*xConst)),yper(0.93)))
        for i in range(13): maps[2].append((xper(0.04),yper(0.93-(i*yConst))))
        for i in range(6): maps[2].append((xper(0.06+(i*xConst)),yper(0.51)))
        for i in range(10): maps[2].append((xper(0.18+(i*xConst)),yper(0.51-(i*0.025))))
        for i in range(3): maps[2].append((xper(0.38+(i*xConst)),yper(0.28)))
        for i in range(15): maps[2].append((xper(0.44),yper(0.28+(i*yConst))))
        for i in range(18): maps[2].append((xper(0.46+(i*xConst)),yper(0.77)))
        for i in range(20): maps[2].append((xper(0.8),yper(0.74-(i*yConst))))
        for i in range(8): maps[2].append((xper(0.82+(i*xConst)),yper(0.07)))
        for i in range(12): maps[2].append((xper(0.96),yper(0.1+(i*yConst))))

        # PORTAL
        for i in range(12): maps[3].append((xper(0.56),yper(0.5-(i*yConst))))
        for i in range(14): maps[3].append((xper(0.56+(i*xConst)),yper(0.075)))
        for i in range(6): maps[3].append((xper(0.84+(i*xConst)),yper(0.035)))
        for i in range(8): maps[3].append((xper(0.96),yper(0.035+(i*yConst))))
        for i in range(13): maps[3].append((xper(0.96-(i*xConst)),yper(0.32)))
        for i in range(18): maps[3].append((xper(0.7),yper(0.32+(i*yConst))))
        for i in range(10): maps[3].append((xper(0.72+(i*xConst)),yper(0.92)))
        for i in range(11): maps[3].append((xper(0.9),yper(0.89-(i*yConst))))
        for i in range(15): maps[3].append((xper(0.92+(i*xConst)),yper(0.54)))
        for i in range(4): maps[3].append((xper(0+(i*xConst)),yper(0.54)))
        for i in range(12): maps[3].append((xper(0.06),yper(0.51-(i*yConst))))
        for i in range(14): maps[3].append((xper(0.08+(i*xConst)),yper(0.11)))
        for i in range(6): maps[3].append((xper(0.36+(i*xConst)),yper(0.04)))
        for i in range(14): maps[3].append((xper(0.46),yper(0.07+(i*yConst))))
        for i in range(6): maps[3].append((xper(0.46-(i*xConst)),yper(0.55)))
        for i in range(7): maps[3].append((xper(0.34),yper(0.55-(i*yConst))))
        for i in range(4): maps[3].append((xper(0.34-(i*xConst)),yper(0.31)))
        for i in range(6): maps[3].append((xper(0.26),yper(0.31)))
        for i in range(4): maps[3].append((xper(0.26-(i*xConst)),yper(0.31)))
        for i in range(12): maps[3].append((xper(0.18),yper(0.31+(i*yConst))))
        for i in range(5): maps[3].append((xper(0.18-(i*xConst)),yper(0.72)))
        for i in range(6): maps[3].append((xper(0.08),yper(0.72+(i*yConst))))
        for i in range(11): maps[3].append((xper(0.1+(i*xConst)),yper(0.895)))
        for i in range(7): maps[3].append((xper(0.32),yper(0.895-(i*yConst))))
        for i in range(6): maps[3].append((xper(0.34+(i*xConst)),yper(0.685)))
        for i in range(8): maps[3].append((xper(0.46),yper(0.685+(i*yConst))))
        for i in range(5): maps[3].append((xper(0.48+(i*xConst)),yper(0.93)))
        for i in range(11): maps[3].append((xper(0.56),yper(0.9-(i*yConst))))

        # ZIGZAG
        for i in range(20): maps[4].append((xper(0.5-(i*xConst)),yper(0.09)))
        for i in range(24): maps[4].append((xper(0.1),yper(0.13+(i*yConst))))
        for i in range(8): maps[4].append((xper(0.12+(i*xConst)),yper(0.94)))
        for i in range(20): maps[4].append((xper(0.28),yper(0.94-(i*yConst))))
        for i in range(8): maps[4].append((xper(0.3+(i*xConst)),yper(0.27)))
        for i in range(19): maps[4].append((xper(0.44),yper(0.3+(i*yConst))))
        for i in range(7): maps[4].append((xper(0.46+(i*xConst)),yper(0.93)))
        for i in range(19): maps[4].append((xper(0.58),yper(0.9-(i*yConst))))
        for i in range(8): maps[4].append((xper(0.6+(i*xConst)),yper(0.27)))
        for i in range(19): maps[4].append((xper(0.74),yper(0.3+(i*yConst))))
        for i in range(8): maps[4].append((xper(0.76+(i*xConst)),yper(0.93)))
        for i in range(24): maps[4].append((xper(0.9),yper(0.9-(i*yConst))))
        for i in range(19): maps[4].append((xper(0.88-(i*xConst)),yper(0.09)))

        # SMILEY
        maps[5].append((xper(0.32),yper(0.93)))
        for i in range(13): maps[5].append((xper(0.28-(i*xConst)),yper(0.93-(i*0.02))))
        for i in range(15): maps[5].append((xper(0.04),yper(0.63-(i*yConst))))
        for i in range(17): maps[5].append((xper(0.06+(i*xConst)),yper(0.12)))
        for i in range(17): maps[5].append((xper(0.4),yper(0.12+(i*yConst))))
        for i in range(9): maps[5].append((xper(0.42+(i*xConst)),yper(0.69)))
        for i in range(18): maps[5].append((xper(0.58),yper(0.66-(i*yConst))))
        for i in range(18): maps[5].append((xper(0.6+(i*xConst)),yper(0.06)))
        for i in range(17): maps[5].append((xper(0.96),yper(0.06+(i*yConst))))
        for i in range(13): maps[5].append((xper(0.96-(i*xConst)),yper(0.69+(i*0.02))))
        for i in range(20): maps[5].append((xper(0.7-(i*xConst)),yper(0.93)))

        # TWAINPORTALS
        for i in range(15): maps[6].append((xper(0.09),yper(0.55-(i*yConst))))
        for i in range(14): maps[6].append((xper(0.07-(i*xConst)),yper(0.06)))
        for i in range(20): maps[6].append((xper(0.99-(i*xConst)),yper(0.04)))
        for i in range(10): maps[6].append((xper(0.59),yper(0.04+(i*yConst))))
        for i in range(17): maps[6].append((xper(0.61+(i*xConst)),yper(0.36-(i*0.005))))
        for i in range(20): maps[6].append((xper(0.95),yper(0.27+(i*yConst))))
        for i in range(9): maps[6].append((xper(0.935-(i*xConst)),yper(0.935)))
        for i in range(13): maps[6].append((xper(0.775),yper(0.9-(i*yConst))))
        for i in range(14): maps[6].append((xper(0.755-(i*xConst)),yper(0.48)))
        for i in range(6): maps[6].append((xper(0.49),yper(0.51+(i*yConst))))
        for i in range(8): maps[6].append((xper(0.51+(i*xConst)),yper(0.69)))
        for i in range(6): maps[6].append((xper(0.65),yper(0.72+(i*yConst))))
        for i in range(7): maps[6].append((xper(0.63-(i*xConst)),yper(0.9)))
        for i in range(5): maps[6].append((xper(0.51),yper(0.9)))
        for i in range(13): maps[6].append((xper(0.51),yper(0.93+(i*yConst))))
        for i in range(2): maps[6].append((xper(0.51),yper(0.02+(i*yConst))))
        for i in range(15): maps[6].append((xper(0.49-(i*xConst)),yper(0.055)))
        for i in range(6): maps[6].append((xper(0.21),yper(0.08+(i*yConst))))
        for i in range(10): maps[6].append((xper(0.23+(i*xConst)),yper(0.255)))
        for i in range(14): maps[6].append((xper(0.43),yper(0.255+(i*yConst))))
        for i in range(6): maps[6].append((xper(0.41),yper(0.745+(i*yConst))))
        for i in range(17): maps[6].append((xper(0.41-(i*xConst)),yper(0.92)))
        for i in range(10): maps[6].append((xper(0.09),yper(0.9-(i*yConst))))

        # SNAIL
        for i in range(14): maps[7].append((xper(0.51+(i*xConst)),yper(0.37)))
        for i in range(8): maps[7].append((xper(0.79),yper(0.37+(i*yConst))))
        for i in range(20): maps[7].append((xper(0.77-(i*xConst)),yper(0.62)))
        for i in range(7): maps[7].append((xper(0.39),yper(0.65+(i*yConst))))
        for i in range(28): maps[7].append((xper(0.39+(i*xConst)),yper(0.9)))
        for i in range(23): maps[7].append((xper(0.93),yper(0.87-(i*yConst))))
        for i in range(43): maps[7].append((xper(0.91-(i*xConst)),yper(0.09)))
        for i in range(23): maps[7].append((xper(0.07),yper(0.12+(i*yConst))))
        for i in range(8): maps[7].append((xper(0.07+(i*xConst)),yper(0.93)))
        for i in range(16): maps[7].append((xper(0.21),yper(0.9-(i*yConst))))
        for i in range(14): maps[7].append((xper(0.23+(i*xConst)),yper(0.37)))

        # COMBINED
        for i in range(35): maps[8].append((xper(0.86-(i*xConst)),yper(0.12)))
        for i in range(5): maps[8].append((xper(0.16-(i*xConst)),yper(0.07)))
        for i in range(9): maps[8].append((xper(0.06),yper(0.07+(i*yConst))))
        for i in range(20): maps[8].append((xper(0.08+(i*xConst)),yper(0.37)))
        for i in range(8): maps[8].append((xper(0.48),yper(0.37+(i*yConst))))
        for i in range(12): maps[8].append((xper(0.46-(i*xConst)),yper(0.68)))
        for i in range(8): maps[8].append((xper(0.22-(i*xConst)),yper(0.62)))
        for i in range(9): maps[8].append((xper(0.06),yper(0.62+(i*yConst))))
        for i in range(5): maps[8].append((xper(0.08+(i*xConst)),yper(0.93)))
        for i in range(5): maps[8].append((xper(0.14),yper(0.93)))
        for i in range(5): maps[8].append((xper(0.18+(i*xConst)),yper(0.93)))
        for i in range(3): maps[8].append((xper(0.26),yper(0.9-(i*yConst))))
        for i in range(4): maps[8].append((xper(0.28+(i*xConst)),yper(0.83)))
        for i in range(5): maps[8].append((xper(0.32),yper(0.83)))
        for i in range(4): maps[8].append((xper(0.36+(i*xConst)),yper(0.83)))
        for i in range(3): maps[8].append((xper(0.44),yper(0.83+(i*yConst))))
        for i in range(4): maps[8].append((xper(0.44+(i*xConst)),yper(0.93)))
        for i in range(5): maps[8].append((xper(0.48),yper(0.93)))
        for i in range(3): maps[8].append((xper(0.52+(i*xConst)),yper(0.93)))
        for i in range(3): maps[8].append((xper(0.56),yper(0.9-(i*yConst))))
        for i in range(4): maps[8].append((xper(0.58+(i*xConst)),yper(0.83)))
        for i in range(5): maps[8].append((xper(0.62),yper(0.83)))
        for i in range(3): maps[8].append((xper(0.66+(i*xConst)),yper(0.83)))
        for i in range(3): maps[8].append((xper(0.72),yper(0.83+(i*yConst))))
        for i in range(4): maps[8].append((xper(0.72+(i*xConst)),yper(0.93)))
        for i in range(5): maps[8].append((xper(0.76),yper(0.93)))
        for i in range(3): maps[8].append((xper(0.8+(i*xConst)),yper(0.93)))
        for i in range(10): maps[8].append((xper(0.86),yper(0.93-(i*yConst))))
        for i in range(12): maps[8].append((xper(0.84-(i*xConst)),yper(0.61)))
        for i in range(7): maps[8].append((xper(0.62),yper(0.57-(i*yConst))))
        for i in range(16): maps[8].append((xper(0.64+(i*xConst)),yper(0.36)))
        for i in range(29): maps[8].append((xper(0.96),yper(0.36+(i*yConst))))
        for i in range(3): maps[8].append((xper(0.96),yper(0.02+(i*yConst))))
        for i in range(5): maps[8].append((xper(0.96-(i*xConst)),yper(0.12)))

        # BOXES
        for i in range(20): maps[9].append((xper(0.7-(i*xConst)),yper(0.72)))
        for i in range(13): maps[9].append((xper(0.3-(i*xConst)),yper(0.72-(i*0.02))))
        for i in range(7): maps[9].append((xper(0.06),yper(0.44-(i*yConst))))
        for i in range(15): maps[9].append((xper(0.08+(i*xConst)),yper(0.22)))
        for i in range(15): maps[9].append((xper(0.38+(i*xConst)),yper(0.22+(i*0.01))))
        for i in range(10): maps[9].append((xper(0.68),yper(0.37-(i*yConst))))
        for i in range(13): maps[9].append((xper(0.7+(i*xConst)),yper(0.05)))
        for i in range(20): maps[9].append((xper(0.96),yper(0.05+(i*yConst))))
        for i in range(12): maps[9].append((xper(0.94-(i*xConst)),yper(0.72)))

        self.x, self.y = maps[self.track][self.id]

        trackpoints.append(self)

    def draw(self):

        if self.show: pygame.draw.circle(windowSurface, self.color, (self.x, self.y), xper(0.005))
        self.color = (50,50,50)

        if self.id == 0:
            if self.track in (0,1,4,5,7,8,9):
                pygame.draw.line(windowSurface, (255,255,255), (self.x,self.y-self.finishlines[self.track][0]),(self.x,self.y+self.finishlines[self.track][0]),2)
                pygame.draw.line(windowSurface, (255,255,255), (self.x-self.finishlines[self.track][1],self.y-self.finishlines[self.track][0]),(self.x-self.finishlines[self.track][1],self.y+self.finishlines[self.track][0]),2)
                for i in range(15) if SCREEN_X < 1000 else range(11):
                    pygame.draw.rect(windowSurface, (255,255,255), pygame.Rect(self.x-self.finishlines[self.track][3], self.y-self.finishlines[self.track][2]+i*xper(0.0125), self.finishlines[self.track][5], self.finishlines[self.track][5]))
                    pygame.draw.rect(windowSurface, (255,255,255), pygame.Rect(self.x-self.finishlines[self.track][4], self.y-self.finishlines[self.track][2]+(i+0.5)*xper(0.0125), self.finishlines[self.track][5], self.finishlines[self.track][5]))

            else:
                pygame.draw.line(windowSurface, (255,255,255), (self.x-self.finishlines[self.track][0],self.y+self.finishlines[self.track][1]),(self.x+self.finishlines[self.track][0],self.y+self.finishlines[self.track][1]),2)
                pygame.draw.line(windowSurface, (255,255,255), (self.x-self.finishlines[self.track][0],self.y-self.finishlines[self.track][1]),(self.x+self.finishlines[self.track][0],self.y-self.finishlines[self.track][1]),2)
                for i in range(16) if SCREEN_X < 1000 else range(11):
                    pygame.draw.rect(windowSurface, (255,255,255), pygame.Rect(self.x-self.finishlines[self.track][2]+i*xper(0.0125), self.y-self.finishlines[self.track][3], self.finishlines[self.track][4], self.finishlines[self.track][4]))
                    pygame.draw.rect(windowSurface, (255,255,255), pygame.Rect(self.x-self.finishlines[self.track][2]+(i+0.5)*xper(0.0125), self.y,self.finishlines[self.track][4], self.finishlines[self.track][4]))

        if self.id == len(trackpoints)-1:
            for tank in tanks:
                if tank.start_ang == 0:
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x+tank.radius,tank.start_y-tank.radius),(tank.start_x+tank.radius,tank.start_y+tank.radius),2)
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x+tank.radius/2,tank.start_y+tank.radius),(tank.start_x+tank.radius,tank.start_y+tank.radius),2)
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x+tank.radius/2,tank.start_y-tank.radius),(tank.start_x+tank.radius,tank.start_y-tank.radius),2)
                if tank.start_ang == math.pi:
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x-tank.radius,tank.start_y-tank.radius),(tank.start_x-tank.radius,tank.start_y+tank.radius),2)
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x-tank.radius/2,tank.start_y+tank.radius),(tank.start_x-tank.radius,tank.start_y+tank.radius),2)
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x-tank.radius/2,tank.start_y-tank.radius),(tank.start_x-tank.radius,tank.start_y-tank.radius),2)
                if tank.start_ang == math.pi/2:
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x-tank.radius,tank.start_y+tank.radius),(tank.start_x+tank.radius,tank.start_y+tank.radius),2)
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x-tank.radius,tank.start_y+tank.radius),(tank.start_x-tank.radius,tank.start_y+tank.radius/2),2)
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x+tank.radius,tank.start_y+tank.radius),(tank.start_x+tank.radius,tank.start_y+tank.radius/2),2)
                if tank.start_ang == -math.pi/2:
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x-tank.radius,tank.start_y-tank.radius),(tank.start_x+tank.radius,tank.start_y-tank.radius),2)
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x-tank.radius,tank.start_y-tank.radius),(tank.start_x-tank.radius,tank.start_y-tank.radius/2),2)
                    pygame.draw.line(windowSurface, (255,255,255), (tank.start_x+tank.radius,tank.start_y-tank.radius),(tank.start_x+tank.radius,tank.start_y-tank.radius/2),2)

class MainHandler(Sprite):

    def __init__(self):
        self.menu = True
        self.menulevel = 0
        self.option = 0
        self.playermode = 0
        self.laps = 1
        self.difficulty = 1
        self.track = 0
        self.choose_menulevel = (0,1)
        self.choose_playermode = (0,1)
        self.choose_laps = (0,1,2)
        self.choose_difficulty = (0,1,2,3)
        self.choose_track = (0,1,2,3,4,5,6,7,8,9)
        self.keypressed = False
        self.f1_pressed = False
        self.f2_pressed = False
        self.tournament = False
        self.tank_points = [0,0,0,0]
        self.tank_times = [0,0,0,0]

    def process(self):

        maps = ((5,128),(8,204),(13,163),(19,255),(10,203),(12,157),(17,257),(10,204),(15,264),(12,125))

        if self.menu:

            self.nWalls, self.nTrackpoints = maps[self.track][0], maps[self.track][1]

            if self.menulevel == 0: self.choose_option = (0,1,2)
            if self.menulevel == 1 and not self.tournament: self.choose_option = (0,1,2,3)

            if not self.keypressed:

                if keys[pygame.K_UP]:
                    self.option = (self.option-1) % len(self.choose_option)
                    self.keypressed = True

                if keys[pygame.K_DOWN]:
                    self.option = (self.option+1) % len(self.choose_option)
                    self.keypressed = True

                if keys[pygame.K_LEFT]:
                    if self.menulevel == 1:
                        if self.option == 0: self.playermode = (self.playermode-1) % len(self.choose_playermode)
                        if self.option == 1: self.laps = (self.laps-1) % len(self.choose_laps)
                        if self.option == 2: self.difficulty = (self.difficulty-1) % len(self.choose_difficulty)
                        if self.option == 3: self.track = (self.track-1) % len(self.choose_track)
                    self.keypressed = True

                if keys[pygame.K_RIGHT]:
                    if self.menulevel == 1:
                        if self.option == 0: self.playermode = (self.playermode+1) % len(self.choose_playermode)
                        if self.option == 1: self.laps = (self.laps+1) % len(self.choose_laps)
                        if self.option == 2: self.difficulty = (self.difficulty+1) % len(self.choose_difficulty)
                        if self.option == 3: self.track = (self.track+1) % len(self.choose_track)
                    self.keypressed = True

                if keys[pygame.K_RETURN]:

                    if self.menulevel == 0:
                        if self.option == 0:
                            self.menulevel = 1
                            self.tournament = False
                        if self.option == 1:
                            self.menulevel = 1
                            self.tournament = True
                            self.option = 0
                        if self.option == 2:
                            pygame.quit()
                            sys.exit()

                    elif self.menulevel == 1:
                        for i in range(self.nTrackpoints): add_sprite(TrackPoint(i,self.track))
                        for i in range(self.nWalls): add_sprite(Wall(i,self.track,self.track//2))
                        for i in range(4): add_sprite(Tank(i,self.playermode, self.track, self.laps, self.difficulty))
                        add_sprite(AuxiliaryHandler(self.playermode, self.laps, self.track, self.difficulty, self.tournament, self.tank_points, self.tank_times))

                        self.menu = False

                    self.keypressed = True

                if keys[pygame.K_ESCAPE]:
                    if self.menulevel == 1:
                        self.menulevel = 0
                        self.option = 0 if not self.tournament else 1
                        self.playermode = 0
                        self.laps = 1
                        self.difficulty = 1
                        self.track = 0
                        self.keypressed = True
                    else:
                        pygame.quit()
                        sys.exit()

            if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT] and not keys[pygame.K_UP] and not keys[pygame.K_DOWN] and not keys[pygame.K_ESCAPE] and not keys[pygame.K_RETURN]:
                self.keypressed = False

        else:

            if not self.keypressed:
                if keys[pygame.K_ESCAPE]:
                    for sprite in sprites:
                        if sprite != self: sprites.remove(sprite)
                    trackpoints.clear()
                    walls.clear()
                    tanks.clear()
                    bombs.clear()

                    if len(sprites) == 1:
                        self.menulevel = 0
                        self.option = 0
                        self.playermode = 0
                        self.laps = 1
                        self.difficulty = 1
                        self.track = 0
                        self.menu = True
                        self.keypressed = True
                        self.tank_points = [0,0,0,0]
                        self.tank_times = [0,0,0,0]

            if not self.f1_pressed:
                if keys[pygame.K_F1]:
                    for tank in tanks: tank.showhitbox = not tank.showhitbox
                    self.f1_pressed = True

            if not self.f2_pressed:
                if keys[pygame.K_F2]:
                    for point in trackpoints: point.show = not point.show
                    self.f2_pressed = True

            if not keys[pygame.K_F1]: self.f1_pressed = False
            if not keys[pygame.K_F2]: self.f2_pressed = False
            if not keys[pygame.K_ESCAPE]: self.keypressed = False

    def draw(self):

        lvlcolors = (
            (11,102,35),
            (215,199,100),
            (255,255,255),
            randcolor_in_range(0,0,30,75,100,150),
            randcolor_in_range(200,255,40,70,0,0)
        )
        menucolor = randcolor_in_range(150,255,0,0,200,255)
        menubackground = modify_color_perc(menucolor,0.1)

        windowSurface.fill(menubackground if self.menu else modify_color_perc(lvlcolors[self.track//2],0.15))

        if self.menu:
            if self.menulevel == 0:
                create_text(B_font,'CrazyTanks',menucolor,menubackground,xper(0.5),yper(0.2))
                create_text(M_font,'New Race',menucolor if self.option == 0 else (75,0,75),menubackground,xper(0.5),yper(0.5))
                create_text(M_font,'Tournament',menucolor if self.option == 1 else (75,0,75),menubackground,xper(0.5),yper(0.6))
                create_text(M_font,'Exit',menucolor if self.option == 2 else (75,0,75),menubackground,xper(0.5),yper(0.7))
            if self.menulevel == 1:
                create_text(B_font,'CrazyTanks',menucolor,menubackground,xper(0.5),yper(0.2))
                create_text(M_font,'< Single Player >' if self.option == 0 and self.playermode == 0 else '< Two Players >' if self.option == 0 and self.playermode == 1 else 'Single Player' if self.playermode == 0 else 'Two Players',menucolor if self.option == 0 else (75,0,75),menubackground,xper(0.5),yper(0.45))
                create_text(M_font,'< Short (10 laps) >' if self.laps == 0 and self.option == 1 else '< Normal (20 laps) >' if self.laps == 1 and self.option == 1 else '< Long (40 laps) >' if self.laps == 2 and self.option == 1 else 'Short (10 laps)' if self.laps == 0 else 'Normal (20 laps)' if self.laps == 1 else 'Long (40 laps)',menucolor if self.option == 1 else (75,0,75),menubackground,xper(0.5),yper(0.55))
                create_text(M_font,'< Difficulty: Easy >' if self.difficulty == 0 and self.option == 2 else '< Difficulty: Normal >' if self.difficulty == 1 and self.option == 2 else '< Difficulty: Hard >' if self.difficulty == 2 and self.option == 2 else '< Difficulty: Very Hard >' if self.difficulty == 3 and self.option == 2 else 'Difficulty: Easy' if self.difficulty == 0 else 'Difficulty: Normal' if self.difficulty == 1 else 'Difficulty: Hard' if self.difficulty == 2 else 'Difficulty: Very Hard',menucolor if self.option == 2 else (75,0,75),menubackground,xper(0.5),yper(0.65))
                create_text(M_font,'< Map: %s >' % ('Park' if self.track == 0 else 'Hallways' if self.track == 1 else 'Messy' if self.track == 2 else 'Portal' if self.track == 3 else 'Zig Zag' if self.track == 4 else 'Smiley' if self.track == 5 else 'Twain Portals' if self.track == 6 else 'Snail' if self.track == 7 else 'Combined' if self.track == 8 else 'Boxes') if self.option == 3 else 'Map: %s' % ('Park' if self.track == 0 else 'Hallways' if self.track == 1 else 'Messy' if self.track == 2 else 'Portal' if self.track == 3 else 'Zig Zag' if self.track == 4 else 'Smiley' if self.track == 5 else 'Twain Portals' if self.track == 6 else 'Snail' if self.track == 7 else 'Combined' if self.track == 8 else 'Boxes'),menucolor if self.option == 3 else (25,25,25) if self.tournament else (75,0,75),menubackground,xper(0.5),yper(0.75))

class AuxiliaryHandler(Sprite):

    def __init__(self, playermode, laps, track, difficulty, tournament, tankpoints, tanktimes):
        self.playermode = playermode
        self.laps = laps
        self.track = track
        self.difficulty = difficulty
        self.racestart_timer = 5
        self.racestart_cooling = 0
        self.playerfinished = [False, False, False, False]
        self.racefinished = False
        self.post_race_option = 0
        self.p_pressed = False
        self.enter_pressed = False
        self.pause = False
        self.tournament = tournament
        self.points_for_rank = [4,3,2,1]
        self.tank_points = tankpoints
        self.tank_times = tanktimes
        self.table_timer = 3
        self.table_cooldown = 0
        self.pointsaccounted = False
        self.randombool = False
        self.tournamentfinished = False

    def process(self):

        maps = ((5,128),(8,204),(13,163),(19,255),(10,203),(12,157),(17,257),(10,204),(15,264),(12,125))
        self.nWalls, self.nTrackpoints = maps[self.track][0], maps[self.track][1]

        if not self.racefinished:

            self.racestart_cooling += deltaT
            if self.racestart_cooling > self.racestart_timer-1:
                for tank in tanks:
                    tank.start = True
                    if tank.finished: self.playerfinished[tank.id] = tank.finished

            if self.playermode == 0 and self.playerfinished[0]:
                for tank in tanks:
                    tank.finished = True
                    tank.ai = True

            if self.playermode == 0 and self.playerfinished[1] and self.playerfinished[2] and self.playerfinished[3]:
                for tank in tanks:
                    tank.finished = True
                    tank.ai = True

            if self.playermode == 1 and self.playerfinished[0] and self.playerfinished[1]:
                for tank in tanks:
                    tank.finished = True
                    tank.ai = True

            if self.playermode == 1 and self.playerfinished[0] and self.playerfinished[2] and self.playerfinished[3]:
                for tank in tanks:
                    tank.finished = True
                    tank.ai = True

            if self.playermode == 1 and self.playerfinished[1] and self.playerfinished[2] and self.playerfinished[3]:
                for tank in tanks:
                    tank.finished = True
                    tank.ai = True

            if self.playerfinished[0] and self.playerfinished[1] and self.playerfinished[2] and self.playerfinished[3]:
                self.racefinished = True

            if self.racestart_cooling > self.racestart_timer:
                if not self.p_pressed:
                    if keys[pygame.K_p]:
                        for tank in tanks: tank.pause = not tank.pause
                        for bomb in bombs: bomb.pause = not bomb.pause
                        self.pause = not self.pause
                        self.p_pressed = True
                if not keys[pygame.K_p]: self.p_pressed = False

        else:
            if not self.tournament:
                if keys[pygame.K_UP]: self.post_race_option = 0
                if keys[pygame.K_DOWN]: self.post_race_option = 1
                if keys[pygame.K_RETURN]:
                    if self.post_race_option == 0:

                        for sprite in sprites:
                            if sprite != sprites[0] and sprite != self: sprites.remove(sprite)
                        trackpoints.clear()
                        walls.clear()
                        tanks.clear()
                        bombs.clear()

                        if len(sprites) == 2:

                            for i in range(self.nTrackpoints): add_sprite(TrackPoint(i,self.track))
                            for i in range(self.nWalls): add_sprite(Wall(i,self.track,self.track//2))
                            for i in range(4): add_sprite(Tank(i,self.playermode, self.track, self.laps, self.difficulty))
                            add_sprite(AuxiliaryHandler(self.playermode, self.laps, self.track, self.difficulty, self.tournament, self.tank_points, self.tank_times))
                            sprites.remove(self)

                    if self.post_race_option == 1:

                        for sprite in sprites:
                            if sprite != sprites[0] and sprite != self: sprites.remove(sprite)
                        trackpoints.clear()
                        walls.clear()
                        tanks.clear()
                        bombs.clear()

                        if len(sprites) == 2:
                            for sprite in sprites:
                                if sprite == sprites[0]:
                                    sprite.menulevel = 0
                                    sprite.option = 0
                                    sprite.playermode = 0
                                    sprite.laps = 1
                                    sprite.difficulty = 1
                                    sprite.track = 0
                                    sprite.menu = True
                                    sprite.keypressed = True
                            sprites.remove(self)
            else:
                self.table_cooldown += deltaT

                if self.table_cooldown > self.table_timer and not self.pointsaccounted:
                    if keys[pygame.K_RETURN]:
                        for tank in tanks:
                            self.tank_points[tank.id] += self.points_for_rank[tank.rank-1]
                            self.tank_times[tank.id] += tank.racetime + tank.racetime*0.01*(tank.rank-1)
                        self.pointsaccounted = True
                        self.enter_pressed = True

                if self.pointsaccounted:
                    if self.track == 9:
                        self.tournamentfinished = True
                        self.post_race_option = 1
                    if keys[pygame.K_UP] and not self.tournamentfinished: self.post_race_option = 0
                    if keys[pygame.K_DOWN]: self.post_race_option = 1
                    if not self.enter_pressed:
                        if keys[pygame.K_RETURN]:
                            if self.post_race_option == 0:

                                for sprite in sprites:
                                    if sprite == sprites[0] and not self.randombool:
                                        sprite.track += 1
                                        self.randombool = True
                                    if sprite != sprites[0] and sprite != self: sprites.remove(sprite)
                                trackpoints.clear()
                                walls.clear()
                                tanks.clear()

                                if len(sprites) == 2:
                                    self.nWalls, self.nTrackpoints = maps[self.track+1][0], maps[self.track+1][1]
                                    for i in range(self.nTrackpoints): add_sprite(TrackPoint(i,self.track+1))
                                    for i in range(self.nWalls): add_sprite(Wall(i,self.track+1,(self.track+1)//2))
                                    for i in range(4): add_sprite(Tank(i,self.playermode, self.track+1, self.laps, self.difficulty))
                                    add_sprite(AuxiliaryHandler(self.playermode, self.laps, self.track+1, self.difficulty, self.tournament, self.tank_points, self.tank_times))
                                    sprites.remove(self)

                            if self.post_race_option == 1:

                                for sprite in sprites:
                                    if sprite != sprites[0] and sprite != self: sprites.remove(sprite)
                                trackpoints.clear()
                                walls.clear()
                                tanks.clear()
                                bombs.clear()

                                if len(sprites) == 2:
                                    for sprite in sprites:
                                        if sprite == sprites[0]:
                                            sprite.menulevel = 0
                                            sprite.option = 0
                                            sprite.playermode = 0
                                            sprite.laps = 1
                                            sprite.difficulty = 1
                                            sprite.track = 0
                                            sprite.menu = True
                                            sprite.keypressed = True
                                            sprite.tank_points = [0,0,0,0]
                                            sprite.tank_times = [0,0,0,0]
                                    sprites.remove(self)

                    if not keys[pygame.K_RETURN]: self.enter_pressed = False

    def draw(self):

        if self.racestart_cooling > 1:
            if self.racestart_cooling < self.racestart_timer:
                create_text(B_font,'3!' if self.racestart_cooling > 1 and self.racestart_cooling < 1.7 else '2!' if self.racestart_cooling > 2 and self.racestart_cooling < 2.7 else '1!' if self.racestart_cooling > 3 and self.racestart_cooling < 3.7 else 'GO!!' if self.racestart_cooling > 4 and self.racestart_cooling < 5 else '',(255,255,255),None,xper(0.5),yper(0.5))

        if self.racefinished:

            if not self.tournament:
                for tank in tanks:
                    if tank.rank == 1: create_text(B_font,'¡%s Wins!' % ('Red' if tank.id == 0 else 'Blue' if tank.id == 1 else 'Purple' if tank.id == 2 else 'Yellow'),modify_color(tank.color,75),None,xper(0.5),yper(0.35))
                create_text(M_font,'Rematch',(255,255,255) if self.post_race_option == 0 else (150,150,150),None,xper(0.5),yper(0.55))
                create_text(M_font,'Back to Menu',(255,255,255) if self.post_race_option == 1 else (150,150,150),None,xper(0.5),yper(0.65))

            else:
                if self.table_cooldown < self.table_timer:
                    for tank in tanks:
                        if tank.rank == 1: create_text(B_font,'¡%s Wins!' % ('Red' if tank.id == 0 else 'Blue' if tank.id == 1 else 'Purple' if tank.id == 2 else 'Yellow'),modify_color(tank.color,75),None,xper(0.5),yper(0.5))

                else:
                    pygame.draw.rect(windowSurface, (0,0,0), pygame.Rect(xper(0.25), yper(0.25), xper(0.5), yper(0.4)))
                    pygame.draw.rect(windowSurface, (255,255,255), pygame.Rect(xper(0.25), yper(0.25), xper(0.5), yper(0.4)),4)
                    for i in range(3): pygame.draw.line(windowSurface, (255,255,255), (xper(0.26), yper(0.35 + (0.1 if i == 1 else 0.2 if i == 2 else 0))),(xper(0.74), yper(0.35 + (0.1 if i == 1 else 0.2 if i == 2 else 0))),2)

                    for tank in tanks:
                        tourneyrank = len(tanks)
                        pos_in_table = yper(0.6)

                        if self.tank_points[tank.id] > 0:
                            for tank2 in tanks:
                                if tank2 != tank:
                                    if self.tank_points[tank.id] > self.tank_points[tank2.id]:
                                        tourneyrank -= 1
                                        pos_in_table -= yper(0.1)
                                    if self.tank_points[tank.id] == self.tank_points[tank2.id] and self.tank_times[tank.id] < self.tank_times[tank2.id]:
                                        tourneyrank -= 1
                                        pos_in_table -= yper(0.1)
                            points = (str(self.tank_points[tank.id]) + ' + ' + str(self.points_for_rank[tank.rank-1])) if not self.pointsaccounted else self.tank_points[tank.id]

                        else:
                            tourneyrank = '1' if tank.id == 0 else '2' if tank.id == 1 else '3' if tank.id == 2 else '4'
                            pos_in_table = yper(0.3) if tank.id == 0 else yper(0.4) if tank.id == 1 else yper(0.5) if tank.id == 2 else yper(0.6)
                            points = ('0'+' + '+str(self.points_for_rank[tank.rank-1]))

                        create_text(M_font,'%s°'%(tourneyrank),modify_color(tank.color,75) if self.pointsaccounted else (255,255,255),None,xper(0.3),pos_in_table)
                        create_text(M_font,'%s pts.'%(points),modify_color(tank.color,75),None,xper(0.675),pos_in_table)
                        if self.pointsaccounted and self.tournamentfinished and tourneyrank == 1: create_text(B_font,'¡%s is the Champion!' % ('Red' if tank.id == 0 else 'Blue' if tank.id == 1 else 'Purple' if tank.id == 2 else 'Yellow'),randcolor_gray(55,255),None,xper(0.5),yper(0.15))
                        if not self.pointsaccounted: create_text(RS_font if SCREEN_X < 1000 else S_font,'%s'%("1st!" if tank.rank == 1 else "2nd!" if tank.rank == 2 else "3rd" if tank.rank == 3 else "4th"),modify_color(tank.color,75),None,xper(0.375),pos_in_table)

                        lines = 17
                        for layer in range(2):
                            for i in range(lines):
                                x = xper(0.35) + math.cos(-math.pi/2 + math.pi/2) * (-tank.radius + 2*tank.radius*(i/lines) + ((tank.radius*2) / lines-1)/2)
                                y = pos_in_table + math.sin(-math.pi/2 + math.pi/2) * (-tank.radius + 2*tank.radius*(i/lines) + ((tank.radius*2) / lines-1)/2)
                                length = tank.radius * 0.7 if abs(i - lines // 2) < lines * 0.2 else tank.radius
                                if layer == 0:
                                    pygame.draw.line(windowSurface, modify_color(tank.color, -50), (x + math.cos(-math.pi/2) * -length, y + math.sin(-math.pi/2) * -length), (x + math.cos(-math.pi/2) * length, y + math.sin(-math.pi/2) * length), max(int((tank.radius*5) / lines-1), 1))
                                else:
                                    pygame.draw.line(windowSurface, tank.color, (x + math.cos(-math.pi/2) * -length, y + math.sin(-math.pi/2) * -length), (x + math.cos(-math.pi/2) * length, y + math.sin(-math.pi/2) * length), max(int((tank.radius*2) / lines-1), 1))

                        pygame.draw.circle(windowSurface, modify_color(tank.color, -25), (xper(0.35), pos_in_table), tank.radius * 0.7)
                        pygame.draw.line(windowSurface, modify_color(tank.color, 25), (xper(0.35), pos_in_table), (xper(0.35) + math.cos(-math.pi/2) * tank.radius * 1.5, pos_in_table + math.sin(-math.pi/2) * tank.radius * 1.5), int(tank.radius * 0.3))
                        pygame.draw.circle(windowSurface, modify_color(tank.color, 75), (xper(0.35), pos_in_table), tank.radius * 0.5)
                        pygame.draw.circle(windowSurface, modify_color(tank.color, 25), (xper(0.35), pos_in_table), tank.radius * 0.5, 1)

                if self.pointsaccounted:
                    create_text(M_font,'Continue' if not self.tournamentfinished else '',(255,255,255) if self.post_race_option == 0 else (150,150,150),None,xper(0.5),yper(0.75))
                    create_text(M_font,'Exit Tournament' if not self.tournamentfinished else 'Back to Menu',(255,255,255) if self.post_race_option == 1 else (150,150,150),None,xper(0.5),yper(0.85))

        if self.pause: create_text(B_font,'PAUSE',randcolor_gray(155,255),None,xper(0.5),yper(0.5))

def xper(percentage):
    return percentage * SCREEN_X

def yper(percentage):
    return percentage * SCREEN_Y

def randcolor():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

def randcolor_in_range(rmin,rmax,gmin,gmax,bmin,bmax):
    return (random.randint(rmin,rmax), random.randint(gmin,gmax), random.randint(bmin,bmax))

def randcolor_gray(mincap,maxcap):
    val = random.randint(mincap,maxcap)
    return (val,val,val)

def modify_color(color, offset):
    return tuple(max(min(c+offset, 255), 0) for c in color)

def modify_color_perc(color, offset):
    return tuple(max(min(c*offset, 255), 0) for c in color)    

def getangle(point1, point2):
    return math.atan2(point2[1]-point1[1], point2[0]-point1[0])

def getangle2(prev_ang, point1, point2):
    angle = math.atan2(point2[1]-point1[1], point2[0]-point1[0])
    if angle - prev_ang < -math.pi: angle += math.pi*2
    if angle - prev_ang >  math.pi: angle -= math.pi*2
    return angle

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

pygame.init()

SCREEN_X = 1280
SCREEN_Y = 720
windowSurface = pygame.display.set_mode((SCREEN_X, SCREEN_Y), depth=32, display=0)
pygame.display.set_caption('CrazyTanks')

B_font = pygame.font.Font(None, 150)
M_font = pygame.font.Font(None, 60)
S_font = pygame.font.Font(None, 20)
RS_font = pygame.font.Font(None, 13)

deltaT = 0
iniT = time.time()
keys = None
sprites = []
trackpoints = []
walls = []
tanks = []
bombs = []

add_sprite(MainHandler())

# MAIN LOOP ..........................................................................

while True:

    now = time.time()
    deltaT = min(now - iniT, 0.05)
    iniT = now
    keys = pygame.key.get_pressed()

    for sprite in sprites:
        sprite.process()
        sprite.draw()

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()