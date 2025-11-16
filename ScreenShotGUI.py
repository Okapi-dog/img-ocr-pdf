# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog,messagebox
import os, signal
import threading
import time
import pyautogui
import math
import json
import glob

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.SSlabel = tk.Label(root, text="Number of screenshots")
        self.SSlabel.place(x=20, y=10)
        self.SS_num = tk.Entry(root)
        self.SS_num.place(x=20, y=30)
        self.var = tk.StringVar()
        self.var.set("Select image directory")
        self.lbl = tk.Label(root, textvariable=self.var)

        self.button = tk.Button(root)
        self.button["text"] = "Start ScreenShot"
        self.button["command"] = self.thread
        self.button.place(x=50, y=70)

        self.button2 = tk.Button(root)
        self.button2["text"] = "Config"
        self.button2["command"] = self.create_window
        self.button2.place(x=190, y=70)

        self.quit = tk.Button(root, text="Quit")
        self.quit["command"] = self.appQuit
        self.quit.place(x=300, y=70)
    
    def set_Text(self, text):
        self.SSlabel["text"]=text


    def thread(self):
        global th
        th = threading.Thread(target=self.ScreenShot)
        th.start()

    def appQuit(self):
        os.kill(os.getpid(), signal.SIGKILL)

    
    def ScreenShot(self):
        path = os.path.dirname(__file__)+"/ScreenShot_config.json"
        try:
            with open(path) as f:
                config = f.read()
            config = json.loads(config)
        except FileNotFoundError:
            messagebox.showerror("Error", 'No config file! Please set config')
            self.create_window()
            exit(1)
        wait_second = config["wait_second"]
        interval_second = config["interval_second"]
        nextpage_key = config["nextpage_key"]
        img_dir = config["img_dir"]
        del_directory_files = config["del_directory_files"]

        if not (type(wait_second)==int and type(interval_second)==int):
            messagebox.showerror("Error", "Value error in config")
        
        try:
            SS_num = int(self.SS_num.get())
        except ValueError:
            messagebox.showerror("Error", "Value error in number of screenshots")

        if del_directory_files:
            for file in glob.glob(img_dir+"/*"):
                os.remove(file)
        
        time.sleep(wait_second)
        zfill_num = math.floor(math.log10(SS_num))+1
        for i in range(SS_num):
            screenshot = pyautogui.screenshot()
            pyautogui.press(nextpage_key) #キーを押して次のページに移動
            screenshot = screenshot.convert('RGB') # jpgに変換するため
            screenshot.save(img_dir+"/"+str(i+1).zfill(zfill_num)+".jpg")
            time.sleep(interval_second)
        self.set_Text("ScreenShot Done!")

    def create_window(self):
        path = os.path.dirname(__file__)+"/ScreenShot_config.json"
        global t, text,text2,text3,check_var,key_stringvar
        try:
            with open(path) as f:
                config = f.read()
            config = json.loads(config)
            wait_second = config["wait_second"]
            interval_second = config["interval_second"]
            nextpage_key = config["nextpage_key"]
            img_dir = config["img_dir"]
            del_directory_files = config["del_directory_files"]
        except FileNotFoundError:
            wait_second = 2
            interval_second = 1
            nextpage_key = "right"
            img_dir = os.path.dirname(__file__)
            del_directory_files = False
        t = tk.Toplevel(self)
        t.geometry("450x450")
        t.wm_title("Screen Shot Config")
        l = tk.Label(t, text="Delay before first screenshot")
        l.place(x=10, y=0)
        text = tk.Entry(t, width=20)
        text.insert(0, str(wait_second))#前回のAPI設定を表示
        text.place(x=10, y=30)
        l2 = tk.Label(t, text="Interval seconds between screenshots")
        l2.place(x=10, y=60)
        text2 = tk.Entry(t, width=20)
        text2.insert(0, str(interval_second))
        text2.place(x=10, y=90)
        l_key = tk.Label(t, text="choose key to next page (default: right arrow key)")
        l_key.place(x=10, y=120)
        key_stringvar = tk.StringVar(t)
        key_stringvar.set(nextpage_key)
        dropdown_key = tk.OptionMenu(t, key_stringvar, "right", "left", "up", "down", "space")
        dropdown_key.place(x=10, y=150)
        l3 =tk.Label(t, text="Screen Shot image directory")
        l3.place(x=10, y=180)
        text3 = tk.Entry(t, width=20)
        text3.insert(0, img_dir)
        text3.place(x=10, y=210)
        button2= tk.Button(t)
        button2.place(x=10, y=240)
        button2["text"] = "Choose Dir"
        button2["command"] = self.set_dir
        check_var = tk.BooleanVar(t)
        check = tk.Checkbutton(
            t,
            text="clear img directory before screenshot",
            variable=check_var  #set variable
        )
        check_var.set(del_directory_files) #前回の設定を表示
        check.place(x=10, y=270)  # チェックボックスの位置を指定
        button3 = tk.Button(t)
        button3["text"] = "Save"
        button3["command"] = self.saveconfig
        button3.place(x=10, y=300)

    def saveconfig(self):
        wait_second = text.get()
        interval_second = text2.get()
        nextpage_key = key_stringvar.get()
        img_dir = text3.get()
        del_directory_files = check_var.get()
        
        if not (wait_second.isdigit() and interval_second.isdigit()):
            messagebox.showerror("Error", "Value error")
            t.destroy()
            exit(1)
        if not os.path.exists(img_dir):
            messagebox.showerror("Error", "Directory does not exist")
            t.destroy()
            exit(1)
        path = os.path.dirname(__file__)+"/ScreenShot_config.json"
        with open(path, mode='w') as f:
            f.write(json.dumps({"wait_second":int(wait_second), "interval_second":int(interval_second), "nextpage_key":nextpage_key, "img_dir":img_dir, "del_directory_files":del_directory_files}))
        t.destroy()

    def set_dir(self):
        img_dir = filedialog.askdirectory(initialdir=text3.get())
        text3.delete( 0, tk.END )
        text3.insert(0, img_dir)



        

root = tk.Tk()
root.geometry("500x100")
root.title("ScreenShot")
app = Application(master=root)
app.mainloop()
