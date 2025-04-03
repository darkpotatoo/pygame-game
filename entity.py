print("[INIT] Entity")

import random
import time
import pygame
import platform
import util
import os
from random import randint
from logger import log
from math import ceil

moveableEntities = []
entities = []
hostileEntities = []

def getEntityVars():
	return [moveableEntities, entities, hostileEntities]

def dirFile(path):
	if platform.system() == "Windows":
		path = path.replace("/", "\\")
	elif platform.system() == "Darwin":
		pass
	return (str(os.getcwd()) + path)

class EntityAI():
	#1 = player
	#2 = basic following
	#3 = basic following + attacking
	#4 = basic following + attacking + dashing
	#5 = basic following + shooting projectiles
	#6 = projectile
	#7 = beacon
	def __init__(self, ai):
		self.ai = ai

#Entity(t[0], int(t[1]), EntityState(int(t[2]), int(t[3]), _e, int(t[5]), bool(t[6])))
# Sprite, AI, Health, Defense, Controllable, Speed, Hostile, Damage
class EntitySpawners():

	def __init__(self, level, has):
		_entity = 0
		self.entities = {}
		self.used = {}
		_has = has.split(": ")[1].split(", ")
		log([str(_has) + " are rooms with entity spawners"], "DEBUG")
		for o in _has:
			self.entities[int(o)] = []
			self.used[int(o)] = False
		for o in _has:
			_has[_has.index(o)] = _has[_has.index(o)].split("\n")[0]
		for o in _has:
			with open(dirFile("/level/spawners" + level + "/" + str(o) + ".txt")) as file:
				for i in file:
					self.x = int(i.split(",")[0])
					self.y = int(i.split(",")[1])
					break
			with open(dirFile("/level/spawners" + level + "/" + str(o) + ".txt")) as file:
				for i in file:
					if not f"{self.x},{self.y}" in i:
						t = i.split(";")
						if t[4] == "True": _e = True
						else: _e = False
						_entity = Entity(t[0], int(t[1]), EntityState(int(t[2]), int(t[3]), _e, int(t[5]), bool(t[6])))
						self.entities[int(o)].append(_entity)

	def spawns(self, room):
		self.used[room] = True
		for entity in self.entities[room]:
			entity.roomRenderingIn = room
			#util.wait(500)
			entity.rendering = True
			entity.pos.x = self.x
			entity.pos.y = self.y
			log(["Entity spawner at " + str(self.x) + " " + str(self.y) + " created entity" + str(entity)])


