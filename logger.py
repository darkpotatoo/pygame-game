print("[INIT] Logger")

import tkinter as tk
from datetime import datetime

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
		updateInfoGui(message[0])
		print(f"\033[0m[LOGGED] [{type}] " + message[0])
	elif type == "DEBUG":
		print(f"\033[38;5;240m[LOGGED] [{type}] " + message[0])
		updateDebugGui(message[0])
		
def saveLogs():
	global infotext, debugtext, logged
	with open("log.txt", "w") as file:
		for i in logged:
			file.write(str(i) + "\n")
		file.close()
	infotext.insert("end-1c","Logger shut down, saved successfully")
	debugtext.insert("end-1c","Logger shut down, saved successfully")
	

infogui = tk.Tk()
infotext = tk.Text(infogui, width = 40, height = 6)
infotext.grid(row = 1, column = 0, columnspan = 2)
infotext.insert("end-1c","Log info will be outputted here")
debuggui = tk.Tk()
debugtext = tk.Text(debuggui, width = 40, height = 6)
debugtext.grid(row = 1, column = 0, columnspan = 2)
debugtext.insert("end-1c","Debug info will be outputted here")

info1, info2, info3, info4, info5, debug1, debug2, debug3, debug4, debug5 = "","","","","","","","","",""
def updateInfoGui(new):
	global info1, info2, info3, info4, info5
	info5 = info4
	info4 = info3
	info3 = info2
	info2 = info1
	info1 = datetime.now().strftime('%H:%M:%S') + " " + new
	infotext.delete(1.0, "end-1c")
	infotext.insert("end-1c", info5 + "\n" + info4 + "\n" + info3 + "\n" + info2 + "\n" + info1)
	infogui.update()
def updateDebugGui(new):
	global debug1, debug2, debug3, debug4, debug5
	debug5 = debug4
	debug4 = debug3
	debug3 = debug2
	debug2 = debug1
	debug1 = datetime.now().strftime('%H:%M:%S') + " " + new 
	debugtext.delete(1.0, "end-1c")
	debugtext.insert("end-1c", debug5 + "\n" + debug4 + "\n" + debug3 + "\n" + debug2 + "\n" + debug1)
	debuggui.update()