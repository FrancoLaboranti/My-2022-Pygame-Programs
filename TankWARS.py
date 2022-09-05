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

    def __init__(self):

        self.z = 7
        self.isPlayer = False
        self.radius = sper(0.0256)
        self.color = (128,128,128)
        self.drawRadius = self.radius
        self.drawColor = self.color
        self.ang = random.uniform(0,math.pi*2)
        self.turretAng = self.ang 
        self.vel = 0
        self.angVel = self.vel
        self.turretAngVel = self.vel
        self.hitCD = 0
        self.primaryShotCD = 0
        self.secondaryShotCD = 0
        self.shieldCD = 0
        self.shieldOverheat = 0
        self.shieldCapacity = 5
        self.shieldCharge = 0
        self.shielded = False
        self.health = 1
        self.healthRegenCD = 1
        self.healthRegenSpeed = 1
        self.attack = 1
        self.defense = 1
        self.moveSpeed = 1
        self.primaryShotAS = 1
        self.secondaryShotAS = 1
        self.shieldAugment = 0
        self.shieldChargeSpeed = 1
        self.borderPushX = 0
        self.borderPushY = 0
        self.showHitbox = False

        tanks.append(self)

    def process(self):

        self.hitCD = max(self.hitCD - deltaT, 0)
        self.primaryShotCD = max(self.primaryShotCD - deltaT, 0)
        self.secondaryShotCD = max(self.secondaryShotCD - deltaT, 0)
        self.healthRegenCD = max(self.healthRegenCD - deltaT, 0)
        self.shieldCD = max(self.shieldCD - deltaT, 0)
        self.shieldOverheat = max(self.shieldOverheat - deltaT/3, 0)
        if not self.shielded:
            charge = deltaT*self.shieldChargeSpeed if self.shieldCharge > 0.2 else deltaT
            self.shieldCharge = max(min(self.shieldCharge + charge, self.shieldCapacity + self.shieldAugment),0)

        self.ang += self.angVel * self.moveSpeed * deltaT
        self.turretAng += self.turretAngVel * self.moveSpeed * deltaT
        self.x += ((math.cos(self.ang)*self.vel) + self.borderPushX) * self.moveSpeed * deltaT
        self.y += ((math.sin(self.ang)*self.vel) + self.borderPushY) * self.moveSpeed * deltaT

        self.angVel *= 0.95
        self.turretAngVel *= 0.95
        self.vel *= 0.99
        self.borderPushX *= 0.99
        self.borderPushY *= 0.99

        if self.ang > math.pi*2 or self.ang < -math.pi*2: self.ang = 0
        if self.turretAng > math.pi*2 or self.turretAng < -math.pi*2: self.turretAng = 0

        for tank in tanks:
            if tank != self:
                if getDist((self.x,self.y),(tank.x,tank.y)) <= self.radius + tank.radius:

                    bumpAng = getAngle2(self.ang,(self.x,self.y),(tank.x,tank.y))

                    self.x -= math.cos(bumpAng)*tank.radius/4
                    self.y -= math.sin(bumpAng)*tank.radius/4
                    self.vel *= 1 - (tank.radius/100)

                    tank.x += math.cos(bumpAng)*self.radius/4
                    tank.y += math.sin(bumpAng)*self.radius/4
                    tank.vel *= 1 - (self.radius/100)

        for box in lootBoxes:
            if getDist((self.x,self.y),(box.x,box.y)) <= self.radius + box.radius:

                bumpAng = getAngle2(self.ang,(self.x,self.y),(box.x,box.y))

                self.x -= math.cos(bumpAng)*box.radius/4
                self.y -= math.sin(bumpAng)*box.radius/4

                box.x += math.cos(bumpAng)*self.radius/4
                box.y += math.sin(bumpAng)*self.radius/4

        if self.health < 1 and self.health > 0 and self.healthRegenCD == 0:
            self.health = min(self.health+0.005, 1)
            self.healthRegenCD = 10 * self.healthRegenSpeed

        for shot in shots:
            if self.isPlayer and not shot.isPlayerShot or not self.isPlayer and shot.isPlayerShot:
                distToShot = getDist((self.x,self.y),(shot.x,shot.y))

                if self.shielded:

                    if distToShot <= self.radius*1.5: spritesToRemove.append(shot)
                    if distToShot <= self.radius*2.5:

                        if not shot.missile:
                            shot.x, shot.y = shot.preX, shot.preY
                            shot.ang += math.pi + random.uniform(-math.pi/4,math.pi/4)
                            shot.isPlayerShot = not shot.isPlayerShot

                elif distToShot < self.radius:

                    self.health = max(self.health - 0.05 * (player[0].attack if player and shot.isPlayerShot else shot.attack) * self.defense * (10 if shot.missile else 1),0)
                    self.hitCD = 0.03
                    if shot.isPlayerShot and player: player[0].score += 250 if shot.missile else 25
                    spritesToRemove.append(shot)

        if self.health == 0:
            if not self.isPlayer:
                if player: player[0].score += self.scoreValue
                amount = self.dropCoins if manager[0].hardMode or self.scoreValue == 10000 else int(self.dropCoins*1.5)
                value = 40 if self.scoreValue == 10000 else random.randint(20,30) if manager[0].hardMode else random.randint(28,42)
                for i in range(amount): addSprite(Coin(self.x, self.y, value + self.coinValue))
                spritesToRemove.append(self)

        self.shielded = False
        self.drawRadius = random.uniform(self.radius*0.8,self.radius*1.2) if self.hitCD > 0 else self.radius

    def draw(self):

        self.drawColor = modifyColor(self.color,112) if self.hitCD > 0 else (255,255,0) if self.isPlayer and self.coinGrabbedCD > 0 else randColor() if self.isPlayer and self.powerModeActiveTime > 0 else self.color

        points = []
        points.append((self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius))
        points.append((self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius))
        points.append((self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius))
        points.append((self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius))
        for i in range(10):
            pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,0.9),(self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius*(1-i*0.2), self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius*(1-i*0.2)),(self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius*(1-i*0.2), self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius*(1-i*0.2)),int(self.drawRadius/2.5))
        for i in range(len(points)):
            pygame.draw.line(windowSurface, self.drawColor, points[i], points[(i+1)%len(points)], int(self.drawRadius/3.5))

        if self.shielded: pygame.draw.circle(windowSurface, (52,204,255), (self.x, self.y), self.drawRadius*2.5, int(self.drawRadius/5))

        if self.showHitbox:
            pygame.draw.rect(windowSurface, (255,255,0), pygame.Rect(self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2), int(self.radius/6))
            pygame.draw.circle(windowSurface, (0,255,255), (self.x, self.y), self.radius, int(self.radius/6))

    def shieldAction(self):

        if self.shieldCharge > 0 and self.shieldCD == 0:
            self.shielded = True
            self.shieldCharge -= deltaT*1.5
            pygame.draw.circle(windowSurface, (52,204,255), (self.x, self.y), self.drawRadius*2.5, int(self.drawRadius/5))

        elif self.shieldCD == 0:
            self.shieldOverheat += deltaT

        if self.shieldOverheat >= 1:
            self.shieldCD = 10
            self.shieldOverheat = 0

    def primaryShotAction(self):

        recoilAng = self.turretAng + math.pi
        if self.primaryShotCD == 0:
            color = randColor() if self.isPlayer and self.powerModeActiveTime > 0 else self.color
            addSprite(PrimaryShot(color,self.radius,self.turretAng,self.x,self.y,self.isPlayer,self.attack,self.showHitbox))
            self.x += math.cos(recoilAng)*sper(0.0016)
            self.y += math.sin(recoilAng)*sper(0.0016)
            self.primaryShotCD = 1 * self.primaryShotAS

    def secondaryShotAction(self):

        recoilAng = self.turretAng + math.pi
        if self.secondaryShotCD == 0:
            color = randColor() if self.isPlayer and self.powerModeActiveTime > 0 else self.color
            addSprite(SecondaryShot(color,self.radius,self.turretAng,self.x,self.y,self.isPlayer,self.attack,self.showHitbox))
            self.x += math.cos(recoilAng)*sper(0.012)
            self.y += math.sin(recoilAng)*sper(0.012)
            self.secondaryShotCD = 10 * self.secondaryShotAS

    def getBorderPush(self):
        self.borderPushX += sper(0.0032) if self.x < 0 + self.radius else -sper(0.0032) if self.x > screenX - self.radius else 0
        self.borderPushY += sper(0.0032) if self.y < 0 + self.radius else -sper(0.0032) if self.y > screenY - self.radius else 0

class Player(Tank):

    def __init__(self):

        super().__init__()

        self.isPlayer = True
        self.radius = sper(0.0128)
        self.x, self.y = xper(0.5), yper(0.5)
        self.forward = pygame.K_w
        self.reverse = pygame.K_s
        self.left = pygame.K_a
        self.right = pygame.K_d
        self.shield = pygame.K_SPACE
        self.primaryShot = mouseLeft
        self.secondaryShot = mouseRight
        self.powerMode = mouseMiddle
        self.power = False
        self.powerModeActiveTime = 0
        self.powHealthRegenSpeed = 0.0025
        self.powAttack = 4
        self.powDefense = 0
        self.powPrimaryShotAS = 0.05
        self.powSecondaryShotAS = 0.05
        self.powMoveSpeed = 2
        self.regHealthRegenSpeed = 1
        self.regAttack = 1
        self.regDefense = 1
        self.regPrimaryShotAS = 0.5
        self.regSecondaryShotAS = 1
        self.regMoveSpeed = 1
        self.healthRegenSpeed = self.regHealthRegenSpeed
        self.attack = self.regAttack
        self.defense = self.regDefense
        self.primaryShotAS = self.regPrimaryShotAS
        self.secondaryShotAS = self.regSecondaryShotAS
        self.moveSpeed = self.regMoveSpeed
        self.shieldAugment = 0
        self.shieldChargeSpeed = 1
        self.moneyToAdd = 0
        self.moneyToAddCD = 0
        self.coinGrabbedCD = 0
        self.money = 0
        self.score = 0

        player.append(self)

    def process(self):

        if manager[0].menu: self.color = manager[0].playerColors[manager[0].colorSelected]

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            self.moneyToAddCD = max(self.moneyToAddCD - deltaT, 0)
            self.coinGrabbedCD = max(self.coinGrabbedCD - deltaT, 0)
            self.powerModeActiveTime = max(self.powerModeActiveTime - deltaT, 0)

            self.primaryShot, self.secondaryShot, self.powerMode = (mouseLeft,mouseRight,mouseMiddle)

            if keys[self.forward]: self.vel += sper(0.0012)
            if keys[self.reverse]: self.vel -= sper(0.0012)
            if keys[self.left]: self.angVel -= sper(0.000125)
            if keys[self.right]: self.angVel += sper(0.000125)
            if keys[self.shield]: self.shieldAction()
            if self.primaryShot: self.primaryShotAction()
            if self.secondaryShot: self.secondaryShotAction()
            if self.powerMode: self.powerModeAction()

            aimAngle = getAngle2(self.turretAng,(self.x,self.y),(mouseX,mouseY))
            self.turretAngVel += sper(0.00015) if aimAngle > self.turretAng else -sper(0.00015)

            self.getBorderPush()

            for coin in coins:
                if getDist((self.x,self.y),(coin.x,coin.y)) < sper(0.15):
                    coin.ang = getAngle2(coin.ang,(coin.x,coin.y),(self.x,self.y))
                    coin.vel += sper(1) * deltaT
                    coin.grabbed = True
                    if getDist((self.x,self.y),(coin.x,coin.y)) < self.radius+coin.radius and not coin.accounted:
                        self.moneyToAdd += coin.value
                        self.coinGrabbedCD = 0.03
                        coin.accounted = True
                        spritesToRemove.append(coin)

            if self.health == 0:
                if not manager[0].victory:
                    manager[0].gameover = True
                    dropLimit = 50
                    while self.money > 40 and dropLimit > 0:
                        value = random.randint(30,50)
                        addSprite(Coin(self.x,self.y,value))
                        self.money -= value
                        dropLimit -= 1
                    spritesToRemove.append(self)
                    player.clear()

            if self.moneyToAdd > 0 and self.moneyToAddCD == 0:
                transfer = 10 if self.moneyToAdd > 1000 else 1
                self.moneyToAdd -= transfer
                self.money += transfer
                self.moneyToAddCD = 0.01

            if self.powerModeActiveTime > 0:
                self.healthRegenCD = self.powHealthRegenSpeed
                self.attack = self.powAttack
                self.defense = self.powDefense
                self.primaryShotAS = self.powPrimaryShotAS
                self.secondaryShotAS = self.powSecondaryShotAS
                self.moveSpeed = self.powMoveSpeed

            else:
                self.attack = self.regAttack
                self.defense = self.regDefense
                self.primaryShotAS = self.regPrimaryShotAS
                self.secondaryShotAS = self.regSecondaryShotAS
                self.moveSpeed = self.regMoveSpeed

            manager[0].playerScore = self.score

    def draw(self):

        super().draw()

        if self.powerModeActiveTime > 0:
            timeLeft = self.powerModeActiveTime * 100 / 30 * 0.01
            pygame.draw.line(windowSurface, (0,0,0),(self.x-self.drawRadius*1.5, self.y-self.drawRadius*1.75),(self.x-self.drawRadius*1.5 + self.drawRadius*3, self.y-self.drawRadius*1.75), int(self.drawRadius/3))
            pygame.draw.line(windowSurface, self.drawColor,(self.x-self.drawRadius*1.425, self.y-self.drawRadius*1.76),(self.x-self.drawRadius*1.425 + self.drawRadius*2.925*timeLeft, self.y-self.drawRadius*1.76), int(self.drawRadius/5))

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x + math.cos(self.ang) * -self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * -self.drawRadius + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x + math.cos(self.ang) * self.drawRadius + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x + math.cos(self.ang) * -self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*1.25, self.y + math.sin(self.turretAng) * self.drawRadius*1.25), int(self.drawRadius/2))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,3), (self.x, self.y), self.drawRadius*0.7)

    def powerModeAction(self):

        if self.power:
            if self.powerModeActiveTime == 0:
                self.powerModeActiveTime = 30
                self.secondaryShotCD = 0
                self.power = False

