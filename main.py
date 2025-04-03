print("\n"*500)
print("[INIT] Main")

#TODO: Separate file for rendering functions
#TODO: Custom font?

import random
import time
import pygame
import os
import sys
import platform
import time
import traceback
import math

from logger import log, saveLogs
from screen import Screen
from level import Level
from entity import Entity, EntityState, getEntityVars

config_windowSize_x = 500
config_windowSize_y = 500
moveableEntities = []
entities = []
hostileEntities = []
completedLevels = []
entitiesAlive = False
kills = 0
bonus = 0
temporaryRender = []
stats = [0,0,0,0,"ERROR"]
pygame.font.init()
font = pygame.font.SysFont(None, 32) #Download this at home
font_small = pygame.font.SysFont(None, 24)
font_large = pygame.font.SysFont(None, 48)

#---- Config loader ----
def loadConfig():
	global config_windowSize_x, config_windowSize_y
	log(["Loading config..."]) 
	with open("config.txt", "r") as file:
		for i in file:
			log(["Read line from config: " + i.split("\n")[0]]) 
		file.close()
		log(["Fully loaded config"]) 
def saveConfig():
	log(["Saving config..."])
	with open("config.txt", "w") as file:
		file.close()

#file in current dir
def dirFile(path):
	if platform.system() == "Windows":
		path = path.replace("/", "\\")
	elif platform.system() == "Darwin":
		pass
	return (str(os.getcwd()) + path)

# ---- Rendering functions ----

#background renderer
def renderBackgroundOverlay(path):
	for x in range(0, screen.get_width()+520, 500):
		for y in range(0, screen.get_height()+520, 500):
			screen.blit(pygame.image.load(dirFile(path)).convert(), (x, y))

def updateLevelKills():
	global kills
	kills += 1

def renderUI():
	global Player, leveltime, kills, deaths, screen
	#health
	pygame.draw.rect(screen, (150, 0, 0), pygame.Rect(5, 465, 210, 30))
	pygame.draw.rect(screen, (200, 0, 0), pygame.Rect(10, 470, 200, 20))
	pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(10, 470, (Player.health*2), 20))
	screen.blit(font.render(str(Player.health) + "/100", True, (255, 255, 255)), (10, 470))
	#score
	_score = int(round(10000 - leveltime*25 + kills*50))
	screen.blit(font.render("SCORE: " + str(_score), True, (255, 0, 0)), (10, 10))
	#dash cooldown
	dcd = time.time() - Player.lastdash
	pygame.draw.rect(screen, (100, 100, 255), pygame.Rect(385, 465, 110, 30))
	if dcd <= 1.5:
		pygame.draw.rect(screen, (50, 50, 200), pygame.Rect(390, 470, dcd*66, 20))
		screen.blit(font.render("DASH", True, (255, 0, 0)), (410, 470))
	else:
		pygame.draw.rect(screen, (150, 150, 255), pygame.Rect(390, 470, 100, 20))
		screen.blit(font.render("DASH", True, (0, 255, 0)), (410, 470))

def renderPlayer(player):
	screen.blit(player.sprite, player.pos)
def renderEntity(entity):
	screen.blit(entity.sprite, entity.pos)

# Object, Position, ID, Frames
#IDS:
# 0 = Heal text
# 1 = Damage text
# 2 = DASH!
# 3 = +100
# 4 = Respawned
# 5 = score viewer
temporaryRenderTimer = {}
def renderTemporaries():
	for object in temporaryRender:
		screen.blit(object[0], object[1])
		try:
			temporaryRenderTimer[object[2]] +=1
		except:
			temporaryRenderTimer[object[2]] = 0
		if temporaryRenderTimer[object[2]] >= object[3]:
			del temporaryRenderTimer[object[2]]
			temporaryRender.remove(object)
#[render object, position, id, object]

#level sel screen
def levelSelectScreen():
	global mode, currentScreen, completedLevels
	time.sleep(0.1)
	currentScreen = Screen("lvlselect1", "/asset/screen/lvlselect1.png", "/screen/buttonslvlselect1.txt")

