# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog,messagebox
import os, signal
import threading
import sys
import time
import pyautogui
import math

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
        self.button["text"] = "Set JPG Dir"
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
        path = os.path.dirname(__file__)+"/ScreenShot_config.txt"
        try:
            with open(path) as f:
                config = f.read()
        except FileNotFoundError:
            messagebox.showerror("Error", 'No config file, Input your API key')
            self.create_window()
            exit(1)
        config = config.split("\n")
        wait_second = config[0]
        interval_second = config[1]

        try:
            wait_second = int(wait_second)
            interval_second = int(interval_second)
        except ValueError:
            messagebox.showerror("Error", "Value error in config") 
        
        try:
            SS_num = int(self.SS_num.get())
        except ValueError:
            messagebox.showerror("Error", "Value error in number of screenshots") 
        
        SS_directory = filedialog.askdirectory(initialdir = img_dir)
        time.sleep(wait_second)
        zfill_num = math.floor(math.log10(SS_num))+1
        for i in range(SS_num):
            screenshot = pyautogui.screenshot()
            pyautogui.press('right') #右矢印キーを押して次のページに移動
            screenshot = screenshot.convert('RGB') # jpgに変換するため
            screenshot.save(SS_directory+"/"+str(i+1).zfill(zfill_num)+".jpg")
            time.sleep(interval_second)
        self.set_Text("ScreenShot Done!")

    def create_window(self):
        path = os.path.dirname(__file__)+"/ScreenShot_config.txt"
        try:
            with open(path) as f:
                config = f.read()
            config = config.split("\n")
            wait_second = config[0]
            interval_second = config[1]
        except FileNotFoundError:
            wait_second = "2"
            interval_second = "1" 
        global t, text,text2
        t = tk.Toplevel(self)
        t.geometry("350x150")
        t.wm_title("Screen Shot Config")
        l = tk.Label(t, text="Delay before first screenshot")
        l.place(x=100, y=5)
        text = tk.Entry(t, width=20)
        text.insert(0, wait_second)#前回のAPI設定を表示
        text.place(x=90, y=30)
        l2 = tk.Label(t, text="Interval seconds between screenshots")
        l2.place(x=100, y=50)
        text2 = tk.Entry(t, width=20)
        text2.insert(0, interval_second)
        text2.place(x=90, y=70)
        button3 = tk.Button(t)
        button3.place(x=150, y=120)
        button3["text"] = "Save"
        button3["command"] = self.saveconfig


    def saveconfig(self):
        wait_second = text.get()
        interval_second = text2.get()
        
        if not (wait_second.isdigit() and interval_second.isdigit()):
            messagebox.showerror("Error", "Value error") 
            t.destroy()
            exit(1)
        path = os.path.dirname(__file__)+"/ScreenShot_config.txt"
        with open(path, mode='w') as f:
            f.write(wait_second+"\n"+interval_second)
        t.destroy()


args = sys.argv
if len(args) > 1:
    img_dir = args[1]
else:
    img_dir = os.path.dirname(__file__)

root = tk.Tk()
root.geometry("700x100")
root.title("Make pdf")
app = Application(master=root)
app.mainloop()