class Enemy(Tank):

    def __init__(self):

        super().__init__()

        spawnSide = random.randint(0,3)
        spawnArea = ((xper(-0.3),xper(1.3),yper(-0.1),yper(-0.3)),
                     (xper(1.1),xper(1.3),yper(-0.3),yper(1.3)),
                     (xper(-0.3),xper(1.3),yper(1.1),yper(1.3)),
                     (xper(-0.1),xper(-0.3),yper(-0.3),yper(1.3)))
        self.x = random.uniform(spawnArea[spawnSide][0],spawnArea[spawnSide][1])
        self.y = random.uniform(spawnArea[spawnSide][2],spawnArea[spawnSide][3])
        self.maxDistToPlayer = random.uniform(sper(0.128),sper(0.512))
        self.inScreen = False
        self.playerLocked = True
        self.scoutModeTimer = 0
        self.aimPointForwardX = xper(0.5)
        self.aimPointForwardY = yper(0.5)
        self.targetX = 0
        self.targetY = 0
        self.shieldUpCD = 0
        self.showLines = False
        self.dropCoins = 0
        self.coinValue = 0
        self.scoreValue = 0
        self.drawAura = False

        reroll = True
        while reroll:
            self.scoutX, self.scoutY = random.randint(xper(0.1),screenX-xper(0.1)), random.randint(yper(0.1),screenY-yper(0.1))
            reroll = False
            for wall in walls:
                if rectCollision((self.scoutX-self.radius*2, self.scoutY-self.radius*2, self.radius*4, self.radius*4),(wall.x, wall.y, wall.width, wall.height)):
                    reroll = True
                    break

        enemies.append(self)

    def process(self):

        super().process()

        self.shieldUpCD = max(self.shieldUpCD - deltaT, 0)
        if self.shieldUpCD > 0: self.shieldAction()

        if player: self.targetX, self.targetY, self.targetRadius = player[0].x, player[0].y, player[0].radius
        if not player or self.scoutModeTimer > 15: self.playerLocked = False

        self.aimAngle = getAngle2(self.turretAng,(self.x,self.y),(self.targetX,self.targetY))

        if self.shotAllowed():
            self.playerLocked = True
            self.scoutModeTimer = 0

            distToPlayer = getDist((self.x,self.y),(self.targetX,self.targetY))
            if distToPlayer > self.maxDistToPlayer or not self.inScreen:
                self.vel += sper(0.0012)
            elif distToPlayer < self.maxDistToPlayer/3:
                self.vel -= sper(0.0012)

        else:
            self.vel += sper(0.0012)
            self.scoutModeTimer += deltaT

        self.moveAngle = getAngle2(self.ang,(self.x,self.y),((self.targetX,self.targetY) if self.playerLocked else (self.scoutX,self.scoutY)))

        directionChange = 0
        for i in range(8):
            pointForwardX, pointForwardY = (self.x + math.cos(self.moveAngle)*self.radius*i, self.y + math.sin(self.moveAngle)*self.radius*i)
            pointRightX, pointRightY = (self.x + math.cos(self.moveAngle + math.pi/2)*self.radius*i, self.y + math.sin(self.moveAngle + math.pi/2)*self.radius*i)
            pointLeftX, pointLeftY = (self.x + math.cos(self.moveAngle - math.pi/2)*self.radius*i, self.y + math.sin(self.moveAngle - math.pi/2)*self.radius*i)

            for wall in walls:

                if rectPointCollision((wall.x, wall.y, wall.width, wall.height), (pointForwardX, pointForwardY)):

                    for wall2 in walls:

                        if not rectPointCollision((wall2.x, wall2.y, wall2.width, wall2.height), (pointRightX, pointRightY)):
                            directionChange = math.pi/2

                        elif not rectPointCollision((wall2.x, wall2.y, wall2.width, wall2.height), (pointLeftX, pointLeftY)):
                            directionChange = -math.pi/2
                            break

            if directionChange != 0: break

        self.moveAngle += directionChange
        self.angVel += sper(0.000125) if self.moveAngle > self.ang else -sper(0.000125)
        self.turretAngVel += sper(0.00015) if self.aimAngle > self.turretAng else -sper(0.00015)

        if not self.playerLocked:
            self.turretAng = self.ang

        if not self.inScreen and self.x < screenX-self.radius*2 and self.x > 0+self.radius*2 and self.y < screenY-self.radius*2 and self.y > 0+self.radius*2:
            self.inScreen = True
        if self.inScreen: self.getBorderPush()

    def draw(self):

        super().draw()

        if self.health < 1:
            healthBarColor = (min(abs(255*(self.health-0.5)-255),255),max(255*(self.health),0),0)
            pygame.draw.line(windowSurface, (0,0,0),(self.x-self.drawRadius*1.5, self.y-self.drawRadius*1.75),(self.x-self.drawRadius*1.5 + self.drawRadius*3, self.y-self.drawRadius*1.75), int(self.drawRadius/3))
            pygame.draw.line(windowSurface, healthBarColor,(self.x-self.drawRadius*1.425, self.y-self.drawRadius*1.76),(self.x-self.drawRadius*1.425 + self.drawRadius*2.925*self.health, self.y-self.drawRadius*1.76), int(self.drawRadius/5))

        if self.drawAura:
            pygame.draw.circle(windowSurface, randColorGray(200,255), (self.x, self.y-self.radius*3), self.drawRadius*0.2)
            for i in range(3):
                pygame.draw.circle(windowSurface, randColorGray(100,255), (self.x + math.cos(self.ang) * self.drawRadius*(0.7-i*0.7) + math.cos(self.ang + math.pi/2) * self.drawRadius*0.8, self.y + math.sin(self.ang) * self.drawRadius*(0.7-i*0.7) + math.sin(self.ang + math.pi/2) * self.drawRadius*0.8), self.drawRadius*0.2,int(self.drawRadius/10))
                pygame.draw.circle(windowSurface, randColorGray(100,255), (self.x + math.cos(self.ang) * self.drawRadius*(0.7-i*0.7) + math.cos(self.ang + math.pi/2) * -self.drawRadius*0.8, self.y + math.sin(self.ang) * self.drawRadius*(0.7-i*0.7) + math.sin(self.ang + math.pi/2) * -self.drawRadius*0.8), self.drawRadius*0.2,int(self.drawRadius/10))

        if self.showLines:
            pygame.draw.rect(windowSurface, (200,150,0), pygame.Rect(self.scoutX-self.radius*2, self.scoutY-self.radius*2, self.radius*4, self.radius*4), int(self.radius/6))
            if player and self.playerLocked: pygame.draw.line(windowSurface, (150,0,0),(self.x, self.y),(self.aimPointForwardX,self.aimPointForwardY), int(self.radius/8))
            pygame.draw.line(windowSurface, (0,150,0),(self.x, self.y),(self.x + math.cos(self.moveAngle)*self.radius*8, self.y + math.sin(self.moveAngle)*self.radius*8), int(self.radius/6))

    def shotAllowed(self):

        if not player or not self.inScreen:
            return False

        for i in range(50):

            self.aimPointForwardX, self.aimPointForwardY = (self.x + math.cos(self.aimAngle)*self.radius*i, self.y + math.sin(self.aimAngle)*self.radius*i)

            if rectPointCollision((self.targetX-self.targetRadius, self.targetY-self.targetRadius, self.targetRadius*2, self.targetRadius*2), (self.aimPointForwardX, self.aimPointForwardY)):
                return True

            else:
                for wall in walls:
                    if rectPointCollision((wall.x, wall.y, wall.width, wall.height), (self.aimPointForwardX, self.aimPointForwardY)):
                        return False

    def shieldEval(self):

        for shot in shots:
            if shot.isPlayerShot:
                if getDist((self.x,self.y),(shot.x,shot.y)) < self.radius*3:
                    self.shieldAction()
                    self.shieldUpCD = 0.5

class SmallPink(Enemy):

    def __init__(self):

        super().__init__()

        self.color = (175,0,175)
        self.radius = sper(0.0096)
        self.healthRegenSpeed = 1
        self.attack = 0.1
        self.defense = 7
        self.moveSpeed = 1.2
        self.primaryShotAS = 0.3
        self.secondaryShotAS = 1
        self.shieldAugment = -4.5
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(0,2)
        self.coinValue = 0
        self.scoreValue = 60

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.25), (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius), (self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.25), (self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius), (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*1.75, self.y + math.sin(self.turretAng) * self.drawRadius*1.75), int(self.drawRadius/4))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2), (self.x, self.y), self.drawRadius*0.5)

