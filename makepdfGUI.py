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
import shutil
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
        self.button["text"] = "Start"
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
        th.daemon = True  # 親が死んだら即死する設定
        th.start()

    def appQuit(self):
        self.master.destroy()
        sys.exit(0)

    async def get_hocr(self,fileName, APIKEY):
        async with self.semaphore:
            print("google OCR",os.path.basename(fileName))
            self.set_Text("google OCR "+os.path.basename(fileName))
            await gcv.aio_detect_text(fileName, APIKEY)
            
            print ("Convert ", os.path.basename(fileName) ,"to hocr")
            self.set_Text("Convert " + os.path.basename(fileName) + " to hocr")
            hocrFileName = fileName.replace("jpg", "hocr")
            jsonFileName = fileName.replace("jpg", "jpg.json")
            with open(jsonFileName, 'r', encoding='utf-8' ) as instream:
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

        tmp_dir = os.path.join(os.path.dirname(__file__), "tmp")
        #tmpフォルダをとりあえず作成して、その中身を空にする
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_files = glob.glob(os.path.join(tmp_dir, "*"))
        for file in tmp_files:
            os.remove(file)

        path = os.path.join(os.path.dirname(__file__), "OCR_config.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = f.read()
        except FileNotFoundError:
            messagebox.showerror("Error", 'No config file, Input your API key')
            self.create_window()
            exit(1)
        config = json.loads(config)
        APIKEY = config["APIKEY"]
        IsLimitingSize = config["IsLimitingSize"]
        disable_gs = config["disable_gs"]
        gs_path = config["gs_path"]
        img_dir = config["img_dir"]
        pdf_dir = config["pdf_dir"]

        if APIKEY=="":
            messagebox.showerror("Error", 'No API key, Input your API key')
        
        try:
            files = sorted(glob.glob(os.path.join(img_dir, "*jpg")))
        except TypeError:                                  # cancel
            exit(1)
        for file in files:
            shutil.copy(file,os.path.join(os.path.dirname(__file__), "tmp"))
        files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "tmp", "*jpg")))
        
        asyncio.run(self.get_hocrs(files, APIKEY))
       

        print("Generating out.pdf")
        self.set_Text("Generating out.pdf")
        hocr2pdf.export_pdf(os.path.join(os.path.dirname(__file__), "tmp"), 150, pdf_dir, IsLimitingSize)

        print("Reducing pdf size")
        self.set_Text ("Reducing pdf size")

        if disable_gs == "False":
            out = "-sOutputFile=" + pdf_dir.replace(".pdf","_gs.pdf")
            command = [gs_path, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5", "-dPDFSETTINGS=/default", "-dDEVICEWIDTHPOINTS=595", "-dPDFFitPage", "-dNOPAUSE", "-dQUIET", "-dBATCH", "-dAutoRotatePages=/None", out, pdf_dir]
            subprocess.check_output(command, stderr=subprocess.STDOUT)    #gsを通すと、なぜか日本語を選択した際に文字化けする。また、shellscriptからの実行ができなくなる。
        print("Done!")
        self.set_Text("Done!")
    

    def create_window(self):
        path = os.path.join(os.path.dirname(__file__), "OCR_config.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = f.read()
            config = json.loads(config)
            APIKEY = config["APIKEY"]
            IsLimitingSize = config["IsLimitingSize"]
            disable_gs = config["disable_gs"]
            gs_path = config["gs_path"]
            img_dir = config["img_dir"]
            pdf_dir = config["pdf_dir"]
        except FileNotFoundError:
            APIKEY = ""
            IsLimitingSize = True
            disable_gs = True
            gs_path = "gs"
            img_dir = os.path.dirname(__file__)
            pdf_dir = os.path.join(os.path.dirname(__file__), "out.pdf")
        global t, text, check_var, check_var2,text3,text4, text_gs_path
        t = tk.Toplevel(self)
        t.geometry("400x400")
        t.wm_title("API KEY Config")
        l = tk.Label(t, text="Set Google API key")
        l.place(x=10, y=5)
        text = tk.Entry(t, width=20)
        text.insert(0, APIKEY)#前回のAPI設定を表示
        text.place(x=10, y=30)
        check_var = tk.BooleanVar(t)
        check = tk.Checkbutton(
            t,
            text="limit pdf size like A4",
            variable=check_var  #set variable
        )
        check_var.set(IsLimitingSize) #前回の設定を表示
        check.place(x=10, y=60)  # チェックボックスの位置を指定
        check_var2 = tk.BooleanVar(t)
        check2 = tk.Checkbutton(
            t,
            text="do not run gs",
            variable=check_var2  #set variable
        )
        check_var2.set(disable_gs) #前回の設定を表示
        check2.place(x=10, y=90)  # 二つ目のチェックボックスの位置を指定
        l_gs = tk.Label(t, text="Path to Ghostscript (if run gs to reduce pdf size)")
        l_gs.place(x=10, y=120)
        text_gs_path = tk.Entry(t, width=20)
        text_gs_path.insert(0, gs_path)
        text_gs_path.place(x=10, y=150)
        l3 =tk.Label(t, text="Screen Shot image directory")
        l3.place(x=10, y=180)
        text3 = tk.Entry(t, width=20)
        text3.insert(0, img_dir)
        text3.place(x=10, y=210)
        button2= tk.Button(t)
        button2.place(x=10, y=240)
        button2["text"] = "Set IMG Directory"
        button2["command"] = self.set_img_dir

        l4 =tk.Label(t, text="Output PDF path")
        l4.place(x=10, y=270)
        text4 = tk.Entry(t, width=20)
        text4.insert(0, pdf_dir)
        text4.place(x=10, y=300)
        button4= tk.Button(t)
        button4.place(x=10, y=330)
        button4["text"] = "Set PDF Filename"
        button4["command"] = self.set_pdf_dir
        button3 = tk.Button(t)
        button3.place(x=10, y=360)
        button3["text"] = "Save"
        button3["command"] = self.saveconfig

    def saveconfig(self):
        api_key = text.get()
        if api_key == "":
            messagebox.showerror("Error", "No API KEY") 
            t.destroy()
            exit(1)
        elif not os.path.exists(text3.get()):
            messagebox.showerror("Error", "IMG Directory does not exist")
            t.destroy()
            exit(1)
        elif not (text4.get().endswith(".pdf")):
            messagebox.showerror("Error", "PDF file must end with .pdf")
            t.destroy()
            exit(1)
        elif not os.path.exists(os.path.dirname(text4.get())):
            messagebox.showerror("Error", "PDF Directory does not exist")
            t.destroy()
            exit(1)
        IsLimitingSize = str(check_var.get())
        disable_gs = str(check_var2.get())
        gs_path = text_gs_path.get()
        img_dir = text3.get()
        pdf_dir = text4.get()
        path = os.path.join(os.path.dirname(__file__), "OCR_config.json")
        with open(path, mode='w', encoding='utf-8') as f:
            f.write(json.dumps({"APIKEY":api_key, "IsLimitingSize":IsLimitingSize, "disable_gs":disable_gs, "gs_path":gs_path, "img_dir":img_dir, "pdf_dir":pdf_dir}))
        t.destroy()
    
    def set_img_dir(self):
        img_dir = filedialog.askdirectory(initialdir=text3.get())
        text3.delete(0, tk.END)
        text3.insert(0, img_dir)

    def set_pdf_dir(self):
        pdf_dir = filedialog.asksaveasfilename(initialdir=text4.get())
        text4.delete(0, tk.END)
        text4.insert(0, pdf_dir)

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