#-- Game --
def screenClickSuccessHandle(bound):
	global running, mode, currentScreen, currentLevel, currentRoom, levelCompleteScreen, stats
	log(["Clicked button " + str(bound)], "DEBUG")
	if currentScreen.name == "main":
		if bound == 0:
			levelSelectScreen()
		if bound == 1:
			running = False
		if bound == 2:
			currentScreen = Screen("scoreviewer1", "/assets/screen/scoreviewer1.png", "/screen/buttonsscoreviewer1.txt")
	elif currentScreen.name == "pause":
		if bound == 0:
			mode = "game"
		if bound == 1:
			currentScreen = Screen("main", "/asset/screen/main.png", "/screen/buttonsmain.txt")
	elif currentScreen.name == "lvlselect1":
		if bound == 0:
			currentRoom = 1
			currentLevel = Level(1, 1, 1)
			mode = "game"
		if bound == 1:
			currentRoom = 1
			currentLevel = Level(1, 2, 1)
			mode = "game"
		if bound == 2:
			currentRoom = 1
			currentLevel = Level(1, 3, 1)
			mode = "game"
		if bound == 3:
			currentRoom = 1
			currentLevel = Level(1, 4, 1)
			mode = "game"
		if bound == 4:
			currentRoom = 1
			currentLevel = Level(1, 5, 1)
			mode = "game"
		if bound == 5:
			currentRoom = 1
			currentLevel = Level(1, 6, 1)
			mode = "game"
		if bound == 6:
			currentScreen = Screen("main", "/asset/screen/main.png", "/screen/buttonsmain.txt")
			mode = "screen"
	elif currentScreen.name == "scoreviewer1":
		if bound < 6:
			lastscore=0
			for i in completedLevels:
				level = i[1]
				_score = i[2]
				if _score <= lastscore:
					continue
				if _score > 15000:
					rank = "S"
				elif _score >= 9750:
					rank = "A"
				elif _score >= 8000:
					rank = "B"
				elif _score >= 6000:
					rank = "C"
				elif _score >= 5000:
					rank = "D"
				else:
					rank = "F"
				_leveltime = i[4]
				lastscore=_score
				if level == bound+1:
					stats = [1, level, _score, _leveltime, rank]
					currentScreen = Screen("scoreviewer-view", "/asset/screen/viewer.png", "/screen/buttonscomplete.txt")
					return
		if bound == 6:
			currentScreen = Screen("main", "/asset/screen/main.png", "/screen/buttonsmain.txt")
			mode = "screen"
	elif currentScreen.name == "complete":
		if bound == 0:
			currentScreen = Screen("main", "/asset/screen/main.png", "/screen/buttonsmain.txt")
			mode = "screen"

def endLevel():
	global currentRoom, currentLevel, Player, leveltime, kills, deaths, bonus, levelCompleteScreen, currentScreen
	currentRoom = 1
	score = round(10000 - leveltime*25 + kills*50 + bonus)
	if score > 15000:
		rank = "S"
	elif score >= 9750:
		rank = "A"
	elif score >= 8000:
		rank = "B"
	elif score >= 6000:
		rank = "C"
	elif score >= 5000:
		rank = "D"
	else:
		rank = "F"
	Player.pos.x=250
	Player.pos.y=250
	completedLevels.append([currentLevel.layer, currentLevel.level, score, kills, leveltime]) #add time to complete, kills, deaths to this
	log(["Completed level", currentLevel.layer, currentLevel.level, score], "INFO_EXTENDED")
	writeSaveFile()
	levelCompleteScreen = [score, leveltime, rank]
	currentScreen = Screen("complete", "/asset/screen/complete.png", "/screen/buttonscomplete.txt")
	leveltime,deaths,kills,bonus = 0,0,0,0
	
def checkRoomChangable():
	global currentRoom, Player
	e = False
	for entity in entities:
		if entity.roomRenderingIn == currentRoom:
			e = True
			break
	return e

#----save file----
def writeSaveFile():
	# TODO: ake this only save best score
	with open("save.txt", "w") as file:
		for i in completedLevels:
			file.write(str(i) + "\n")
def loadSaveFile():
	with open("save.txt", "r") as file:
		for i in file:
			completedLevels.append(eval(i))