class BasicRed(Enemy):

    def __init__(self):

        super().__init__()

        self.radius = sper(0.0128)
        self.color = (75,0,0)
        self.healthRegenSpeed = 1
        self.attack = 0.5
        self.defense = 3
        self.moveSpeed = 0.9
        self.primaryShotAS = 1
        self.secondaryShotAS = 1
        self.shieldAugment = -4.5
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(2,3)
        self.coinValue = 5
        self.scoreValue = 105

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*1.75, self.y + math.sin(self.turretAng) * self.drawRadius*1.75), int(self.drawRadius/4))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), self.drawRadius*0.6)

class BasicBlue(Enemy):

    def __init__(self):

        super().__init__()

        self.radius = sper(0.0128)
        self.color = (0,0,150)
        self.healthRegenSpeed = 1
        self.attack = 0.8
        self.defense = 2
        self.moveSpeed = 1
        self.primaryShotAS = 0.8
        self.secondaryShotAS = 1
        self.shieldAugment = -4.5
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(4,6)
        self.coinValue = 5
        self.scoreValue = 210

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x + math.cos(self.ang) * -self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * -self.drawRadius + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/4))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), self.drawRadius*0.6)

class Rhomb(Enemy):

    def __init__(self):

        super().__init__()

        self.sRedInt = 100
        self.startRadius = sper(0.01)
        self.healthRegenSpeed = 1
        self.startAttack = 0.2
        self.startDefense = 3
        self.moveSpeed = 1.3
        self.primaryShotAS = 0.2
        self.secondaryShotAS = 1
        self.shieldAugment = -4.5
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(6,9)
        self.coinValue = 10
        self.scoreValue = 360

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()

            self.defense = max(self.startDefense * self.health,0.1)
            self.attack = self.startAttack + abs(self.health-1)
            self.radius = min(self.startRadius * (1 + abs(self.health-1)),sper(0.02))
            self.eRedInt = self.sRedInt * (1 + abs(self.health-1))
            self.color = (self.eRedInt,max(50*self.health,0),max(50*self.health,0))

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius), (self.x + math.cos(self.ang)*self.drawRadius*1.25, self.y + math.sin(self.ang)*self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang)*self.drawRadius*1.25, self.y + math.sin(self.ang)*self.drawRadius*1.25), (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius), (self.x - math.cos(self.ang)*self.drawRadius*1.25, self.y - math.sin(self.ang)*self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang)*self.drawRadius*1.25, self.y - math.sin(self.ang)*self.drawRadius*1.25), (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/4))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,3), (self.x, self.y), self.drawRadius*0.6)

class Icy(Enemy):

    def __init__(self):

        super().__init__()

        self.radius = sper(0.0128)
        self.color = (0,125,150)
        self.healthRegenSpeed = 1
        self.attack = 0.5
        self.defense = 0.7
        self.moveSpeed = 0.9
        self.primaryShotAS = 0.5
        self.secondaryShotAS = 1
        self.shieldAugment = -3
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(8,12)
        self.coinValue = 10
        self.scoreValue = 480

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()

            self.shieldEval()

            if player:
                for shot in shots:
                    if shot.color == modifyColor(self.color,150):
                        if getDist((player[0].x,player[0].y),(shot.x,shot.y)) < player[0].radius and player[0].powerModeActiveTime == 0:
                            player[0].vel *= 0.1

    def draw(self):

        super().draw()

        for i in range(1,19):
            pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x, self.y), (self.x + math.cos(math.pi*2*i/18) * self.drawRadius*(1.4 if i % 2 == 0 else 1.1), self.y + math.sin(math.pi*2*i/18) * self.drawRadius*(1.4 if i % 2 == 0 else 1.1)), int(self.drawRadius/5))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x, self.y), self.drawRadius,int(self.drawRadius/5))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*3, self.y + math.sin(self.turretAng) * self.drawRadius*3), int(self.drawRadius/4))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), self.drawRadius*0.7)

class Purple(Enemy):

    def __init__(self):

        super().__init__()

        self.radius = sper(0.017)
        self.color = (60,24,90)
        self.healthRegenSpeed = 1
        self.attack = 1.1
        self.defense = 1
        self.moveSpeed = 1
        self.primaryShotAS = 0.5
        self.secondaryShotAS = 1
        self.shieldAugment = -4
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(10,14)
        self.coinValue = 15
        self.scoreValue = 630

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()
                self.secondaryShotAction()

            self.shieldEval()

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x + math.cos(self.ang) * -self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * -self.drawRadius + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2.25), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*1.25, self.y + math.sin(self.turretAng) * self.drawRadius*1.25), int(self.drawRadius/2))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), self.drawRadius*0.6)

class Mortar(Enemy):

    def __init__(self):

        super().__init__()

        self.radius = sper(0.0128)
        self.color = (150,150,0)
        self.healthRegenSpeed = 1
        self.attack = 1
        self.defense = 1
        self.moveSpeed = 0.4
        self.primaryShotAS = 1
        self.secondaryShotAS = 0.3
        self.shieldAugment = -2
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(12,17)
        self.coinValue = 15
        self.scoreValue = 765

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.secondaryShotAction()

            self.shieldEval()

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang)*self.drawRadius*1.25, self.y - math.sin(self.ang)*self.drawRadius*1.25),(self.x + math.cos(self.ang)*self.drawRadius*1.25, self.y + math.sin(self.ang)*self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius), (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2.25), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*1.5, self.y + math.sin(self.turretAng) * self.drawRadius*1.5), int(self.drawRadius/2))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), self.drawRadius*0.8)

class Invis(Enemy):

    def __init__(self):

        super().__init__()

        self.radius = sper(0.0128)
        self.healthRegenSpeed = 0.005
        self.attack = 4
        self.defense = 1
        self.moveSpeed = 0.7
        self.primaryShotAS = 3
        self.secondaryShotAS = 1
        self.shieldAugment = -4.5
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(13,18)
        self.coinValue = 15
        self.scoreValue = 810

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()

        self.color = (background[0],background[1],background[2])

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface,self.drawColor, (self.x + math.cos(self.ang) * -self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * -self.drawRadius + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface,self.drawColor, (self.x + math.cos(self.ang) * self.drawRadius + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface,self.drawColor, (self.x + math.cos(self.ang) * -self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface,self.drawColor, (self.x + math.cos(self.ang) * self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * self.drawRadius + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface,self.drawColor, (self.x + math.cos(self.ang) * -self.drawRadius + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * -self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface,self.drawColor, (self.x + math.cos(self.ang) * self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * -self.drawRadius*0.4 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*0.4 + math.sin(self.ang + math.pi/2) * -self.drawRadius),int(self.drawRadius/4))
        pygame.draw.line(windowSurface,self.drawColor, (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/4))
        pygame.draw.circle(windowSurface,self.drawColor, (self.x, self.y), self.drawRadius*0.6)

class Exploder(Enemy):

    def __init__(self):

        super().__init__()

        self.color = (140,70,0)
        self.radius = sper(0.0128)
        self.healthRegenSpeed = 1
        self.attack = 2
        self.defense = 1
        self.moveSpeed = 1
        self.primaryShotAS = 0.5
        self.secondaryShotAS = 1
        self.shieldAugment = -4.5
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(14,20)
        self.coinValue = 15
        self.scoreValue = 900

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                    self.primaryShotAction()

            if self.health < 0.4:
                self.color = randColorInRange(180,255,90,180,0,0)
                self.vel += sper(0.0024)
                self.moveSpeed = 1.2
                self.drawRadius = random.uniform(self.radius,self.radius*1.5)

                if player:
                    if getDist((self.x,self.y),(player[0].x,player[0].y)) <= (self.radius + player[0].radius)*1.1:
                        self.health = 0
                        spritesToRemove.append(self)

                    if self.health <= 0:
                        if getDist((player[0].x,player[0].y),(self.x,self.y)) < self.radius*6 and player[0].powerModeActiveTime == 0:
                            player[0].health -= 0.4 if not player[0].shielded else 0.1
                            player[0].hitCD = 0.03

    def draw(self):

        super().draw()

        for i in range(4):
            pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5),(self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius*(0.6-i*0.4), self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius*(0.6-i*0.4)),(self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius*(0.6-i*0.4), self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius*(0.6-i*0.4)),int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,3), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/3))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,3), (self.x, self.y), self.drawRadius*0.8)

class Commander(Enemy):

    def __init__(self):

        super().__init__()

        self.radius = sper(0.0228)
        self.healthRegenSpeed = 0.01
        self.attack = 1.5
        self.defense = 0.5
        self.moveSpeed = 0.8
        self.primaryShotAS = 0.1
        self.secondaryShotAS = 1
        self.shieldAugment = 0
        self.shieldChargeSpeed = 1
        self.dropCoins = random.randint(17,25)
        self.coinValue = 20
        self.scoreValue = 1250
        self.auraCD = 0

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()

            self.shieldEval()

            self.color = randColorGray(100,150)
            self.auraCD = max(self.auraCD - deltaT, 0)

            if self.auraCD == 0 or self.health <= 0:
                for tank in tanks:
                    if not tank.isPlayer and tank != self:

                        if self.health <= 0: tank.drawAura = False

                        elif getDist((self.x,self.y),(tank.x,tank.y)) < self.radius*10:
                            tank.drawAura = True
                            tank.primaryShotCD *= 0.9
                            tank.secondaryShotCD *= 0.995
                            tank.healthRegenCD *= 0.2
                            tank.shieldEval()

                        else: tank.drawAura = False

                self.auraCD = 0.01

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius), (self.x + math.cos(self.ang) * self.drawRadius*1.25, self.y + math.sin(self.ang) * self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius), (self.x - math.cos(self.ang) * self.drawRadius*0.5, self.y - math.sin(self.ang) * self.drawRadius*0.5), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius), (self.x + math.cos(self.ang) * self.drawRadius*1.25, self.y + math.sin(self.ang) * self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius), (self.x - math.cos(self.ang) * self.drawRadius*0.5, self.y - math.sin(self.ang) * self.drawRadius*0.5), int(self.drawRadius/4))
        for i in range(3):
            pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x + math.cos(self.ang) * self.drawRadius*(0.7-i*0.7) + math.cos(self.ang + math.pi/2) * self.drawRadius*0.8, self.y + math.sin(self.ang) * self.drawRadius*(0.7-i*0.7) + math.sin(self.ang + math.pi/2) * self.drawRadius*0.8), self.drawRadius*0.2,int(self.drawRadius/8))
            pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x + math.cos(self.ang) * self.drawRadius*(0.7-i*0.7) + math.cos(self.ang + math.pi/2) * -self.drawRadius*0.8, self.y + math.sin(self.ang) * self.drawRadius*(0.7-i*0.7) + math.sin(self.ang + math.pi/2) * -self.drawRadius*0.8), self.drawRadius*0.2,int(self.drawRadius/8))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,3), (self.x, self.y), self.drawRadius*0.7)
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/3))

class Breeder(Enemy):

    def __init__(self):

        super().__init__()

        self.color = (75,0,75)
        self.radius = sper(0.032)
        self.healthRegenSpeed = 1
        self.attack = 1
        self.defense = 0.1
        self.moveSpeed = 0.2
        self.primaryShotAS = 1
        self.secondaryShotAS = 1
        self.shieldAugment = 10
        self.shieldChargeSpeed = 2
        self.dropCoins = random.randint(21,30)
        self.coinValue = 20
        self.scoreValue = 1500
        self.spawnTimer = 0

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            self.shieldEval()

            self.spawnTimer = max(self.spawnTimer - deltaT, 0)

            if self.spawnTimer == 0:
                addSprite(BreederChild(self.x,self.y))
                self.spawnTimer = 10

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang)*self.drawRadius*1.25, self.y - math.sin(self.ang)*self.drawRadius*1.25),(self.x + math.cos(self.ang)*self.drawRadius*1.25, self.y + math.sin(self.ang)*self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius), (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius), (self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius), (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius), int(self.drawRadius/4))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), self.drawRadius*0.9,int(self.drawRadius/5))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), self.drawRadius*0.6,int(self.drawRadius/5))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,2.5), (self.x, self.y), self.drawRadius*0.3)

