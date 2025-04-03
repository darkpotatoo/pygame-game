print("[INIT] Screen")

import os, platform
from logger import log

class Screen():
	def __init__(self, name, image, buttons):
		self.image = dirFile(image)
		self.buttons = getButtons(buttons)
		self.name = name
		log(["Loaded screen", image, buttons, name], "INFO_EXTENDED")

	def checkClickInBounds(self, pos, x):
		i=self.buttons[x]
		if pos[0] >= i[0] and pos[0] <= i[1] and pos[1] >= i[2] and pos[1] <= i[3]:
			log(["Mouse clicked in bounds of button " + str(i)], "DEBUG")
			return True
		return False

#x;x2;y;y2
def getButtons(buttons):
	_b = []
	with open(dirFile(buttons)) as file:
		for i in file:
			line=i.split(";")
			_b.append([int(line[0]), int(line[1]), int(line[2]), int(line[3])])
	return _b

def dirFile(path):
	if platform.system() == "Windows":
		path = path.replace("/", "\\")
	elif platform.system() == "Darwin":
		pass
	return (str(os.getcwd()) + path)