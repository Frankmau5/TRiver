#!/usr/bin/env python3

import sys
import datetime
import torrent_parser as tp
import humanize
import tkinter
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import simplejson as json

class Win_ui():
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("TRiver")
        self.window.geometry("800x600") 
        m = self.mk_menu()
        self.window.config(menu = m)
        self.mk_text()
        self.tr_backend = TRiver_Backend()
        self.window.mainloop()

    def mk_menu(self):
        menu_bar = tkinter.Menu(self.window)
        filem = tkinter.Menu(menu_bar)
        filem.add_command(label="Open",command= self.on_open)
        filem.add_command(label="About", command= self.on_about)
        filem.add_command(label="Save As", command= self.save_as)
        filem.add_command(label="Exit", command= self.on_exit)

        menu_bar.add_cascade(label="File", menu = filem)
        return menu_bar

    def mk_text(self):
        scrollbar = tkinter.Scrollbar(self.window,orient='vertical')
        scrollbar.pack(side=tkinter.RIGHT, fill='y')
        
        self.t = tkinter.Text(self.window, yscrollcommand=scrollbar.set)
        self.t.insert(tkinter.INSERT, "Please open a torrent file to view the metadata.")
        #self.t.config(state=tkinter.DISABLED) # Read-Only
        self.t.pack(expand = True, fill=tkinter.BOTH)
        scrollbar.config(command=self.t.yview)
        
        
    def on_exit(self):
        self.window.destroy()
    
    def save_as(self):
        name = fd.asksaveasfilename()
        name = name.replace(".torrent", "")
        myJsonStr = self.t.get('1.0', tkinter.END)
        if "Please open a torrent file " in myJsonStr:
            pass
        else:
            jsonDict = json.loads(myJsonStr)
            tp.create_torrent_file(f"{name}.torrent", jsonDict)

    def on_about(self):
        mb.showinfo("About", "TRiver for windows - version 1.0.0\nWebsite: https://frankmau5.tech/ \nSupport: https://paypal.me/FrankMulvie")

    def on_open(self):
        name = fd.askopenfilename()

        #data = self.tr_backend.get_torrent_data(name)
        data = self.tr_backend.GetTorrentData(name)

        self.t.config(state=tkinter.NORMAL)
        self.t.delete('1.0',tkinter.END)
        self.t.insert(tkinter.INSERT, data)
        self.t.config(state=tkinter.DISABLED)

    def FormatDataStr(self, data):
        formatedStr = ''

        for item in data:
            for key in item:
                formatedStr = f"{formatedStr} {key} : {item[key]}\n"

        return formatedStr


class TRiver_Backend():
    def __init__(self):
        self.data = None

    def GetTorrentData(self, filepath):
        self.data = tp.parse_torrent_file(filepath)
        self.data = json.dumps(self.data,indent=4)

        return self.data

    def get_torrent_data(self, filepath):
        self.data = tp.parse_torrent_file(filepath)
        text = ""

        for key in self.data:
            if key == "creation date":
                try:
                    dt = datetime.date.fromtimestamp(self.data[key])
                    text = text + str(key) + " = " + str(dt) + "\n\n"
                    continue
                except OverflowError as of:
                    print(str(of))
                except OSError as ose:
                    print(str(ose))
            
            if key == "announce-list":
                d = self.data[key]
                text = text + str(key) + " = "
                for da in d:
                    for dat in da:
                        text = text + str(dat) + " , \n" 

                text = text + "\n\n"
                continue
            
            if key == "info":
                for ckey in self.data[key]:
                    if ckey == "files" :
                        text = text + "Files = "
                        for d in self.data[key][ckey]:
                            text = text + "Size" + " : " + str(self.human_readable_size(d["length"]))   + " , "
                            text = text + "Filename" + " : " + str(d["path"])   + " \n"
                    if "Files =" not in text:
                        if ckey == "name":
                            text = text + " File = " + self.data[key]["name"]
                        if ckey == "length":
                            text = text + "Size : " + str(self.human_readable_size(self.data[key]["length"]))
                            
                text = text + "\n\n"
                continue

            if key == "nodes":
                d = self.data[key]
                text = text + str(key) + " = "
                for da in d:
                    text = text + str(da[0]) + ":" + str(da[1])   + " , "
                text = text + "\n\n"
                continue

            text = text + str(key) + " = " + str(self.data[key]) + "\n\n"

        return text

    def human_readable_size(self, byte_size):
        return humanize.naturalsize(byte_size, gnu=True)

def main():
    win_app = Win_ui()

main()