class BreederChild(SmallPink):

    def __init__(self,x,y):

        super().__init__()

        self.x = x
        self.y = y

class BossGreen(Enemy):

    def __init__(self):

        super().__init__()

        self.color = (0,100,0)
        self.radius = sper(0.0256)
        self.healthRegenSpeed = 1
        self.attack = 2
        self.defense = 0.3
        self.moveSpeed = 0.5
        self.primaryShotAS = 0.7
        self.secondaryShotAS = 1
        self.shieldAugment = 5
        self.shieldChargeSpeed = 2
        self.dropCoins = random.randint(28,40)
        self.coinValue = 20
        self.scoreValue = 2000

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()
                self.secondaryShotAction()

            self.shieldEval()

    def draw(self):

        super().draw()

        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius), (self.x + math.cos(self.ang)*self.drawRadius*1.25, self.y + math.sin(self.ang)*self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang)*self.drawRadius*1.25, self.y + math.sin(self.ang)*self.drawRadius*1.25), (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius), (self.x - math.cos(self.ang)*self.drawRadius*1.25, self.y - math.sin(self.ang)*self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang)*self.drawRadius*1.25, self.y - math.sin(self.ang)*self.drawRadius*1.25), (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang)*self.drawRadius*1.25, self.y - math.sin(self.ang)*self.drawRadius*1.25),(self.x + math.cos(self.ang)*self.drawRadius*1.25, self.y + math.sin(self.ang)*self.drawRadius*1.25), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,1.5), (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius), (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/4))
        pygame.draw.line(windowSurface, modifyColorPerc(self.drawColor,2.25), (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*1.25, self.y + math.sin(self.turretAng) * self.drawRadius*1.25), int(self.drawRadius/2))
        pygame.draw.circle(windowSurface, modifyColorPerc(self.drawColor,3), (self.x, self.y), self.drawRadius*0.6)

class FinalBoss(Enemy):

    def __init__(self):

        super().__init__()

        self.radius = sper(0.035)
        self.healthRegenSpeed = 1
        self.attack = 2
        self.defense = 0.015
        self.moveSpeed = 1
        self.primaryShotAS = 0.2
        self.secondaryShotAS = 0.3
        self.shieldAugment = 25
        self.shieldChargeSpeed = 3
        self.dropCoins = 50
        self.coinValue = 50
        self.scoreValue = 10000
        self.teleportCD = 10
        self.spawnCD = 0
        self.rageMode = False
        self.maxDistToPlayer = sper(0.2)
        self.shieldCharge = 30

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            super().process()

            if self.shotAllowed():
                self.primaryShotAction()
                self.secondaryShotAction()

            self.shieldEval()

            self.teleportCD = max(self.teleportCD - deltaT, 0)
            self.spawnCD = max(self.spawnCD - deltaT, 0)

            c = (int(min(abs(255*(self.health-0.5)-255),255)),int(max(255*(self.health),0)),0)
            self.color = randColorInRange(c[0]//5, c[0]//3, c[1]//5, c[1]//3, c[2], c[2])

            if self.teleportCD < 3 and player:
                self.color = randColorInRange(75,150,75,150,200,255)
                self.drawRadius = random.uniform(self.radius*0.9,self.radius*1.1)

                if self.teleportCD == 0:
                    reroll = True
                    while reroll:
                        self.x, self.y = random.randint(0,screenX), random.randint(0,screenY)
                        reroll = False
                        for wall in walls:
                            if rectCollision((self.x-self.radius, self.y-self.radius, self.radius*2, self.radius*2),(wall.x, wall.y, wall.width, wall.height)):
                                reroll = True
                                break
                    self.ang = getAngle((self.x,self.y),(player[0].x,player[0].y))
                    self.turretAng = self.ang
                    self.teleportCD = 5 if self.rageMode else 20

            if self.health < 0.5 and self.spawnCD == 0 and len(enemies) < 10:
                chance = random.randint(0,3)
                if chance == 0:
                    for i in range(4): addSprite(Icy())
                elif chance == 1:
                    for i in range(4): addSprite(Mortar())
                elif chance == 2:
                    for i in range(4): addSprite(Invis())
                elif chance == 3:
                    for i in range(4): addSprite(Exploder())
                self.spawnCD = 60

            if self.health < 0.2 and not self.rageMode:
                self.primaryShotAS = 0.01
                self.secondaryShotAS = 0.1
                self.moveSpeed = 1.5
                self.teleportCD = 0.5
                self.rageMode = True

            if self.health <= 0:
                manager[0].victory = True
                for tank in tanks:
                    if not tank.isPlayer: tank.health = 0

    def draw(self):

        super().draw()

        for i in range(10):
            color =  randColor() if self.rageMode else modifyColorPerc(self.drawColor,(3-0.35*i))
            pygame.draw.line(windowSurface, color, (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius), (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius), int(self.drawRadius/(4+0.5*i)))
            pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius), (self.x - math.cos(self.ang) * self.drawRadius*0.9, self.y - math.sin(self.ang) * self.drawRadius*0.9), int(self.drawRadius/(4+0.5*i)))
            pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius), (self.x - math.cos(self.ang) * self.drawRadius*0.9, self.y - math.sin(self.ang) * self.drawRadius*0.9), int(self.drawRadius/(4+0.5*i)))
            pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius),(self.x + math.cos(self.ang) * self.drawRadius*0.9, self.y + math.sin(self.ang) * self.drawRadius*0.9), int(self.drawRadius/(4+0.5*i)))
            pygame.draw.line(windowSurface, color, (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius),(self.x + math.cos(self.ang) * self.drawRadius*0.9, self.y + math.sin(self.ang) * self.drawRadius*0.9), int(self.drawRadius/(4+0.5*i)))
            pygame.draw.circle(windowSurface, color, (self.x - math.cos(self.ang) * self.drawRadius*0.9, self.y - math.sin(self.ang) * self.drawRadius*0.9), self.drawRadius*(0.2-0.01*i))
            pygame.draw.circle(windowSurface, color, (self.x + math.cos(self.ang) * self.drawRadius*0.9, self.y + math.sin(self.ang) * self.drawRadius*0.9), self.drawRadius*(0.2-0.01*i))
            pygame.draw.circle(windowSurface, color, (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius),self.drawRadius*(0.2-0.01*i))
            pygame.draw.circle(windowSurface, color, (self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * -self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * -self.drawRadius),self.drawRadius*(0.2-0.01*i))
            pygame.draw.circle(windowSurface, color, (self.x + math.cos(self.ang) * self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius),self.drawRadius*(0.2-0.01*i))
            pygame.draw.circle(windowSurface, color, (self.x + math.cos(self.ang) * -self.drawRadius*1.25 + math.cos(self.ang + math.pi/2) * self.drawRadius, self.y + math.sin(self.ang) * -self.drawRadius*1.25 + math.sin(self.ang + math.pi/2) * self.drawRadius),self.drawRadius*(0.2-0.01*i))
            pygame.draw.circle(windowSurface, color, (self.x - math.cos(self.ang + math.pi/2)*self.drawRadius, self.y - math.sin(self.ang + math.pi/2)*self.drawRadius),self.drawRadius*(0.2-0.01*i))
            pygame.draw.circle(windowSurface, color, (self.x + math.cos(self.ang + math.pi/2)*self.drawRadius, self.y + math.sin(self.ang + math.pi/2)*self.drawRadius),self.drawRadius*(0.2-0.01*i))
            pygame.draw.line(windowSurface, color, (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*2, self.y + math.sin(self.turretAng) * self.drawRadius*2), int(self.drawRadius/(4+0.5*i)))
            pygame.draw.line(windowSurface, color, (self.x, self.y), (self.x + math.cos(self.turretAng) * self.drawRadius*1.25, self.y + math.sin(self.turretAng) * self.drawRadius*1.25), int(self.drawRadius/(2+0.5*i)))
            pygame.draw.circle(windowSurface, color, (self.x, self.y), self.drawRadius*(0.7-0.04*i))

class PrimaryShot(Sprite):

    def __init__(self, tankColor, tankRadius, tankTurretAng, tankX, tankY, tankIsPlayer, tankAttack, tankShowHitbox):

        self.z = 4
        self.color = modifyColor(tankColor,150)
        self.radius = tankRadius*0.3
        self.ang = tankTurretAng
        self.x = tankX + math.cos(self.ang)*self.radius*7
        self.y = tankY + math.sin(self.ang)*self.radius*7
        self.preX, self.preY = self.x, self.y
        self.vel = sper(0.8)
        self.missile = False
        self.isPlayerShot = tankIsPlayer
        self.attack = tankAttack
        self.showHitbox = tankShowHitbox

        shots.append(self)

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            self.preX, self.preY = self.x, self.y
            self.x += math.cos(self.ang)*self.vel*deltaT
            self.y += math.sin(self.ang)*self.vel*deltaT

            if self.x > screenX+self.radius*4 or self.x < 0-self.radius*4 or self.y > screenY+self.radius*4 or self.y < 0-self.radius*4:
                spritesToRemove.append(self)

    def draw(self):

        pygame.draw.line(windowSurface,self.color, (self.x - math.cos(self.ang) * self.radius*2, self.y - math.sin(self.ang) * self.radius*2), (self.x,self.y), int(self.radius/2))

        if self.showHitbox: pygame.draw.circle(windowSurface, (0,255,255), (self.x, self.y), self.radius)

class SecondaryShot(Sprite):

    def __init__(self, tankColor, tankRadius, tankTurretAng, tankX, tankY, tankIsPlayer, tankAttack, tankShowHitbox):

        self.z = 4
        self.color = tankColor
        self.baseColor = self.color
        self.glowColor = modifyColorPerc(self.color,2)
        self.colorTimer = 0
        self.radius = tankRadius*0.3
        self.ang = tankTurretAng
        self.x = tankX + math.cos(self.ang)*self.radius*4
        self.y = tankY + math.sin(self.ang)*self.radius*4
        self.vel = sper(0.48)
        self.angVel = sper(0.005)
        self.lifeSpan = random.randint(7,10)
        self.missile = True
        self.isPlayerShot = tankIsPlayer
        self.attack = tankAttack
        self.showHitbox = tankShowHitbox

        shots.append(self)

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            self.lifeSpan -= deltaT
            if self.lifeSpan <= 0: spritesToRemove.append(self)

            if player and self.isPlayerShot: self.targetX, self.targetY = mouseX, mouseY
            elif player: self.targetX, self.targetY = player[0].x, player[0].y
            else: self.targetX, self.targetY = random.randint(0,screenX),random.randint(0,screenY)

            aimAngle = getAngle2(self.ang,(self.x,self.y),(self.targetX,self.targetY))

            self.ang += self.angVel * deltaT if aimAngle > self.ang else -self.angVel * deltaT
            self.x += math.cos(self.ang)*self.vel*deltaT
            self.y += math.sin(self.ang)*self.vel*deltaT

            if self.ang > math.pi*2 or self.ang < -math.pi*2: self.ang = 0

            self.colorTimer += deltaT
            if self.colorTimer > 0.075:
                self.color = self.glowColor if self.color == self.baseColor else self.baseColor
                self.colorTimer = 0

    def draw(self):

        pygame.draw.line(windowSurface, self.color, (self.x - math.cos(self.ang) * self.radius*4, self.y - math.sin(self.ang) * self.radius*4), (self.x,self.y), int(self.radius*2))
        pygame.draw.circle(windowSurface, self.color, (self.x,self.y), self.radius)

        if self.showHitbox: pygame.draw.circle(windowSurface, (0,255,255), (self.x, self.y), self.radius)