def changeRoomCheck():
	global currentLevel, currentRoom, currentScreen, mode, entitiesAlive, dt, Player
	for entity in entities:
		if entity.roomRenderingIn != currentRoom and entity.ai != 1:
			entity.rendering = False
	if Player.pos.x > 490:
		Player.pos.x =- Player.speed * dt
		return False
	if Player.pos.x < 0:
		Player.pos.x =+ Player.speed * dt
		return False
	if Player.pos.y > 490:
		Player.pos.y =- Player.speed * dt
		return False
	if Player.pos.y < 0:
		Player.pos.y =+ Player.speed * dt
		return False
	if entitiesAlive:
		return False
	if not checkRoomChangable():
		for i in enumerate(currentLevel.doors.door):
			if str(currentRoom) in i[1]:
				if currentLevel.doors.door[i[1]] == 0:
					mode = "screen"
					currentScreen = Screen("main", "/asset/screen/main.png", "/screen/buttonsmain.txt")
					endLevel()
					return True
			if str(currentRoom) + "_" in i[1]:
				if "left" in i[1]:
					if Player.pos.x > 0 and Player.pos.x < 20 and Player.pos.y < 280 and Player.pos.y > 220:
						currentRoom = currentLevel.doors.door[i[1]]
						log(["Player moved to room " + str(currentLevel.doors.door[i[1]])], "DEBUG")
						Player.pos.x = 475
						Player.pos.y = 250
						time.sleep(0.2)
						return True
				elif "upper" in i[1]:
					if Player.pos.x < 280 and Player.pos.x > 220 and Player.pos.y < 20 and Player.pos.y > 0:
						currentRoom = currentLevel.doors.door[i[1]]
						log(["Player moved to room " + str(currentLevel.doors.door[i[1]])], "DEBUG")
						Player.pos.x = 250
						Player.pos.y = 475
						time.sleep(0.2)
						return True
				if "lower" in i[1]:
					if Player.pos.x < 280 and Player.pos.x > 220 and Player.pos.y < 500 and Player.pos.y > 480:
						currentRoom = currentLevel.doors.door[i[1]]
						log(["Player moved to room " + str(currentLevel.doors.door[i[1]])], "DEBUG")
						Player.pos.x = 250
						Player.pos.y = 25
						time.sleep(0.2)
						return True
				elif "right" in i[1]:
					if Player.pos.x > 480 and Player.pos.x < 500 and Player.pos.y < 280 and Player.pos.y > 220:
						currentRoom = currentLevel.doors.door[i[1]]
						log(["Player moved to room " + str(currentLevel.doors.door[i[1]])], "DEBUG")
						Player.pos.x = 25
						Player.pos.y = 250
						time.sleep(0.2)
						return True
	

def tryUncrossablesOnMovable(entity, lastmove):
	global currentLevel, currentRoom
	if lastmove == "":
		return True
	for i in enumerate(currentLevel.uncrossables.uncrossable):
		c = currentLevel.uncrossables.uncrossable[i[1]]
		if str(currentRoom) in str(i[1]).split("_")[0]:
			if entity.pos.x+24 > c[0] and entity.pos.x < c[1] and entity.pos.y+24 > c[2] and entity.pos.y < c[3]:
				if lastmove == "s": entity.pos.y += entity.speed * dt
				if lastmove == "w": entity.pos.y -= entity.speed * dt
				if lastmove == "a": entity.pos.x += entity.speed * dt
				if lastmove == "d": entity.pos.x -= entity.speed * dt
				return False

#TODO: Transparent invinc tick overlay
def entityAttack(entity):
	if time.time() - Player.invincticks > 0.5:
		log([str(entity) + " attacked player"], "DEBUG")
		Player.health -= (entity.damage+random.randint(-4, 4))-Player.defense
		temporaryRender.append([font.render("-" + str(entity.damage), True, (255, 0, 255)), (Player.pos.x, Player.pos.y), 1, 10])
		Player.invincticks = time.time()

