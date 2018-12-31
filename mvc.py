# Written by Shreepa Parthaje

import sys

import webbrowser

import pickle

from os import path, listdir, remove

from shutil import make_archive, rmtree

import zipfile

import datetime

import tkinter as tk
from tkinter import *
from tkinter import simpledialog
from tkinter import filedialog

from dropbox import DropboxOAuth2FlowNoRedirect
from dropbox import Dropbox
from dropbox import files

# ------------- CONSTANTS -------------
ROOT, CONSOLE, ENTRY = 0, 1, 2
APP_KEY = open("secret.txt", "r").read().split()[0]
APP_SECRET = open("secret.txt", "r").read().split()[1]
CHUNK_SIZE = 4 * 1024 * 1024

# ------------- GLOBALS -------------
settings = {}


def local_backup(branch_name, gui):
    global settings  # Read

    backup_dir = settings["BACKUP_DIR"]
    saves_path = settings["SAVES_DIR"]

    now = datetime.datetime.now()
    month = now.month
    day = now.day
    year = now.year
    hour = now.hour
    minute = now.minute

    backup_name = str(month) + " " + str(day) + " " + str(year) + " | " + str(hour) + ":" + str(minute) + " |"

    base = path.join(backup_dir, branch_name)

    make_archive(path.join(base, "{0} saves".format(backup_name)), 'zip', saves_path)


def pull_from_dropbox(branch_name, symbol, gui):
    global settings  # Read

    confirm = simpledialog.askstring("Confirm",
                                     "Type in 'YES' if you wish to proceed. This will override existing worlds"
                                     " if a conflict is found")

    if not confirm == "YES":
        return "Pull cancelled"

    saves_path = settings["SAVES_DIR"]
    temp_dir = settings["TEMP_DIR"]
    source = "/" + branch_name + "/"

    if settings["OAUTH"] == 'null':
        return "Please type in /login to use this feature"

    println("Starting download... ", gui)
    println("Do not close the app until 'done downloading' message is shown on the console", gui)

    # clear temp_dir
    for path_temp in listdir(temp_dir):
        if path.isdir(path.join(temp_dir, path_temp)):
            rmtree(path.join(temp_dir, path_temp))
        else:
            remove(path.join(temp_dir, path_temp))

    # download zip files
    dbx = Dropbox(settings["OAUTH"].access_token)
    for entry in dbx.files_list_folder(source).entries:
        file = source + entry.name
        with open(path.join(temp_dir, entry.name), "wb") as f:
            metadata, res = dbx.files_download(path=file)
            f.write(res.content)
            f.close()

    for path_temp in listdir(temp_dir):
        file = path.join(temp_dir, path_temp)
        name, extension = path.splitext(file)
        file_name, ext = path.splitext(path_temp)

        if file_name[0] == symbol and extension == ".zip":
            with zipfile.ZipFile(file, 'r') as zip_ref:
                z = path.join(saves_path, file_name)
                zip_ref.extractall(z)

        remove(file)

    return "done downloading"


