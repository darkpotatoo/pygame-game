print("[INIT] Logger")

import tkinter as tk
from datetime import datetime

sigma = False
logged = []
displayedEntries = []

def log(message, type="INFO"):
	#types are INFO, WARNING, ERROR
	#add _EXTENDED to type to multi-line
	if not "EXTENDED" in type:
		logged.append("[" + type + "] " + message[0])
	if "EXTENDED" in type:
		logged.append("[" + type + "] " + message[0] + " {")
		for i in message:
			if i != message[0]: logged.append("\t" + str(i))
		logged.append("\t}")
	if type == "INFO":
		pass
		#if sigma: print(f"\033[0m[LOGGED] [{type}] " + message[0])
	elif type == "DEBUG":
		pass
		#print(f"\033[38;5;240m[LOGGED] [{type}] " + message[0])
		
def saveLogs():
	global infotext, debugtext, logged
	with open("log.txt", "w") as file:
		for i in logged:
			file.write(str(i) + "\n")
		file.close()