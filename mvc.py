# Written by Shreepa Parthaje

import tkinter as tk
from tkinter import *

import sys

from dropbox import DropboxOAuth2FlowNoRedirect
from dropbox import Dropbox

# Nice GUI (done)
# Upload / download from dropbox (normal files)
# Create zips of folders + unzip when arriving at locations
# settings to change directories
# account login system
# make a nice README.md and change README.txt into a string variable
# deploy and test on windows + macs
# test with friends

""""
GUI IDEAS / BUGS
add icon
have keyword with specific colors

DROPBOX STUFF
oauth stuff needs to be sorted out
"""

ROOT, CONSOLE, ENTRY = 0, 1, 2
FONT = ("inconsolata", 12, "normal")
APP_TOKEN = ''
APP_KEY = open("secret.txt", "r").read().split()[0]
APP_SECRET = open("secret.txt", "r").read().split()[1]

def login(gui):
	auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

	authorize_url = auth_flow.start()
	print(authorize_url)
	auth_code = input("Enter the authorization code here: ").strip()

	try:
	    oauth_result = auth_flow.finish(auth_code)
	except:
	    return "Error: {0}".format(1)

	dbx = Dropbox(oauth_result.access_token)
	return "Logged In"

def println(item, gui):
	console = gui[CONSOLE]
	console.config(state=NORMAL)

	if console.get(1.0, END) == "\n":
		console.insert(END, item)
	else:
		console.insert(END, "\n" + item)

	console.see(END)
	console.config(state=DISABLED)

def get_console(gui):
	entry = gui[ENTRY]
	log = entry.get()
	entry.delete(0, END)
	return log

def parse_command(command, gui):
	params = command.split(" ")
	fp = params[0] # first parameter
	if (fp == "/settings"):
		return "settings"
	elif (fp == "/backup" or fp == "backup"):
		return "backup"
	elif (fp == "/push" or fp == "push"):
		return "push"
	elif (fp == "/pull" or fp == "pull"):
		return "pull"
	elif (fp == "/login" or fp == "login"):
		return login(gui)
	elif (fp == "/quit" or fp == "quit"):
		sys.exit(0)
	elif (fp == "/help" or fp == "help"):
		return open("README.txt").read()
	elif (fp == "/clear" or fp == "clear"):
		gui[CONSOLE].config(state=NORMAL)
		gui[CONSOLE].delete(1.0, END)
		gui[CONSOLE].config(state=DISABLED)
		return ""
	else:
		return "'{0}' is not a valid command, type /help for help".format(command)

def get_command(event, gui):
	command = get_console(gui)
	log = parse_command(command, gui)
	println(log, gui)

def create_GUI():
	gui = []
	root = tk.Tk()
	root.minsize(1200, 300)
	root.resizable(0, 0)
	root.title("MinecraftVC")
	root.configure(background='black')

	console = Text(root, width=126, height=17, bd=0, highlightthickness=0, relief='ridge', bg='black', foreground='white', font=FONT)
	console.pack()
	console.insert(END, "Welcome to MinecraftVC, type in /help to learn the commands")
	console.config(state=DISABLED)

	entry = Entry(root, width=126, bd=0, highlightthickness=0, relief='ridge', bg='black', foreground='white', insertbackground='white', font=FONT)
	entry.focus()
	entry.pack()

	gui.append(root)
	gui.append(console)
	gui.append(entry)

	return gui

def main():
	gui_elements = create_GUI()
	gui_elements[ROOT].bind("<Return>", lambda event: get_command(event, gui_elements))
	gui_elements[ROOT].mainloop()

if __name__ == "__main__":
	main()