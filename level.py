print("[INIT] Level")

import platform, os
import pygame
from logger import log
from entity import EntitySpawners



"""
Level Room Layout (multiplication grid):

[ ][1][2][3][4][5][6]
[1]
[2]
[3]
[4]
[5]
[6]
"""

def dirFile(path):
	if platform.system() == "Windows":
		path = path.replace("/", "\\")
	elif platform.system() == "Darwin":
		pass
	return (str(os.getcwd()) + path)

def renderBackgroundOverlay(screen, path):
	for x in range(0, screen.get_width()+520, 500):
		for y in range(0, screen.get_height()+520, 500):
			screen.blit(pygame.image.load(dirFile(path)).convert(), (x, y))

paths1_1 = [dirFile("assets/levels/1-1/" + str(i) + ".png") for i in range(1, 26)]

class RoomDoors():
	door = {}
	def __init__(self, level):
		with open(dirFile("/level/doors" + level + ".txt")) as file:
			for i in file:
				self.door[str(i.split(": ")[0]).replace("[", "").replace("]", "")] = int(i.split(": ")[1])
	# EXAMPLE for room 1: self.doors["room_1_right"] = 2

class RoomUncrossables():
	uncrossable = {}
	def __init__(self, level):
		a=0
		with open(dirFile("/level/uncrossables" + level + ".txt")) as file:
			for i in file:
				a+=1
				self.uncrossable[i.split(": ")[0] + "_" + str(a)] = [int(i.split(": ")[1].split(";")[0]), int(i.split(";")[1]), int(i.split(";")[2]), int(i.split(";")[3])]
	# EXAMPLE for room 1: self.uncrossable[1] = [0, 0, 0, 0] x;x2;y;y2

class Level():
	def __init__(self, layer, level, paths):
		self.layer = layer
		self.level = level
		self.paths = paths
		#has
		with open(dirFile("/level/has.txt")) as file:
			for i in file:
				if str(layer)+"_"+str(level) in i.split(":")[0]:
					_has = i
					log([_has + " is the _has for the opened level"], "DEBUG")
		self.has = _has.split(": ")[1].split(", ")
		for i in range(len(self.has)):
			self.has[i] = int(self.has[i])
		#beaecon
		with open(dirFile("/level/beacons.txt")) as file:
			for i in file:
				if str(layer)+"_"+str(level) in i.split(":")[0]:
					_beacon = i
					log([_beacon + " is the _beacon for the current level"], "DEBUG")
		self.beacon = _beacon.split(": ")[1].split(", ")
		self.spawner = EntitySpawners(str(layer) + "_" + str(level), _has)
		self.doors = RoomDoors(str(layer) + "_" + str(level))
		self.uncrossables = RoomUncrossables(str(layer) + "_" + str(level))
		log(["Loaded level " + str(layer) + "-" + str(level), paths, self.doors.door, self.uncrossables.uncrossable], "INFO_EXTENDED")

	def draw(self, room, screen):
		renderBackgroundOverlay(screen, "/asset/levels/" + str(self.layer) + "-" + str(self.level) + "/" + str(room) + ".png")