# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog,messagebox
import os, signal
import subprocess
import glob
import threading
import sys
import json
import asyncio
#以下のファイル(gcv.py,gcv2hocr.py,hocr2pdf.py)は、このファイルと同じディレクトリに置いてください
import gcv
import gcv2hocr
import hocr2pdf

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        self.var = tk.StringVar()
        self.var.set("Select image directory")
        self.lbl = tk.Label(root, textvariable=self.var)
        self.lbl.place(x=50, y=10)

        self.button = tk.Button(root)
        self.button["text"] = "Set JPG Dir"
        self.button["command"] = self.thread
        self.button.place(x=50, y=50)

        self.button2 = tk.Button(root)
        self.button2["text"] = "Config"
        self.button2["command"] = self.create_window
        self.button2.place(x=190, y=50)

        self.quit = tk.Button(root, text="Quit")
        self.quit["command"] = self.appQuit
        self.quit.place(x=300, y=50)
    
    def set_Text(self, text):
        self.var.set(text)


    def thread(self):
        global th
        th = threading.Thread(target=self.makepdf)
        th.start()

    def appQuit(self):
        os.kill(os.getpid(), signal.SIGKILL)

    async def get_hocr(self,fileName, APIKEY):
        async with self.semaphore:
            print("google OCR",os.path.basename(fileName))
            self.set_Text("google OCR "+os.path.basename(fileName))
            await gcv.aio_detect_text(fileName, APIKEY)
            
            print ("Convert ", os.path.basename(fileName) ,"to hocr")
            self.set_Text("Convert " + os.path.basename(fileName) + " to hocr")
            hocrFileName = fileName.replace("jpg", "hocr")
            jsonFileName = fileName.replace("jpg", "jpg.json")
            instream =open(jsonFileName, 'r', encoding='utf-8' )
            resp = json.load(instream)
            resp = resp['responses'][0] if 'responses' in resp and len(resp['responses']) >= 0 and "textAnnotations" in resp['responses'][0] else False
            page = gcv2hocr.fromResponse(resp)
            with (open(hocrFileName, 'w', encoding="utf-8")) as outfile:
                outfile.write(page.render().encode('utf-8') if str == bytes else page.render())
                outfile.close()
    
    async def get_hocrs(self,fileNames, APIKEY, max_concurrency=50):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        tasks= [self.get_hocr(fileName, APIKEY) for fileName in fileNames]
        await asyncio.gather(*tasks)

    
    def makepdf(self):
        path = os.path.dirname(__file__)+"/config.txt"
        try:
            with open(path) as f:
                config = f.read()
        except FileNotFoundError:
            messagebox.showerror("Error", 'No config file, Input your API key')
            self.create_window()
            exit(1)
        config = config.split("\n")
        APIKEY = config[0]
        IsLimitingSize = config[1]
        disable_gs = config[2]

        if APIKEY=="":
            messagebox.showerror("Error", 'No API key, Input your API key')

        dname = filedialog.askdirectory(initialdir = img_dir)
        
        try:
            files = sorted(glob.glob(dname+"/*jpg"))
        except TypeError:                                  # cancel
            exit(1)
        
        asyncio.run(self.get_hocrs(files, APIKEY))
       

        print("Generating out.pdf")
        self.set_Text("Generating out.pdf")
        out0 = dname+"/out0.pdf"
        hocr2pdf.export_pdf(dname, 150, out0, IsLimitingSize)

        print("Reducing pdf size")
        self.set_Text ("Reducing pdf size")

        if disable_gs == "False":
            out = "-sOutputFile=" + dname + "/out.pdf"
            command = ["gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5", "-dPDFSETTINGS=/default", "-dDEVICEWIDTHPOINTS=595", "-dPDFFitPage", "-dNOPAUSE", "-dQUIET", "-dBATCH", "-dAutoRotatePages=/None", out, out0]
            subprocess.check_output(command)    #gsを通すと、なぜか日本語を選択した際に文字化けする。また、shellscriptからの実行ができなくなる。
        print("Done!")
        self.set_Text("Done!")

    def create_window(self):

        global t, text, check_var, check_var2
        t = tk.Toplevel(self)
        t.geometry("350x150")
        t.wm_title("API KEY Config")
        l = tk.Label(t, text="Set Google API key")
        l.place(x=100, y=5)
        text = tk.Entry(t, width=20)
        text.place(x=90, y=30)
        check_var = tk.BooleanVar(t)
        check = tk.Checkbutton(
            t,
            text="limit pdf size like A4",
            variable=check_var  #set variable
        )
        check.place(x=90, y=60)  # チェックボックスの位置を指定
        check_var2 = tk.BooleanVar(t)
        check2 = tk.Checkbutton(
            t,
            text="do not run gs",
            variable=check_var2  #set variable
        )
        check2.place(x=90, y=90)  # 二つ目のチェックボックスの位置を指定
        button3 = tk.Button(t)
        button3.place(x=150, y=120)
        button3["text"] = "Save"
        button3["command"] = self.saveconfig

    def saveconfig(self):
        api_key = text.get()
        if api_key == "":
            messagebox.showerror("Error", "No API KEY") 
            t.destroy()
            exit(1)
        IsLimitingSize = str(check_var.get())
        disable_gs = str(check_var2.get())
        path = os.path.dirname(__file__)+"/config.txt"
        with open(path, mode='w') as f:
            f.write(api_key+"\n"+IsLimitingSize+"\n"+disable_gs)
        t.destroy()


args = sys.argv
if len(args) > 1:
    img_dir = args[1]
else:
    img_dir = os.path.dirname(__file__)

root = tk.Tk()
root.geometry("400x100")
root.title("Make pdf")
app = Application(master=root)
app.mainloop()