class Wall(Sprite):

    def __init__(self,color):

        self.z = 6
        self.color = color
        self.width = random.uniform((xper(0.15) if len(walls) < 2 else xper(0.1) if len(walls) < 5 else xper(0.05)),(xper(0.175) if len(walls) < 2 else xper(0.125) if len(walls) < 5 else xper(0.075)))
        self.height = random.uniform((yper(0.275) if len(walls) < 2 else yper(0.175) if len(walls) < 5 else yper(0.1)),(yper(0.3) if len(walls) < 2 else yper(0.225) if len(walls) < 5 else yper(0.15)))

        reroll = True
        while reroll:
            self.x, self.y = random.uniform(0+xper(0.025),screenX),random.uniform(0+yper(0.042),screenY)
            reroll = False
            if self.x+self.width > screenX-xper(0.025) or self.y+self.height > screenY-yper(0.042): reroll = True
            for wall in walls:
                if rectCollision((wall.x, wall.y, wall.width, wall.height),(self.x, self.y, self.width, self.height)):
                    reroll = True
                    break
            for tank in tanks:
                if rectCollision((tank.x-tank.radius, tank.y-tank.radius, tank.radius*2, tank.radius*2),(self.x, self.y, self.width, self.height)):
                    reroll = True
                    break
            for box in lootBoxes:
                if rectCollision((box.x-box.radius, box.y-box.radius, box.radius*2, box.radius*2),(self.x, self.y, self.width, self.height)):
                    reroll = True
                    break

        walls.append(self)

    def process(self):

        for tank in tanks:
            if rectCollision((tank.x-tank.radius, tank.y-tank.radius, tank.radius*2, tank.radius*2),(self.x, self.y, self.width, self.height)):

                leftBorder = abs(tank.x+tank.radius*2-self.x)
                rightBorder = abs(tank.x-tank.radius*2-(self.x+self.width))
                topBorder = abs(tank.y+tank.radius*2-self.y)
                bottomBorder = abs(tank.y-tank.radius*2-(self.y+self.height))

                closestBorder = min(leftBorder,rightBorder,topBorder,bottomBorder)

                if closestBorder == leftBorder: tank.x = self.x-tank.radius
                if closestBorder == rightBorder: tank.x = self.x+self.width+tank.radius
                if closestBorder == topBorder: tank.y = self.y-tank.radius
                if closestBorder == bottomBorder: tank.y = self.y+self.height+tank.radius

        for shot in shots:
            if rectCollision((shot.x-shot.radius*0.75, shot.y-shot.radius*0.75, shot.radius*1.5, shot.radius*1.5),(self.x, self.y, self.width, self.height)):
                spritesToRemove.append(shot)

        for coin in coins:
            if not coin.grabbed:
                if rectCollision((coin.x-coin.radius, coin.y-coin.radius, coin.radius*2, coin.radius*2),(self.x, self.y, self.width, self.height)):

                    leftBorder = abs(coin.x+coin.radius*2-self.x)
                    rightBorder = abs(coin.x-coin.radius*2-(self.x+self.width))
                    topBorder = abs(coin.y+coin.radius*2-self.y)
                    bottomBorder = abs(coin.y-coin.radius*2-(self.y+self.height))

                    closestBorder = min(leftBorder,rightBorder,topBorder,bottomBorder)

                    if closestBorder == leftBorder: coin.x = self.x-coin.radius
                    if closestBorder == rightBorder: coin.x = self.x+self.width+coin.radius
                    if closestBorder == topBorder: coin.y = self.y-coin.radius
                    if closestBorder == bottomBorder: coin.y = self.y+self.height+coin.radius

        for box in lootBoxes:
            if rectCollision((box.x-box.radius, box.y-box.radius, box.radius*2, box.radius*2),(self.x, self.y, self.width, self.height)):

                leftBorder = abs(box.x+box.radius*2-self.x)
                rightBorder = abs(box.x-box.radius*2-(self.x+self.width))
                topBorder = abs(box.y+box.radius*2-self.y)
                bottomBorder = abs(box.y-box.radius*2-(self.y+self.height))

                closestBorder = min(leftBorder,rightBorder,topBorder,bottomBorder)

                if closestBorder == leftBorder: box.x = self.x-box.radius
                if closestBorder == rightBorder: box.x = self.x+self.width+box.radius
                if closestBorder == topBorder: box.y = self.y-box.radius
                if closestBorder == bottomBorder: box.y = self.y+self.height+box.radius

    def draw(self):

        for i in range(2):
            pygame.draw.rect(windowSurface, modifyColorPerc(self.color,0.8) if i % 2 == 0 else self.color, pygame.Rect(self.x + self.width/2*i/25, self.y + self.height/2*i/25, self.width - self.width*i/25, self.height - self.height*i/25))

class Explosion(Sprite):

    def __init__(self,x,y,radius):

        self.z = 2
        self.x = x
        self.y = y
        self.startRadius = radius
        self.radius = self.startRadius
        self.repeat = False

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            self.radius += sper(0.3) * deltaT
            if self.radius > self.startRadius*3 and self.startRadius > sper(0.01) and not self.repeat:
                addSprite(Explosion(self.x,self.y,self.radius/5))
                self.repeat = True
            if self.radius > self.startRadius*6:
                spritesToRemove.append(self)

    def draw(self):

        pygame.draw.circle(windowSurface,(255, random.randint(128,255), 0),(self.x,self.y),self.radius,int(self.radius/8))

class Coin(Sprite):

    def __init__(self,x,y,value):

        self.z = 5
        self.x = x
        self.y = y
        self.ang = random.uniform(0,math.pi*2)
        self.vel = random.uniform(sper(0.06),sper(0.08))
        self.value = value
        self.radius = self.value * sper(0.02) / 90
        self.lifeSpan = random.randint(15,25)
        self.blinkCD = 0
        self.grabbed = False
        self.accounted = False

        coins.append(self)

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            self.lifeSpan -= deltaT
            if self.lifeSpan <= 0: spritesToRemove.append(self)

            self.x += math.cos(self.ang)*self.vel * deltaT
            self.y += math.sin(self.ang)*self.vel * deltaT
            self.vel = max(self.vel - 50 * deltaT,0)

            if self.x > screenX-self.radius: self.x = screenX-self.radius
            elif self.x < 0 + self.radius: self.x = 0 + self.radius
            if self.y > screenY-self.radius: self.y = screenY-self.radius
            elif self.y < 0 + self.radius: self.y = 0 + self.radius

            if self.lifeSpan < 5: self.blinkCD += deltaT
            if self.blinkCD > 0.2: self.blinkCD = 0

    def draw(self):

        color = (255,255,0) if self.blinkCD < 0.1 else (64,64,0)
        pygame.draw.circle(windowSurface,color,(self.x,self.y),self.radius)
        pygame.draw.circle(windowSurface,modifyColorPerc(color,0.5),(self.x,self.y),self.radius*0.6,int(self.radius/4))
        pygame.draw.circle(windowSurface,modifyColorPerc(color,0.5),(self.x,self.y),self.radius,int(self.radius/4))