#---- entity class ----
class Entity():

	def __init__(self, sprite, ai, EntityState):
		global e, moveableEntities, hostileEntities, entities
		from main import screen
		self.sprite = pygame.image.load(dirFile(sprite)).convert()
		self.pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
		self.ai = EntityAI(ai)
		self.roomRenderingIn = 0
		self.rendering = False
		self.parried = False
		self.lastattack = time.time()
		self.invincticks = time.time()
		self.lastdash = time.time()
		self.damage = EntityState.damage
		self.health = EntityState.health
		self.defense = EntityState.defense
		self.speed = EntityState.speed
		log(["Loaded entity", sprite, ai, EntityState.controllable, EntityState.health, EntityState.speed], "INFO_EXTENDED")
		if EntityState.controllable == True:
			moveableEntities.append(self)
		entities.append(self)
		if EntityState.hostile == True:
			hostileEntities.append(self)

	def checkToDie(self):
		from main import updateLevelKills
		if self.health <= 0:
			log(["Entity " + str(self) + " died"], "DEBUG")
			self.rendering = False
			updateLevelKills()
			self.roomRenderingIn = 0
			self.pos.x = 700
			self.pos.y = 700
			self.ai.ai = -1

	def behaviorWithAI(self):
		from main import Player, tryUncrossablesOnMovable, dt, entityDash, entityAttack, temporaryRender, font, playerAttack
		xdif = abs(Player.pos.x - self.pos.x)
		ydif = abs(Player.pos.y - self.pos.y)
		if (self.ai.ai == 2 or self.ai.ai == 3 or self.ai.ai == 4) and (xdif <= 20 and ydif <= 20):
			self.pos.x += (randint(-1, 1))
			self.pos.y += (randint(-1, 1))
		if (self.ai.ai == 2 or self.ai.ai == 3 or self.ai.ai == 4) and (xdif > 15 or ydif > 15):
			if Player.pos.x > self.pos.x and Player.pos.y > self.pos.y:
				self.pos.x += self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
				self.pos.y += self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
				tryUncrossablesOnMovable(self, "d")
				tryUncrossablesOnMovable(self, "w")
			if Player.pos.x < self.pos.x and Player.pos.y > self.pos.y:
				self.pos.x -= self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
				self.pos.y += self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
				tryUncrossablesOnMovable(self, "a")
				tryUncrossablesOnMovable(self, "w")
			if Player.pos.x < self.pos.x and Player.pos.y < self.pos.y:
				self.pos.x -= self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
				self.pos.y -= self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
				tryUncrossablesOnMovable(self, "a")
				tryUncrossablesOnMovable(self, "s")
			if Player.pos.x > self.pos.x and Player.pos.y < self.pos.y:
				self.pos.x += self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
				self.pos.y -= self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
				tryUncrossablesOnMovable(self, "d")
				tryUncrossablesOnMovable(self, "s")
		if (self.ai.ai == 3 or self.ai.ai == 4) and xdif < 10 and ydif < 10:
			if (time.time() - self.lastattack) > 1:
				self.lastattack = time.time()
				entityAttack(self)
		if (self.ai.ai == 4) and (xdif > 200 or ydif > 200):
			entityDash(self, "e")
		if (self.ai.ai == 5):
			if (xdif > 200 or ydif > 200):
				if Player.pos.x > self.pos.x and Player.pos.y > self.pos.y:
					self.pos.x += self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
					self.pos.y += self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
					tryUncrossablesOnMovable(self, "d")
					tryUncrossablesOnMovable(self, "w")
				if Player.pos.x < self.pos.x and Player.pos.y > self.pos.y:
					self.pos.x -= self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
					self.pos.y += self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
					tryUncrossablesOnMovable(self, "a")
					tryUncrossablesOnMovable(self, "w")
				if Player.pos.x < self.pos.x and Player.pos.y < self.pos.y:
					self.pos.x -= self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
					self.pos.y -= self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
					tryUncrossablesOnMovable(self, "a")
					tryUncrossablesOnMovable(self, "s")
				if Player.pos.x > self.pos.x and Player.pos.y < self.pos.y:
					self.pos.x += self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
					self.pos.y -= self.speed * dt + randint(int(-50 / self.speed), ceil(50 / self.speed))
					tryUncrossablesOnMovable(self, "d")
					tryUncrossablesOnMovable(self, "s")
			if ((time.time() - self.lastattack) > abs((self.speed-600)/250)):
				self.projectile("/asset/sprite/fireball.png", self.damage, self.speed*1.5)
				self.lastattack = time.time()
			if (xdif < 200 or ydif < 200):
				if Player.pos.x > self.pos.x and Player.pos.y > self.pos.y:
					self.pos.x -= self.speed * dt / 3
					self.pos.y -= self.speed * dt / 3
					tryUncrossablesOnMovable(self, "a")
					tryUncrossablesOnMovable(self, "s")
				if Player.pos.x < self.pos.x and Player.pos.y > self.pos.y:
					self.pos.x += self.speed * dt / 3
					self.pos.y -= self.speed * dt / 3
					tryUncrossablesOnMovable(self, "d")
					tryUncrossablesOnMovable(self, "s")
				if Player.pos.x < self.pos.x and Player.pos.y < self.pos.y:
					self.pos.x += self.speed * dt / 3
					self.pos.y += self.speed * dt / 3
					tryUncrossablesOnMovable(self, "d")
					tryUncrossablesOnMovable(self, "w")
				if Player.pos.x > self.pos.x and Player.pos.y < self.pos.y:
					self.pos.x -= self.speed * dt / 3
					self.pos.y += self.speed * dt / 3
					tryUncrossablesOnMovable(self, "a")
					tryUncrossablesOnMovable(self, "w")
		if (self.ai.ai == 6):
			if self.parried == False:
				if Player.pos.x > self.pos.x and Player.pos.y > self.pos.y:
					self.pos.x += self.speed * dt
					self.pos.y += self.speed * dt
					tryUncrossablesOnMovable(self, "d")
					tryUncrossablesOnMovable(self, "w")
				if Player.pos.x < self.pos.x and Player.pos.y > self.pos.y:
					self.pos.x -= self.speed * dt
					self.pos.y += self.speed * dt
					tryUncrossablesOnMovable(self, "a")
					tryUncrossablesOnMovable(self, "w")
				if Player.pos.x < self.pos.x and Player.pos.y < self.pos.y:
					self.pos.x -= self.speed * dt
					self.pos.y -= self.speed * dt
					tryUncrossablesOnMovable(self, "a")
					tryUncrossablesOnMovable(self, "s")
				if Player.pos.x > self.pos.x and Player.pos.y < self.pos.y:
					self.pos.x += self.speed * dt
					self.pos.y -= self.speed * dt
					tryUncrossablesOnMovable(self, "d")
					tryUncrossablesOnMovable(self, "s")
				if xdif < 10 and ydif < 10:
					entityAttack(self)
					self.health = -1
					self.checkToDie()
			if self.parried == True:
				if self.pos.x > self.owner.pos.x and self.pos.y > self.owner.pos.y:
					self.pos.x -= self.speed*2 * dt
					self.pos.y -= self.speed*2 * dt
					tryUncrossablesOnMovable(self, "d")
					tryUncrossablesOnMovable(self, "w")
				if self.pos.x < self.owner.pos.x and self.pos.y > self.owner.pos.y:
					self.pos.x += self.speed*2 * dt
					self.pos.y -= self.speed*2 * dt
					tryUncrossablesOnMovable(self, "a")
					tryUncrossablesOnMovable(self, "w")
				if self.pos.x < self.owner.pos.x and self.pos.y < self.owner.pos.y:
					self.pos.x += self.speed*2 * dt
					self.pos.y += self.speed*2 * dt
					tryUncrossablesOnMovable(self, "a")
					tryUncrossablesOnMovable(self, "s")
				if self.pos.x > self.owner.pos.x and self.pos.y < self.owner.pos.y:
					self.pos.x -= self.speed*2 * dt
					self.pos.y += self.speed*2 * dt
					tryUncrossablesOnMovable(self, "d")
					tryUncrossablesOnMovable(self, "s")
				xdif = abs(self.owner.pos.x - self.pos.x)
				ydif = abs(self.owner.pos.y - self.pos.y)
				if xdif < 10 and ydif < 10:
					playerAttack(self.owner)
					self.health = -1
					self.checkToDie()
		if (self.ai.ai == 7):
			if time.time() - self.lastattack > 1.33:
				self.lastattack = time.time()
				if random.randint(1, 2) == 2:
					self.health += 2
					temporaryRender.append([font.render("+2", True, (0, 150, 0)), (self.pos.x, self.pos.y), 1, 10])
				self.projectile("/asset/sprite/beaconprojectile.png", self.damage, self.speed)


	def projectile(self, sprite, dmg, speed):
		global entities, hostileEntities
		from main import currentRoom
		log(["Projectile spawned from" + str(self)], "DEBUG")
		projectile = Entity(sprite, 6, EntityState(999, 0, False, speed, True, dmg))
		projectile.pos.x = self.pos.x
		projectile.pos.y = self.pos.y
		projectile.owner = self
		projectile.roomRenderingIn = currentRoom
		projectile.rendering = True
		entities.append(projectile)
		hostileEntities.append(projectile)

class EntityState():

	def __init__(self, health, defense, controllable = False, speed = 100, hostile=False, damage=10):
		self.health = health
		self.defense = defense
		self.controllable = controllable
		self.hostile = hostile
		self.speed = speed
		self.damage = damage
		log(["Entity state loaded", health, defense, controllable, hostile], "INFO_EXTENDED")