def playerAttack(entit = None):
	if entit != None:
		entit.invincticks = time.time()
		if Player.health <= 97: Player.health += 15
		log([str(entit) + " attacked by player, has hp: " + str(entit.health)], "DEBUG")
		entit.health -= Player.damage
		Player.lastattack = time.time()
		entit.checkToDie()
	if entit == None:
		if (time.time() - Player.lastattack) > 0.25:
			for entity in entities:
				if entity != Player:
					xdif = abs(Player.pos.x-entity.pos.x)
					ydif = abs(Player.pos.y-entity.pos.y)
					if xdif < 40 and ydif < 40 and time.time() - entity.invincticks > 0.5:
						if entity.ai.ai == 6:
							temporaryRender.append([font.render("+15", True, (0, 255, 0)), (Player.pos.x, Player.pos.y), 1, 15])
							temporaryRender.append([font.render("PARRY!", True, (255, 255, 255)), (Player.pos.x-20, Player.pos.y-25), 1, 10])
							entity.parried = True
						else:
							entity.invincticks = time.time()
							if Player.health <= 97: Player.health += 3
							log([str(entity) + " attacked by player, has hp: " + str(entity.health)], "DEBUG")
							entity.health -= Player.damage
							temporaryRender.append([font.render("+3", True, (0, 255, 0)), (entity.pos.x, entity.pos.y), 1, 15])
							Player.lastattack = time.time()
							entity.checkToDie()

hasUsedBeacon = {}
def checkBeacon():
	global currentLevel, currentRoom, hasUsedBeacon, entities, hostileEntities, bonus
	try: hasUsedBeacon[currentRoom]
	except: hasUsedBeacon[currentRoom] = False
	if not hasUsedBeacon[currentRoom]:
		for i in currentLevel.beacon:
			if int(i.split(";")[0]) == currentRoom:
				_beacon = Entity("/asset/sprite/beacon.png", 7, EntityState(100, 0, False, 100, True, 15))
				_beacon.pos.x = int(i.split(";")[1])
				_beacon.pos.y = int(i.split(";")[2])
				entities.append(_beacon)
				hostileEntities.append(_beacon)
				_beacon.roomRenderingIn = currentRoom
				_beacon.rendering = True
				hasUsedBeacon[currentRoom] = True

def checkDeath():
	global Player, currentLevel, currentRoom, mode, currentScreen, screen, entities
	if Player.health <= 0:
		log(["Player died"], "DEBUG")
		for entity in entities:
			if entity.rendering == True: entity.rendering = False
		mode = "screen"
		screen.blit(pygame.image.load(dirFile("/asset/screen/death.png")), (0, 0))
		pygame.display.flip()
		time.sleep(3)
		mode = "game"
		currentLevel = Level(currentLevel.layer, currentLevel.level, 1)
		currentRoom = 1
		Player = newPlayerEntity(100, 0, 200)
		Player.pos.x = 250
		Player.pos.y = 250

dashers = []
def checkDash():
	for x in dashers:
		if time.time() - x.lastdash > 0.2:
			dashers.pop(dashers.index(x))
			x.speed = x.speed/3
def entityDash(entity, lastmove):
	if time.time() - entity.lastdash > 1.5:
		entity.lastdash = time.time()
		log([str(entity) + " dashed"], "DEBUG")
		entity.invincticks += 0.5
		entity.speed = entity.speed * 3
		dashers.append(entity)
		temporaryRender.append([font.render("DASH!", True, (100, 100, 100)), (entity.pos.x, entity.pos.y), 2, 10])

def newPlayerEntity(health, defense, speed):
	return Entity("/asset/sprite/player.png", 1, EntityState(health, defense, True, speed))