class LootBox(Sprite):

    def __init__(self):

        self.z = 3
        self.ang = random.uniform(0,math.pi*2)
        self.angVel = random.choice((random.uniform(-sper(0.005),-sper(0.002)),random.uniform(sper(0.002),sper(0.005))))
        self.startRadius = sper(0.0192)
        self.radius = self.startRadius
        self.lifeSpan = 30
        self.health = 10
        self.hitCD = 0
        self.destroyed = False

        chance = random.random()
        self.boxType = 'power' if chance <= 0.1 else 'firstAid' if chance > 0.1 and chance <= 0.3 else 'coin'

        reroll = True
        while reroll:
            self.x, self.y = random.randint(xper(0.1),screenX-xper(0.1)), random.randint(yper(0.1),screenY-yper(0.1))
            reroll = False
            for wall in walls:
                if rectCollision((self.x-self.radius*1.5, self.y-self.radius*1.5, self.radius*3, self.radius*3),(wall.x, wall.y, wall.width, wall.height)):
                    reroll = True
                    break
            for tank in tanks:
                if rectCollision((self.x-self.radius*1.5, self.y-self.radius*1.5, self.radius*3, self.radius*3),(tank.x-tank.radius, tank.y-tank.radius, tank.radius*2, tank.radius*2)):
                    reroll = True
                    break

        lootBoxes.append(self)

    def process(self):

        if not manager[0].pause and not manager[0].shop and not manager[0].quitOption:
            self.lifeSpan -= deltaT
            if self.lifeSpan <= 10:
                spritesToRemove.append(self)

            self.hitCD = max(self.hitCD - deltaT, 0)

            self.ang += self.angVel * deltaT

            for shot in shots:
                if shot.isPlayerShot:
                    if getDist((shot.x,shot.y),(self.x,self.y)) < self.radius:
                        self.health -= 1
                        self.hitCD = 0.05
                        player[0].score += 100
                        spritesToRemove.append(shot)

            if self.health <= 0 and not self.destroyed:
                if self.boxType == 'power':
                    if player[0].power:
                        player[0].powerModeAction()
                        player[0].powerModeActiveTime = 30
                    player[0].power = True
                elif self.boxType == 'firstAid':
                    player[0].health = min(player[0].health + 0.33, 1)
                else:
                    for i in range(random.randint(17,25)): addSprite(Coin(self.x,self.y,random.randint(20,40)))
                self.destroyed = True
                spritesToRemove.append(self)

            self.radius = self.lifeSpan * self.startRadius / 30 + (random.uniform(self.radius*0.25,self.radius*0.5) if self.hitCD > 0 else 0)

    def draw(self):

        color = randColor() if self.boxType == 'power' else (100,255,0) if self.boxType == 'firstAid' else (74,46,6)
        drawColor = (50,50,50) if self.lifeSpan < 10.25 else modifyColor(color,100) if self.hitCD > 0 else color
        symbol = 'P' if self.boxType == 'power' else '+' if self.boxType == 'firstAid' else '$'
        symbolColor = (50,50,50) if self.lifeSpan < 10.25 or self.hitCD > 0 else modifyColorPerc(color,3) if self.boxType == 'power' else (255,255,255) if self.boxType == 'firstAid' else (255,255,0)

        for i in range(10):
            pygame.draw.line(windowSurface, modifyColorPerc(drawColor,0.9),(self.x + math.cos(self.ang - math.pi/2) * self.radius*(1-i*0.2), self.y + math.sin(self.ang - math.pi/2) * self.radius*(1-i*0.2)), (self.x + math.cos(self.ang) * self.radius*(1-i*0.2), self.y + math.sin(self.ang) * self.radius*(1-i*0.2)), int(self.radius/3))
            pygame.draw.line(windowSurface, modifyColorPerc(drawColor,0.9),(self.x - math.cos(self.ang) * self.radius*(1-i*0.2), self.y - math.sin(self.ang) * self.radius*(1-i*0.2)), (self.x + math.cos(self.ang - math.pi/2) * self.radius*(1-i*0.2), self.y + math.sin(self.ang - math.pi/2) * self.radius*(1-i*0.2)), int(self.radius/3))
        pygame.draw.line(windowSurface, drawColor, (self.x + math.cos(self.ang) * self.radius, self.y + math.sin(self.ang) * self.radius), (self.x + math.cos(self.ang + math.pi/2) * self.radius, self.y + math.sin(self.ang + math.pi/2) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, drawColor, (self.x + math.cos(self.ang + math.pi/2) * self.radius, self.y + math.sin(self.ang + math.pi/2) * self.radius), (self.x - math.cos(self.ang) * self.radius, self.y - math.sin(self.ang) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, drawColor, (self.x - math.cos(self.ang) * self.radius, self.y - math.sin(self.ang) * self.radius), (self.x + math.cos(self.ang - math.pi/2) * self.radius, self.y + math.sin(self.ang - math.pi/2) * self.radius), int(self.radius/4))
        pygame.draw.line(windowSurface, drawColor, (self.x + math.cos(self.ang - math.pi/2) * self.radius, self.y + math.sin(self.ang - math.pi/2) * self.radius), (self.x + math.cos(self.ang) * self.radius, self.y + math.sin(self.ang) * self.radius), int(self.radius/4))
        createTextCenter(sFont,symbol,symbolColor,None,self.x,self.y)

class Button(Sprite):

    def __init__(self, i, x, y, width, height, rectColor, content, fontSize, assignment):

        self.z = 1
        self.id = i
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.color = rectColor
        self.mouseBefore = False
        self.mLeftPressed = False
        self.mRightPressed = False
        self.highlighted = False
        self.highlightColor = modifyColor(self.color, 20)
        self.pressedColor = modifyColor(self.color, 60)
        self.content = content
        self.size = fontSize
        self.assignment = assignment

        buttons.append(self)

    def process(self):

        if rectPointCollision((self.x, self.y, self.width, self.height), (mouseX, mouseY)):
            self.highlighted = True
        else:
            self.highlighted = False

        if mouseLeft and self.highlighted:
            if not self.mouseBefore:
                self.mLeftPressed = True
        elif mouseRight and self.highlighted:
            if not self.mouseBefore:
                self.mRightPressed = True
        else:
            if (self.mLeftPressed or self.mRightPressed) and self.highlighted:

                if self.assignment == 'startGame' and self.mLeftPressed:
                    manager[0].menu = False
                    manager[0].menuButtons = False
                    while buttons:
                        for button in buttons: spritesToRemove.append(button)
                        removeSprites()
                    player[0].shieldCharge = 0
                    player[0].shieldCD = 0
                    player[0].secondaryShotCD = 0
                    for shot in shots: spritesToRemove.append(shot)

                if self.assignment == 'chooseColor':
                    manager[0].colorSelected = (manager[0].colorSelected + (1 if self.mLeftPressed else -1)) % len(manager[0].playerColors)
                    self.color = modifyColorPerc(manager[0].playerColors[manager[0].colorSelected],2)
                    self.highlightColor = modifyColor(self.color, 20)
                    self.pressedColor = modifyColor(self.color, 60)

                if self.assignment == 'chooseDifficulty':
                    manager[0].hardMode = not manager[0].hardMode
                    self.content = 'Hardcore' if manager[0].hardMode else 'Normal'

                if self.assignment == 'exit' and self.mLeftPressed:
                    pygame.quit()
                    sys.exit()

                if self.assignment == 'buyDmg' and self.mLeftPressed:
                    if player[0].money >= manager[0].upgradesCost[0] and manager[0].upgradesLvls[0] <= 10:
                        player[0].money -= manager[0].upgradesCost[0]
                        player[0].regAttack += 0.2
                        manager[0].upgradesCost[0] += int(manager[0].upgradesCost[0]*0.15)
                        manager[0].upgradesLvls[0] += 1

                if self.assignment == 'buyDef' and self.mLeftPressed:
                    if player[0].money >= manager[0].upgradesCost[1] and manager[0].upgradesLvls[1] <= 10:
                        player[0].money -= manager[0].upgradesCost[1]
                        player[0].regDefense -= 0.08
                        manager[0].upgradesCost[1] += int(manager[0].upgradesCost[1]*0.15)
                        manager[0].upgradesLvls[1] += 1

                if self.assignment == 'buyAs' and self.mLeftPressed:
                    if player[0].money >= manager[0].upgradesCost[2] and manager[0].upgradesLvls[2] <= 10:
                        player[0].money -= manager[0].upgradesCost[2]
                        player[0].regPrimaryShotAS -= 0.04
                        manager[0].upgradesCost[2] += int(manager[0].upgradesCost[2]*0.15)
                        manager[0].upgradesLvls[2] += 1

                if self.assignment == 'buyAs2' and self.mLeftPressed:
                    if player[0].money >= manager[0].upgradesCost[3] and manager[0].upgradesLvls[3] <= 10:
                        player[0].money -= manager[0].upgradesCost[3]
                        player[0].regSecondaryShotAS -= 0.08
                        player[0].secondaryShotCD *= player[0].regSecondaryShotAS
                        player[0].secondaryShotAS = player[0].regSecondaryShotAS
                        manager[0].upgradesCost[3] += int(manager[0].upgradesCost[3]*0.15)
                        manager[0].upgradesLvls[3] += 1

                if self.assignment == 'buyShCap' and self.mLeftPressed:
                    if player[0].money >= manager[0].upgradesCost[4] and manager[0].upgradesLvls[4] <= 10:
                        player[0].money -= manager[0].upgradesCost[4]
                        player[0].shieldAugment += 1
                        manager[0].upgradesCost[4] += int(manager[0].upgradesCost[4]*0.15)
                        manager[0].upgradesLvls[4] += 1

                if self.assignment == 'buyShReg' and self.mLeftPressed:
                    if player[0].money >= manager[0].upgradesCost[5] and manager[0].upgradesLvls[5] <= 10:
                        player[0].money -= manager[0].upgradesCost[5]
                        player[0].shieldChargeSpeed += 0.2
                        manager[0].upgradesCost[5] += int(manager[0].upgradesCost[5]*0.15)
                        manager[0].upgradesLvls[5] += 1

                if self.assignment == 'buyHpReg' and self.mLeftPressed:
                    if player[0].money >= manager[0].upgradesCost[6] and manager[0].upgradesLvls[6] <= 10:
                        player[0].money -= manager[0].upgradesCost[6]
                        player[0].regHealthRegenSpeed -= 0.095
                        player[0].healthRegenCD *= player[0].regHealthRegenSpeed
                        player[0].healthRegenSpeed = player[0].regHealthRegenSpeed
                        manager[0].upgradesCost[6] += int(manager[0].upgradesCost[6]*0.15)
                        manager[0].upgradesLvls[6] += 1

                if self.assignment == 'buyMspeed' and self.mLeftPressed:
                    if player[0].money >= manager[0].upgradesCost[7] and manager[0].upgradesLvls[7] <= 10:
                        player[0].money -= manager[0].upgradesCost[7]
                        player[0].regMoveSpeed += 0.05
                        manager[0].upgradesCost[7] += int(manager[0].upgradesCost[7]*0.15)
                        manager[0].upgradesLvls[7] += 1

            self.mLeftPressed, self.mRightPressed = False, False

        self.mouseBefore = mouseLeft or mouseRight

    def draw(self):

        color = self.pressedColor if (self.mLeftPressed or self.mRightPressed) else self.highlightColor if self.highlighted else self.color
        pygame.draw.rect(windowSurface, color, pygame.Rect(self.x, self.y, self.width, self.height))
        createTextCenter(self.size,self.content,(255,255,255),None,(self.x+self.width/2),(self.y+self.height/2))

        if self.assignment == 'chooseDifficulty':
            self.color = (178, random.randint(90,178), 0) if manager[0].hardMode else (10,10,10)
            self.highlightColor = modifyColor(self.color, 20)
            self.pressedColor = modifyColor(self.color, 60)

        if 'Upgrade' in self.content:
            costColor = (64,64,0) if manager[0].upgradesLvls[self.id] > 10 else (255,255,0) if player[0].money >= manager[0].upgradesCost[self.id] else (200,0,0)
            lvlColor = randColorInRange(150,255,0,0,150,255) if manager[0].upgradesLvls[self.id] > 10 else (255,0,0) if manager[0].upgradesLvls[self.id] > 8 else (255,125,0) if manager[0].upgradesLvls[self.id] > 6 else (255,255,0) if manager[0].upgradesLvls[self.id] > 4 else (0,180,0) if manager[0].upgradesLvls[self.id] > 2 else (0,180,180)
            pygame.draw.rect(windowSurface, lvlColor, pygame.Rect(self.x, self.y, self.width, self.height),int(sper(0.002)))
            pygame.draw.circle(windowSurface, costColor,(self.x+xper(0.012),self.y+yper(0.02)),sper(0.008))
            pygame.draw.circle(windowSurface, modifyColorPerc(costColor,0.5),(self.x+xper(0.012),self.y+yper(0.02)),sper(0.008)*0.6,int(sper(0.0105)/4))
            pygame.draw.circle(windowSurface, modifyColorPerc(costColor,0.5),(self.x+xper(0.012),self.y+yper(0.02)),sper(0.008),int(sper(0.01)/4))
            createTextLeft(tFont,str(manager[0].upgradesCost[self.id]) if manager[0].upgradesLvls[self.id] <= 10 else 'MAXED OUT',costColor,None,self.x+xper(0.021),self.y+yper(0.0125))
            createTextLeft(tFont,'Lvl %s' %(manager[0].upgradesLvls[self.id] if manager[0].upgradesLvls[self.id] <= 10 else 'max'),lvlColor,None,self.x+xper(0.122),self.y+yper(0.07))

class Manager(Sprite):

    def __init__(self):

        self.z = 0
        self.menu = True
        self.shop = False
        self.pause = False
        self.quitOption = False
        self.gameover = False
        self.victory = False
        self.showFPS = False
        self.tabPressed = False
        self.pPressed = False
        self.escPressed = False
        self.fPressed = False
        self.f1Pressed = False
        self.f2Pressed = False
        self.handCursor = False
        self.menuButtons = False
        self.shopButtons = False
        self.hardMode = False
        self.endTextTimer = 0
        self.pauseBlinkCD = 0
        self.menuEffectCD = 0
        self.scoreEffectCD = 0
        self.colorSelected = 0
        self.playerColors = ((0,0,80),(80,0,0),(0,80,0),(90,90,0),(0,70,90),(70,0,90),(80,80,80),(100,50,0))
        self.upgradesText = ['Upgrade tank damage','Upgrade tank defense','Upgrade cannon firerate','Upgrade missile refresh','Upgrade shield capacity','Upgrade shield regen','Upgrade health regen','Upgrade move speed']
        self.upgradesAssig = ['buyDmg','buyDef','buyAs','buyAs2','buyShCap','buyShReg','buyHpReg','buyMspeed']
        self.upgradesCost = [1400,1200,1300,1250,1200,1300,1100,1100]
        self.upgradesLvls = [1,1,1,1,1,1,1,1]
        self.lootBoxCD = 30
        self.waveNumber = 0
        self.waveTime = 0
        self.waveList = (

            #__WALL_REROLL__#

            ('BasicRed',3,30),('BasicRed',3,30),('BasicRed',4,30),('BasicRed',4,30),('BasicRed',4,30),
            ('BasicRed',6,5),('BasicBlue',2,55),('BasicBlue',4,30),('BasicRed',6,30),('BasicBlue',5,30),
            ('Rhomb',1,5),('BasicRed',3,55),('BasicBlue',4,30),('BasicRed',5,30),('Purple',1,30),
            ('BasicRed',6,5),('SmallPink',4,55),('BasicBlue',4,5),('BasicRed',5,55),('Rhomb',2,30),
            ('SmallPink',8,5),('SmallPink',4,55),('BasicBlue',3,30),('Rhomb',1,5),('Purple',1,55),
            ('BasicRed',7,30),('BasicRed',7,5),('Mortar',1,55),('SmallPink',5,5),('BasicRed',7,55),
            ('BasicBlue',5,30),('BasicRed',5,30),('BasicBlue',5,5),('BasicRed',5,55),('Rhomb',3,30),
            ('Purple',2,30),('SmallPink',10,30),('Mortar',2,30),('Rhomb',2,5),('Rhomb',3,55),
            ('BasicRed',6,30),('BasicRed',6,30),('BasicBlue',8,30),('SmallPink',7,5),('SmallPink',7,55),
            ('BasicBlue',8,30),('BasicRed',6,5),('BasicBlue',4,55),('Purple',2,30),('BossGreen',1,3600),

                    #__50_WAVES_______________________

            ('BasicBlue',8,30),('Rhomb',4,30),('BasicBlue',8,30),('BasicRed',8,5),('Icy',2,55),
            ('Mortar',2,5),('Purple',1,55),('Icy',1,5),('Rhomb',3,30),('BasicBlue',10,30),
            ('Exploder',2,30),('Exploder',3,30),('Icy',2,5),('Exploder',2,5),('BasicRed',7,80),
            ('BasicRed',10,30),('BasicBlue',10,30),('Purple',3,30),('Mortar',3,30),('Exploder',3,30),
            ('Invis',2,30),('Invis',3,30),('Invis',2,5),('Invis',3,5),('Invis',4,80),
            ('Rhomb',4,30),('Invis',3,5),('Icy',2,5),('BasicBlue',10,80),('BossGreen',2,3600),
            ('SmallPink',8,5),('Rhomb',3,5),('SmallPink',4,80),('Rhomb',6,5),('SmallPink',10,55),
            ('SmallPink',10,30),('SmallPink',6,5),('BasicBlue',8,55),('BasicRed',8,5),('Purple',3,55),
            ('Rhomb',5,5),('SmallPink',7,55),('Rhomb',3,5),('Invis',3,5),('Icy',2,80),
            ('BasicRed',15,30),('Mortar',3,5),('BasicBlue',12,55),('Exploder',3,5),('BossGreen',2,3600),

                    #__100_WAVES______________________

            ('Commander',1,5),('BasicRed',6,1),('BasicBlue',7,54),('Invis',12,5),('Purple',3,55),
            ('Icy',6,10),('Exploder',4,50),('Rhomb',7,1),('Mortar',4,59),('Rhomb',15,60),
            ('Exploder',10,1),('Commander',1,59),('Breeder',1,1),('SmallPink',8,1),('Icy',4,58),
            ('Commander',1,1),('Mortar',3,1),('Rhomb',4,1),('Purple',2,1),('BossGreen',1,3600),
            ('Breeder',2,1),('Rhomb',6,1),('Icy',2,1),('Exploder',2,1),('Breeder',1,3600),
            ('Invis',14,1),('Commander',1,59),('Mortar',9,60),('Purple',6,60),('BossGreen',3,3600),
            ('Icy',1,1),('Exploder',4,1),('Invis',4,1),('Breeder',2,5),('Commander',1,3600),
            ('Rhomb',6,1),('BossGreen',1,1),('BasicBlue',6,1),('Breeder',1,1),('Commander',1,3600),
            ('Invis',4,4),('Mortar',4,4),('Icy',4,4),('Exploder',4,4),('Breeder',2,3600),
            ('Purple',6,5),('Rhomb',10,55),('Breeder',4,5),('BossGreen',4,5),('Commander',2,3600),

                    #__150_WAVES______________________

            ('FinalBoss',1,3600)
        )

        manager.append(self)

    def process(self):

        if not self.menu:

            if not self.pause and not self.shop and not self.quitOption and not self.victory and not self.gameover:
                self.waveTime = max(self.waveTime - deltaT, 0)
                self.lootBoxCD = max(self.lootBoxCD - deltaT, 0)

                if self.waveTime == 0 or not enemies:
                    self.callWave(self.waveList[self.waveNumber][0],self.waveList[self.waveNumber][1],self.waveList[self.waveNumber][2])

                if self.lootBoxCD == 0 and self.waveTime < 100:
                    addSprite(LootBox())
                    self.lootBoxCD = random.randint(50,70) if self.hardMode else random.randint(30,50)

            if self.victory:
                self.scoreEffectCD = max(self.scoreEffectCD - deltaT, 0)
                if player[0].money > 0 and self.scoreEffectCD == 0:
                    moneyTransfer = 10 if player[0].money > 1000 else 1
                    player[0].money -= moneyTransfer
                    player[0].score += moneyTransfer*20
                    self.scoreEffectCD = 0.01

            if not self.victory and not self.gameover and not self.quitOption:

                if not self.tabPressed and not self.pause:
                    if keys[pygame.K_TAB]:
                        self.shop = not self.shop
                        self.shopButtons = False
                        while buttons:
                            for button in buttons: spritesToRemove.append(button)
                            removeSprites()
                        self.tabPressed = True

                if not self.pPressed and not self.shop:
                    if keys[pygame.K_p]:
                        self.pause = not self.pause
                        self.pauseBlinkCD = 0
                        self.pPressed = True

            if self.shop:
                if not self.shopButtons:
                    for i in range(8):
                        addSprite(Button(i,xper(0.005),yper(0.12)+yper(0.11)*i,xper(0.165),yper(0.1),(10,10,10),self.upgradesText[i],sFont,self.upgradesAssig[i]))
                    self.shopButtons = True

        else:

            self.menuEffectCD += deltaT
            if self.menuEffectCD > 0.05:
                addSprite(Explosion(random.randint(0,screenX),random.randint(0,screenY),random.uniform(sper(0.0064),sper(0.0128))))
                self.menuEffectCD = 0

            if not self.menuButtons:
                addSprite(Button(None,xper(0.025),yper(0.25),xper(0.15),yper(0.07),(10,10,10),'Start',mFont,'startGame'))
                addSprite(Button(None,xper(0.025),yper(0.35),xper(0.15),yper(0.07),modifyColorPerc(self.playerColors[self.colorSelected],2),'Tank Color',mFont,'chooseColor'))
                addSprite(Button(None,xper(0.025),yper(0.45),xper(0.15),yper(0.07),(10,10,10),'Hardcore' if self.hardMode else 'Normal',mFont,'chooseDifficulty'))
                addSprite(Button(None,xper(0.025),yper(0.55),xper(0.15),yper(0.07),(10,10,10),'Exit',mFont,'exit'))
                self.menuButtons = True

        if not self.escPressed:
            if keys[pygame.K_ESCAPE] and not self.shop and not self.pause:
                if not self.menu:
                    if self.quitOption:
                        self.mainMenu()
                    elif self.victory or self.gameover:
                        self.mainMenu()
                    else:
                        self.quitOption = True
                        self.escPressed = True
                else:
                    pygame.quit()
                    sys.exit()

        if not self.fPressed:
            if keys[pygame.K_f]:
                self.showFPS = not self.showFPS
                self.fPressed = True

        if not self.f1Pressed:
            if keys[pygame.K_F1]:
                for tank in tanks: tank.showHitbox = not tank.showHitbox
                for shot in shots: shot.showHitbox = not shot.showHitbox
                self.f1Pressed = True

        if not self.f2Pressed:
            if keys[pygame.K_F2]:
                for tank in tanks:
                    if not tank.isPlayer: tank.showLines = not tank.showLines
                self.f2Pressed = True

        if self.quitOption and mouseLeft: self.quitOption = False

        if not player and not self.gameover: addSprite(Player())

        if not keys[pygame.K_TAB]: self.tabPressed = False
        if not keys[pygame.K_p]: self.pPressed = False
        if not keys[pygame.K_ESCAPE]: self.escPressed = False
        if not keys[pygame.K_f]: self.fPressed = False
        if not keys[pygame.K_F1]: self.f1Pressed = False
        if not keys[pygame.K_F2]: self.f2Pressed = False

    def draw(self):

        global background
        background = modifyColorPerc(self.wallColor,0.2) if walls else randColorGray(0,5)

        for button in buttons:
            if button.highlighted:
                self.handCursor = True
                break
            else:
                self.handCursor = False

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND) if self.handCursor else pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        pygame.mouse.set_visible(self.menu or self.shop)

        if not self.menu:
            if player:
                maxCharge = player[0].shieldCapacity + player[0].shieldAugment
                charge = (player[0].shieldCharge * 100 / maxCharge * 0.01) * (abs(player[0].shieldCD-10) / 10)
                healthBarColor = (255,255,255) if player[0].hitCD > 0 else (random.randint(175,225),0,0) if player[0].health < 0.25 else (min(abs(255*(player[0].health-0.5)-255),255),max(255*(player[0].health),0),0)
                shieldBarColor = (random.randint(100,150),0,0) if player[0].shieldOverheat > 0 else (52,204,255) if player[0].shieldCD == 0 else (26,102,127)

                if player[0].shieldOverheat > 0: createTextCenter(tFont,'OVERHEATING!',(random.randint(175,225),0,0),None,player[0].x,player[0].y+player[0].radius*3)

                pygame.draw.rect(windowSurface, modifyColorPerc(healthBarColor,0.3), pygame.Rect(xper(0.005), yper(0.01), xper(0.16), yper(0.025)))
                pygame.draw.rect(windowSurface, healthBarColor, pygame.Rect(xper(0.005), yper(0.01), xper(0.16)*player[0].health, yper(0.025)))
                pygame.draw.rect(windowSurface, modifyColorPerc(healthBarColor,1.7), pygame.Rect(xper(0.005), yper(0.01), xper(0.16), yper(0.025)),int(sper(0.002)))

                pygame.draw.rect(windowSurface, modifyColorPerc(shieldBarColor,0.3), pygame.Rect(xper(0.005), yper(0.042), xper(0.14), yper(0.0175)))
                pygame.draw.rect(windowSurface, shieldBarColor, pygame.Rect(xper(0.005), yper(0.042), xper(0.14)*charge, yper(0.0175)))
                for i in range(1,maxCharge):
                    pygame.draw.line(windowSurface,(0,0,0),(xper(0.145)/maxCharge*i,yper(0.044)),(xper(0.145)/maxCharge*i,yper(0.052)),int(sper(0.001)))
                pygame.draw.rect(windowSurface, modifyColorPerc(shieldBarColor,1.7), pygame.Rect(xper(0.005), yper(0.042), xper(0.14), yper(0.0175)),int(sper(0.002)))

                pygame.draw.circle(windowSurface,(255,255,0),(xper(0.012),yper(0.08)),sper(0.0105))
                pygame.draw.circle(windowSurface,(128,128,0),(xper(0.012),yper(0.08)),sper(0.0105)*0.6,int(sper(0.0105)/4))
                pygame.draw.circle(windowSurface,(128,128,0),(xper(0.012),yper(0.08)),sper(0.0105),int(sper(0.01)/4))
                createTextLeft(sFont,str(player[0].money),(255,255,0),None,xper(0.025),yper(0.069))
                if player[0].moneyToAdd > 0: createTextLeft(tFont,'+ %s'%(player[0].moneyToAdd),(128,128,0),None,xper(0.0075),yper(0.1))
                if not self.victory: createTextLeft(tFont,'Score: %s' %(player[0].score),(255,255,255),None,xper(0.08),yper(0.072))

                if player[0].power:
                    color = randColor()
                    pygame.draw.circle(windowSurface,color,(xper(0.155),yper(0.05)),sper(0.0075))
                    pygame.draw.circle(windowSurface,modifyColor(color,50),(xper(0.155),yper(0.05)),sper(0.0075),int(sper(0.005)/2))
                    pygame.draw.circle(windowSurface,modifyColor(color,150),(xper(0.155),yper(0.05)),sper(0.002))
                elif player[0].powerMode and player[0].powerModeActiveTime == 0:
                    pygame.draw.circle(windowSurface,(150,0,0),(xper(0.155),yper(0.05)),sper(0.006))
                    pygame.draw.circle(windowSurface,(255,0,0),(xper(0.155),yper(0.05)),sper(0.003))
                    createTextLeft(tFont,'NO CHARGE',(200,0,0),None,xper(0.1625),yper(0.0425))
                else:
                    pygame.draw.circle(windowSurface,(100,100,100),(xper(0.155),yper(0.05)),sper(0.004))
                    pygame.draw.circle(windowSurface,(255,255,255),(xper(0.155),yper(0.05)),sper(0.002))

                if not self.shop:
                    crosshairRecoil = max(player[0].primaryShotCD * 150 / player[0].primaryShotAS * 0.01,1)
                    crosshairColor = player[0].drawColor if player[0].powerModeActiveTime > 0 else (75,75,75) if player[0].secondaryShotCD > 0 else modifyColorPerc(player[0].color,3)
                    pygame.draw.circle(windowSurface,crosshairColor,(mouseX,mouseY),sper(0.0075)*crosshairRecoil,int(sper(0.01)/5))
                    pygame.draw.line(windowSurface,crosshairColor,(mouseX-sper(0.0095)*crosshairRecoil,mouseY-sper(0.0001)),(mouseX+sper(0.009)*crosshairRecoil,mouseY-sper(0.0001)),int(sper(0.01)/5))
                    pygame.draw.line(windowSurface,crosshairColor,(mouseX-sper(0.0001),mouseY-sper(0.0095)*crosshairRecoil),(mouseX-sper(0.0001),mouseY+sper(0.009)*crosshairRecoil),int(sper(0.01)/5))

            if self.pause:
                self.pauseBlinkCD += deltaT
                createTextCenter(bFont,'PAUSE' if self.pauseBlinkCD > 0.5 else '',(0,0,0),None,xper(0.504),yper(0.505))
                createTextCenter(bFont,'PAUSE' if self.pauseBlinkCD > 0.5 else '',(255,255,255),None,xper(0.5),yper(0.5))
                if self.hardMode:
                    text = 'H' if self.pauseBlinkCD < 0.071 else 'HA' if self.pauseBlinkCD < 0.142 else 'HAR' if self.pauseBlinkCD < 0.213 else 'HARD' if self.pauseBlinkCD < 0.284 else 'HARDC' if self.pauseBlinkCD < 0.355 else 'HARDCO' if self.pauseBlinkCD < 0.426 else 'HARDCOR' if self.pauseBlinkCD < 0.5 else 'HARDCORE'
                    createTextCenter(sFont,text,(0,0,0),None,xper(0.504),yper(0.575))
                    createTextCenter(sFont,text,(255,random.randint(128,255),0),None,xper(0.5),yper(0.57))
                if self.pauseBlinkCD > 1: self.pauseBlinkCD = 0

            elif self.quitOption:
                createTextCenter(mFont,'Quit to Menu?',(0,0,0),None,xper(0.504),yper(0.485))
                createTextCenter(sFont,'ESC to confirm, LeftClick to cancel',(0,0,0),None,xper(0.503),yper(0.554))
                createTextCenter(mFont,'Quit to Menu?',(255,255,255),None,xper(0.5),yper(0.48))
                createTextCenter(sFont,'ESC to confirm, LeftClick to cancel',(255,255,0),None,xper(0.5),yper(0.55))

            elif self.victory or self.gameover:
                self.endTextTimer += deltaT
                if self.endTextTimer > 4:
                    text = 'VICTORY!' if self.victory else 'GAME OVER'
                    createTextCenter(bFont,text,(0,0,0),None,xper(0.504),yper(0.455))
                    createTextCenter(mFont,'Score: %s' %(self.playerScore),(0,0,0),None,xper(0.504),yper(0.555))
                    createTextCenter(bFont,text,(255,255,255),None,xper(0.5),yper(0.45))
                    createTextCenter(mFont,'Score: %s' %(self.playerScore),(255,255,0),None,xper(0.5),yper(0.55))

            if keys[pygame.K_F3]:
                createTextLeft(sFont,'Sprites: %s' %(len(sprites)),(75,75,75),None,xper(0.885),yper(0.75))
                createTextLeft(sFont,'Enemies: %s' %(len(enemies)),(75,75,75),None,xper(0.885),yper(0.8))
                createTextLeft(sFont,'LootTimer: %s' %(round(self.lootBoxCD)),(75,75,75),None,xper(0.885),yper(0.85))
                createTextLeft(sFont,'WaveTimer: %s' %(round(self.waveTime)),(75,75,75),None,xper(0.885),yper(0.9))
                createTextLeft(sFont,'WaveNum: %s' %(self.waveNumber),(75,75,75),None,xper(0.885),yper(0.95))

        else:
            color = randColorGray(150,255)
            createTextLeft(bFont,'TankWARS',modifyColorPerc(color,0.25),None,random.uniform(xper(0.025),xper(0.03)),random.uniform(yper(0.055),yper(0.065)))
            createTextLeft(bFont,'TankWARS',color,None,random.uniform(xper(0.02),xper(0.025)),random.uniform(yper(0.05),yper(0.06)))

            pygame.draw.rect(windowSurface, (0,0,0), pygame.Rect(xper(0.01), yper(0.7), xper(0.5), yper(0.275)))
            pygame.draw.rect(windowSurface, (255,255,255), pygame.Rect(xper(0.01), yper(0.7), xper(0.5), yper(0.275)),int(sper(0.002)))
            createTextLeft(mFont,'Controls:',(255,255,255),None,xper(0.03),yper(0.735))
            createTextLeft(sFont,'WASD to move, MOUSE to aim, SPACEBAR to shield.',(255,255,255),None,xper(0.03),yper(0.82))
            createTextLeft(sFont,'LMB shoots cannon, RMB missiles, MIDDLE BUTTON for power mode.',(255,255,255),None,xper(0.03),yper(0.87))
            createTextLeft(sFont,'Spend money to get upgrades for your tank at the shop (TAB).',(255,255,255),None,xper(0.03),yper(0.92))

        if self.showFPS: createTextLeft(tFont,'FPS: %s' %(str(round(clock.get_fps()))),(255,255,255),None,xper(0.95),yper(0.01))

    def mainMenu(self):
        while len(sprites) > 1:
            for sprite in sprites:
                if sprite != self:
                    spritesToRemove.append(sprite)
            removeSprites()
        player.clear()
        self.menu = True
        self.quitOption = False
        self.gameover = False
        self.victory = False
        self.endTextTimer = 0
        self.upgradesCost = [1400,1200,1300,1250,1200,1300,1100,1100]
        self.upgradesLvls = [1,1,1,1,1,1,1,1]
        self.waveNumber = 0
        self.lootBoxCD = 30
        self.escPressed = True

    def callWave(self, name, amount, waveTime):

        if self.waveNumber % 5 == 0:
            while walls:
                for wall in walls: spritesToRemove.append(wall)
                removeSprites()
            self.wallColor = randColorInRange(50,255,50,255,50,255)
            for i in range(random.randint(5,7)): addSprite(Wall(self.wallColor))

        self.waveNumber = (self.waveNumber+1) % len(self.waveList)
        self.waveTime = waveTime

        n = amount if self.hardMode else max(int(amount*0.5),1)
        for i in range(n):
            if name == 'SmallPink': addSprite(SmallPink())
            elif name == 'BasicRed': addSprite(BasicRed())
            elif name == 'BasicBlue': addSprite(BasicBlue())
            elif name == 'Rhomb': addSprite(Rhomb())
            elif name == 'Purple': addSprite(Purple())
            elif name == 'Icy': addSprite(Icy())
            elif name == 'Mortar': addSprite(Mortar())
            elif name == 'Invis': addSprite(Invis())
            elif name == 'Exploder': addSprite(Exploder())
            elif name == 'Commander': addSprite(Commander())
            elif name == 'Breeder': addSprite(Breeder())
            elif name == 'BossGreen': addSprite(BossGreen())
            elif name == 'FinalBoss': addSprite(FinalBoss())

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

def randColorGray(low, high):
    n = random.randint(low,high)
    return (n,n,n)

def modifyColor(color, offset):
    return tuple(max(min(c+offset, 255), 0) for c in color)

def modifyColorPerc(color, offset):
    return tuple(int(max(min(c*offset, 255), 0)) for c in color)

def getAngle(point1, point2):
    return math.atan2(point2[1]-point1[1], point2[0]-point1[0])

def getAngle2(prevAng, point1, point2):
    angle = math.atan2(point2[1]-point1[1], point2[0]-point1[0])
    if angle - prevAng < -math.pi: angle += math.pi*2
    if angle - prevAng >  math.pi: angle -= math.pi*2
    return angle

def getDist(point1, point2):
    return math.sqrt(abs(point1[0]-point2[0])**2+abs(point1[1]-point2[1])**2)

def rectCollision(r1, r2):
    if r1[0] + r1[2] > r2[0] and r1[0] < r2[0] + r2[2]:
        if r1[1] + r1[3] > r2[1] and r1[1] < r2[1] + r2[3]:
            return True
    return False

def rectPointCollision(rect, point):
    return point[0] >= rect[0] and point[0] <= rect[0]+rect[2] and point[1] >= rect[1] and point[1] <= rect[1]+rect[3]

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
            if sprite in tanks:
                tanks.remove(sprite)
                addSprite(Explosion(sprite.x,sprite.y,sprite.radius))
            if sprite in enemies:
                enemies.remove(sprite)
            if sprite in walls:
                walls.remove(sprite)
            if sprite in shots:
                shots.remove(sprite)
                addSprite(Explosion(sprite.x,sprite.y,sprite.radius*2 if sprite.missile else sprite.radius/2))
            if sprite in coins:
                coins.remove(sprite)
            if sprite in lootBoxes:
                lootBoxes.remove(sprite)
                addSprite(Explosion(sprite.x,sprite.y,sprite.radius/2))
            if sprite in buttons:
                buttons.remove(sprite)
            sprites.remove(sprite)
            spritesToRemove.remove(sprite)

# INITIALIZATION .....................................................................

pygame.init()

screenX = 1280
screenY = 720
windowSurface = pygame.display.set_mode((screenX, screenY), depth=32, display=0)
pygame.display.set_caption('TankWARS')

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
tanks = []
enemies = []
walls = []
shots = []
coins = []
lootBoxes = []
buttons = []
manager = []
player = []
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