def push_to_dropbox(branch_name, symbol, gui):
    global settings  # Read

    saves_path = settings["SAVES_DIR"]
    temp_dir = settings["TEMP_DIR"]

    if settings["OAUTH"] == 'null':
        return "Please type in /login to use this feature"

    # clear temp_dir
    for path_temp in listdir(temp_dir):
        remove(path.join(temp_dir, path_temp))

    # archive worlds starting with 'symbol' to temp_dir
    for path_save in listdir(saves_path):
        file_path = path.join(saves_path, path_save)
        if path.isdir(file_path) and path_save[0] == symbol:
            make_archive(path.join(temp_dir, path_save), 'zip', file_path)

    dbx = Dropbox(settings["OAUTH"].access_token)

    # clear branch_directory in dropbox
    try:
        confirm = simpledialog.askstring("Confirm",
                                         "Type in 'YES' if you wish to proceed. This will delete the current '{0}'"
                                         " branch if it already exists in dropbox".format(branch_name))
        if not confirm == "YES":
            return "Action Not "
        dbx.files_delete("/" + branch_name)
    except Exception:
        pass

    println("Starting upload... ", gui)
    println("Do not close the app until 'done uploading' message is shown on the console", gui)

    # upload every zip file to dropbox in temp_dir
    for path_temp in listdir(temp_dir):
        zip_file = path.join(temp_dir, path_temp)
        destination = "/" + branch_name + "/" + path_temp

        with open(zip_file, "rb") as f:
            file_size = path.getsize(zip_file)
            if file_size < CHUNK_SIZE:
                dbx.files_upload(f.read(), destination)
            else:
                # upload_session_start_result
                upload_ssr = dbx.files_upload_session_start(f.read(CHUNK_SIZE))

                cursor = files.UploadSessionCursor(session_id=upload_ssr.session_id, offset=f.tell())
                commit = files.CommitInfo(path=destination)

                while f.tell() < file_size:
                    percent = str(f.tell() / file_size * 100) + "%"
                    print(percent)

                    if (file_size - f.tell()) <= CHUNK_SIZE:
                        dbx.files_upload_session_finish(f.read(CHUNK_SIZE), cursor, commit)
                    else:
                        dbx.files_upload_session_append(f.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                        cursor.offset = f.tell()

    # clear temp_dir
    for path_temp in listdir(temp_dir):
        remove(path.join(temp_dir, path_temp))

    return "done uploading"


def edit_settings():
    global settings  # Read and Write

    # FONT
    family = simpledialog.askstring("Font Family (currently: " + str(settings["FONT"][0]) + ")", "Type in pass to not "
                                                                                                 "change this value")
    if family == "pass":
        family = settings["FONT"][0]

    size = simpledialog.askstring("Font Size (currently: " + str(settings["FONT"][1]) + ")", "Type in pass to not "
                                                                                             "change this value")
    try:
        size = int(size)
    except ValueError:
        size = settings["FONT"][1]

    settings["FONT"] = (family, size, "normal")

    # BG_COLOR and TEXT_COLOR
    for key in ("BG_COLOR", "TEXT_COLOR", "SYMBOL"):
        color = simpledialog.askstring("{0} (currently: ".format(key) + str(settings[key]) + ")",
                                       "Type in pass to not "
                                       "change this value")
        if color == "pass":
            color = settings[key]

        settings[key] = color

    # BACKUP_DIR and SAVES_DIR

    for key in ("BACKUP_DIR", "SAVES_DIR", "TEMP_DIR"):
        backup_dir = str(filedialog.askdirectory(
            title="Choose {0}, Click cancel to keep previous {0} (".format(key) + settings[key] + ")"))
        if not (backup_dir == "" or backup_dir == "()"):
            settings[key] = backup_dir

    save(settings)


def view_settings(gui):
    global settings  # Read

    for key in settings:
        if key == "OAUTH":
            pass
        elif key == "FONT":
            s = key + ": " + str(settings[key][0]) + ", " + str(settings[key][1])
            println(s, gui)
        else:
            s = key + ": " + str(settings[key])
            println(s, gui)


def login():
    global settings  # Writes

    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

    authorize_url = auth_flow.start()
    webbrowser.open(authorize_url)
    auth_code = simpledialog.askstring("Log Into MinecraftVC",
                                       "Please log into dropbox in the link opened, authorize this app, and paste the "
                                       "code into the text field to log into MinecraftVC.").strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
    except:
        return "Error logging in, are you sure you typed in the code correctly?"

    settings["OAUTH"] = oauth_result
    return "Logged In"


def parse_command(command, gui):
    global settings  # Read

    params = command.split(" ")
    fp = params[0]  # first parameter
    if (fp == "/settings" or fp == "settings") and len(params) == 2:
        if params[1] == "view":
            view_settings(gui)
            return ""
        elif params[1] == "edit":
            edit_settings()
            return "To see any visual changes, please restart the app"

    elif fp == "/backup" or fp == "backup":
        if len(params) == 2:
            if params[1] == "view":
                print("JIEFIJFIJEIJ")
            local_backup(params[1], gui)
        else:
            local_backup("main", gui)
        return "backup"

    elif fp == "/push" or fp == "push":
        if len(params) == 1:
            return push_to_dropbox("main", settings["SYMBOL"], gui)
        if len(params) == 2:
            return push_to_dropbox(params[1], settings["SYMBOL"], gui)
        if len(params) == 3:
            return push_to_dropbox(params[1], params[2], gui)

    elif fp == "/pull" or fp == "pull":
        if len(params) == 1:
            return pull_from_dropbox("main", settings["SYMBOL"], gui)
        if len(params) == 2:
            return pull_from_dropbox(params[1], settings["SYMBOL"], gui)
        if len(params) == 3:
            return pull_from_dropbox(params[1], params[2], gui)

    elif fp == "/login" or fp == "login":
        if not settings["OAUTH"] == 'null':
            return "Already Logged In"
        return login()

    elif fp == "/logout" or fp == "logout":
        settings["OAUTH"] = "null"
        return "You have been logged out, use /login to log back in"

    elif fp == "/quit" or fp == "quit":
        save(settings)
        sys.exit(0)

    elif fp == "/help" or fp == "help":
        return open("README.txt").read()
    elif fp == "/clear" or fp == "clear":
        gui[CONSOLE].config(state=NORMAL)
        gui[CONSOLE].delete(1.0, END)
        gui[CONSOLE].config(state=DISABLED)
        return ""

    else:
        return "'{0}' is not a valid command, type /help for help".format(command)


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


def get_command(gui):
    command = get_console(gui)
    log = parse_command(command, gui)
    println(log, gui)


def create_GUI():
    global settings  # Read

    bg_color = settings["BG_COLOR"]
    txt_color = settings["TEXT_COLOR"]
    font = settings["FONT"]

    gui = []
    root = tk.Tk()
    root.minsize(1200, 300)
    root.resizable(0, 0)
    root.title("MinecraftVC")
    root.configure(background='black')

    console = Text(root, width=126, height=17, bd=0, highlightthickness=0, relief='ridge', bg=bg_color,
                   foreground=txt_color, font=font)
    console.pack()
    console.insert(END, "Welcome to MinecraftVC")
    console.config(state=DISABLED)

    entry = Entry(root, width=126, bd=0, highlightthickness=0, relief='ridge', bg=bg_color, foreground=txt_color,
                  insertbackground=txt_color, font=font)
    entry.focus()
    entry.pack()

    gui.append(root)
    gui.append(console)
    gui.append(entry)

    if settings["BACKUP_DIR"] == "null":
        println("Please type in /settings edit to setup MinecraftVC", gui)
        println("For help setting up MinecraftVC type in /help setup", gui)
        println("For general help type in /help", gui)

    return gui


def save(s):
    f = open("mvc.settings", "wb")
    try:
        pickle.dump(s, f)
        f.close()
    except TypeError:
        print("Saving settings has failed")
        f.close()


def reload():
    try:
        f = open("mvc.settings", "rb")
        s = pickle.load(f)
        f.close()
        return s
    except (IOError, EOFError) as e:
        s = {
            "FONT": ("Courier", 12, "normal"),
            "BG_COLOR": 'black',
            "TEXT_COLOR": 'white',
            "BACKUP_DIR": "null",
            "SAVES_DIR": "null",
            "TEMP_DIR": "null",
            "SYMBOL": "*",
            "OAUTH": "null"
        }
        save(s)
        return s


def main():
    global settings  # Writes

    settings = reload()
    gui_elements = create_GUI()
    gui_elements[ROOT].bind("<Return>", lambda event: get_command(gui_elements))
    gui_elements[ROOT].mainloop()
    save(settings)


if __name__ == "__main__":
    main()