def main():
	global screen, currentScreen, currentLevel, currentRoom
	global running, mode, dt
	global leveltime, levelCompleteScreen, stats
	global entities, moveableEntities, hostileEntities, Player

	loadSaveFile()
	log(["Loaded completed levels", completedLevels], "INFO_EXTENDED")
	loadConfig()
	log(["Loading game..."])
	pygame.init()

	pygame.joystick.init()
	if pygame.joystick.get_count() > 0:
		joystick = pygame.joystick.Joystick(0)
		joystick.init()
		print(f"{joystick.get_name()} is connected")
	
	mode = "screen"
	currentScreen = Screen("main", "/asset/screen/main.png", "/screen/buttonsmain.txt")
	currentLevel = None
	currentRoom = None
	leveltime = 0

	screen = pygame.display.set_mode((config_windowSize_x,config_windowSize_y)) #, pygame.RESIZABLE)
	pygame.display.set_icon(pygame.image.load(dirFile("/asset/icon.png")))
	pygame.display.set_caption('Window Caption')

	clock = pygame.time.Clock()
	running = True
	dt = 0
	log(["Loaded init", clock, running, screen], "INFO_EXTENDED")

	Player = newPlayerEntity(100, 0, 200)
	Player.rendering = True
	log(["Loaded player"])
	log(["Starting game loop"]) 

	lastmove = ""

	while running:

		_temp = getEntityVars()
		moveableEntities = _temp[0]
		entities = _temp[1]
		hostileEntities = _temp[2]

		#system event handling
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if mode=="screen":
				if event.type == pygame.MOUSEBUTTONDOWN:
					log(["Mouse clicked at " + str(event.pos)], "DEBUG")
					# Main screen
					if currentScreen.name == "main":
						#start button
						if (currentScreen.checkClickInBounds(event.pos, 0)): screenClickSuccessHandle(0)
						#quit button
						if (currentScreen.checkClickInBounds(event.pos, 1)): screenClickSuccessHandle(1)
						#score viewer
						if (currentScreen.checkClickInBounds(event.pos, 2)): screenClickSuccessHandle(2)
					elif currentScreen.name == "pause":
						#continue button
						if (currentScreen.checkClickInBounds(event.pos, 0)): screenClickSuccessHandle(0)
						#exit to main menu button
						if (currentScreen.checkClickInBounds(event.pos, 1)): screenClickSuccessHandle(1)
					elif currentScreen.name == "lvlselect1":
						Player = newPlayerEntity(100, 0, 200)
						#1-1
						if (currentScreen.checkClickInBounds(event.pos, 0)): screenClickSuccessHandle(0)
						#1-2
						if (currentScreen.checkClickInBounds(event.pos, 1)): screenClickSuccessHandle(1)
						#1-3
						if (currentScreen.checkClickInBounds(event.pos, 2)): screenClickSuccessHandle(2)
						#1-4
						if (currentScreen.checkClickInBounds(event.pos, 3)): screenClickSuccessHandle(3)
						#1-5
						if (currentScreen.checkClickInBounds(event.pos, 4)): screenClickSuccessHandle(4)
						#1-6
						if (currentScreen.checkClickInBounds(event.pos, 5)): screenClickSuccessHandle(5)
						#back
						if (currentScreen.checkClickInBounds(event.pos, 6)): screenClickSuccessHandle(6)
					elif currentScreen.name == "scoreviewer1":
						#1-1
						if (currentScreen.checkClickInBounds(event.pos, 0)): screenClickSuccessHandle(0)
						#1-2
						if (currentScreen.checkClickInBounds(event.pos, 1)): screenClickSuccessHandle(1)
						#1-3
						if (currentScreen.checkClickInBounds(event.pos, 2)): screenClickSuccessHandle(2)
						#1-4
						if (currentScreen.checkClickInBounds(event.pos, 3)): screenClickSuccessHandle(3)
						#1-5
						if (currentScreen.checkClickInBounds(event.pos, 4)): screenClickSuccessHandle(4)
						#1-6
						if (currentScreen.checkClickInBounds(event.pos, 5)): screenClickSuccessHandle(5)
						#back
						if (currentScreen.checkClickInBounds(event.pos, 6)): screenClickSuccessHandle(6)
					elif currentScreen.name == "complete":
						#continue button
						if (currentScreen.checkClickInBounds(event.pos, 0)): screenClickSuccessHandle(0)
		#----------------- RENDERING -------------------
		#screen rendering
		screen.fill("black")

		#screen overlay and custom additions
		if mode=="screen":
			pygame.mouse.set_visible(True)
			if currentScreen.name == "main":
				renderBackgroundOverlay("/asset/screen/main.png")
			elif currentScreen.name == "pause":
				renderBackgroundOverlay("/asset/screen/pause.png")
			elif currentScreen.name == "lvlselect1":
				renderBackgroundOverlay("/asset/screen/lvlselect1.png")
			elif currentScreen.name == "scoreviewer1":
				renderBackgroundOverlay("/asset/screen/scoreviewer1.png")
			elif currentScreen.name == "complete":
				renderBackgroundOverlay("/asset/screen/complete.png")
				stats = levelCompleteScreen
				layer = currentLevel.layer
				level = currentLevel.level
				screen.blit(font_large.render("COMPLETED " + str(layer) + "-" + str(level), True, (0, 0, 0)), (150, 150))
				screen.blit(font.render("RANK: " + stats[2], True, (0, 0, 0)), (200, 200))
				screen.blit(font.render("SCORE: " + str(math.ceil(stats[0])), True, (0, 0, 0)), (180, 230))
				screen.blit(font.render("TIME: " + str(round(stats[1], 2)) + " seconds", True, (0, 0, 0)), (150, 260))
			elif currentScreen.name == "scoreviewer-view":
				renderBackgroundOverlay("/asset/screen/complete.png")
				screen.blit(font_large.render("SCORE FOR " + str(stats[0]) + "-" + str(stats[1]), True, (0, 0, 0)), (120, 150))
				screen.blit(font.render("RANK: " + stats[4], True, (0, 0, 0)), (200, 200))
				screen.blit(font.render("SCORE: " + str(math.ceil(stats[2])), True, (0, 0, 0)), (180, 230))
				screen.blit(font.render("TIME: " + str(round(stats[3], 2)) + " seconds", True, (0, 0, 0)), (150, 260))

		
		#game render
		if mode=="game":
			leveltime += 1 * dt
			pygame.mouse.set_visible(False)
			currentLevel.draw(currentRoom, screen)

			renderUI()
			renderTemporaries()

			checkDash()
			checkDeath()
			checkBeacon()

			#movement handling
			keys = pygame.key.get_pressed()
			for entity in entities:
				if entity.rendering == True and entity.roomRenderingIn == currentRoom:
					renderEntity(entity)
					entity.behaviorWithAI()
				elif entity.roomRenderingIn == currentRoom and entity.rendering == False:
					entity.rendering = True
			renderPlayer(Player)
			for movable in moveableEntities:
				if keys[pygame.K_c] or joystick.get_button(1):
					entityDash(movable, lastmove)
				if keys[pygame.K_z] or joystick.get_button(0):
					playerAttack()
				if keys[pygame.K_UP] or joystick.get_axis(1) < -0.3:
					movable.pos.y -= movable.speed * dt
					lastmove = "w"
				if keys[pygame.K_DOWN] or joystick.get_axis(1) > 0.3:
					movable.pos.y += movable.speed * dt
					lastmove = "s"
				if keys[pygame.K_LEFT] or joystick.get_axis(0) < -0.3:
					movable.pos.x -= movable.speed * dt
					lastmove = "a"
				if keys[pygame.K_RIGHT] or joystick.get_axis(0) > 0.3:
					movable.pos.x += movable.speed * dt
					lastmove = "d"
				tryUncrossablesOnMovable(movable, lastmove)
			changeRoomCheck()
			if currentRoom in currentLevel.has:
				if currentLevel.spawner.used[currentRoom] == False:
					thereisabeacon = False
					for entit in entities:
						if entit.ai.ai == 7 or entit.ai.ai == "7":
							thereisabeacon = True
					if not thereisabeacon:
						currentLevel.spawner.spawns(currentRoom)
					print(thereisabeacon)
		if pygame.key.get_pressed()[pygame.K_ESCAPE]:
			if mode=="screen":
				running = False
			elif mode=="game":
				mode = "screen"
				time.sleep(0.2)
				currentScreen = Screen("pause", "/asset/screen/pause.png", "/screen/buttonspause.txt")

		pygame.display.flip()
		dt = clock.tick(60) / 1000

cmsg = ["Cry about it.",
		"This game is just full of issues!",
		"Hey, at least it worked for a little bit.",
		"Not my fault!!! Wait, it is.",
		"Hmm. This shouldn't have happened.",
		"You'll figure it out, right?"
		]

def game():
	global screen, running
	try:
		log(["Program starting..."])
		main()
		log(["Program terminated"])
		running = False
		time.sleep(0.1)
		saveConfig()
		saveLogs()
		pygame.quit()
	except:
		try:
			pygame.display.set_icon(pygame.image.load(dirFile("/asset/icon.png")))
			pygame.display.set_caption('Crashed!')
			pygame.display.flip()
			screen.blit(pygame.image.load(dirFile("/asset/screen/crash.png")), (0, 0))
			pygame.display.flip()
			time.sleep(1)
		except: pass

		print("\n\"" + random.choice(cmsg) + "\"", "\n---=== Game crashed ===---")
		print("\n\033[33mThe most recent error trace is as follows:")
		print("\033[31m" + traceback.format_exc())
		print("\033[32mThis may not be accurate. If you really want information, change debug mode to true.\033[37m")
		exit()

game()