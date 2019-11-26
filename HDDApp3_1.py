# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 13:54:56 2019

@author: Avishek Paul
"""

# from tkinter import NW
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, BOTH, END, LEFT
import threading
import time
import pandas as pd
import os
# import Queue
import sys

import win32api

sys.setrecursionlimit(1500)
pd.set_option("display.max_colwidth", 10000)
pd.set_option('display.max_columns', 15)
pd.set_option('precision', 8)

TITLE_FONT = ("Arial", 14)
LARGE_FONT = ("Times New Roman", 11)


class HardDiskContent(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "HDD Content Reader")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.SystemParam = {
            "DriveLetter": tk.StringVar(),
            "SaveFile": tk.StringVar()}

        # Store different page information. Add here new page for initialization
        self.frames = {}

        #        for F in (StartPage,GeneralParameters):
        F = StartPage
        frame = F(container, self)
        self.frames[F] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    # Function for showing a frame
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.update()
        frame.event_generate("<<ShowFrame>>")

    def get_page(self, page_class):
        return self.frames[page_class]


class Threader(threading.Thread):

    def __init__(self, Drive_letter):

        threading.Thread.__init__(self, Drive_letter)
        self.daemon = True
        self.Drive_letter = Drive_letter

    def run(self):

        #         while True:
        #        print("Look a while true loop that doesn't block the GUI!")
        print("Scanning Drive: ", self.Drive_letter)
        #        time.sleep(1)

        directory_list = []

        for (dirpath, dirnames, filenames) in os.walk(self.Drive_letter):
            for k in range(1):
                directory_list.append(dirpath)

        print(directory_list)
        return directory_list


class StartPage(tk.Frame):
    # Initialization loop. Anything declared here is executed as soon as the program is run.
    # Even if the page is not visible
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Label for start Page
        label = tk.Label(self, text=" Sakata Lab ", font=TITLE_FONT)
        label.pack(pady=10, padx=10)

        top_frame = tk.LabelFrame(self, text="Selection", padx=5, pady=5)

        label0 = tk.Label(top_frame, text="Select Drive")
        label0.grid(row=1, column=1, columnspan=2)

        label1 = tk.Label(top_frame, text="Save FileName")
        label1.grid(row=2, column=1, columnspan=2)

        button = tk.Button(top_frame, text="Scan", command=lambda: [self.scan()])
        button.grid(row=1, column=5, columnspan=2, padx=10, pady=5)

        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        #        drives = [drivestr in drives.split('\000') if drivestr]
        print(drives)

        self.drive_selection = ttk.Combobox(top_frame, values=drives, height=4, width=10)
        self.drive_selection.grid(row=1, column=3, columnspan=2)
        self.drive_selection.bind("<<ComboboxSelected>>", self.Drive_letter)

        self.entry2 = tk.Entry(top_frame, textvariable=self.controller.SystemParam["SaveFile"], width=20)
        self.entry2.grid(row=2, column=3, columnspan=2)

        button2 = tk.Button(top_frame, text="Save", command=lambda: [self.save_data(controller)])
        button2.grid(row=2, column=5, columnspan=2, padx=10)

        # LAYOUT
        top_frame.pack()

    def Drive_letter(self, event):
        try:
            self.controller.SystemParam["DriveLetter"] = self.drive_selection.get()
            print("Selected Drive Letter = ", self.controller.SystemParam["DriveLetter"])
        # TODO: try to restrict that exception
        except:
            messagebox.showwarning("Drive Selection Notification", "No Option Selected")

    def Drive_Scanner(self, *args):

        print('Extra Arguments ', args)
        #        print("Scanning Drive: ",Drive_letter)
        print(self.controller.SystemParam["DriveLetter"])
        directory_list = []

        for (dirpath, dirnames, filenames) in os.walk(self.controller.SystemParam["DriveLetter"]):
            for k in range(1):
                directory_list.append(dirpath)

        #        self.directory_list = directory_list
        #        print(directory_list)
        time.sleep(5)
        self.controller.directory_list = directory_list
        

    # Function to notify the user of selection     
    def scan(self):

        if not self.drive_selection.get():
            print("Drive Not Selected")
        else:
            #            print(self.controller.SystemParam["DriveLetter"])

            Scan_Process = threading.Thread(target=self.Drive_Scanner, daemon=True)
            Scan_Process.start()
            Scan_Process.join()
            directory_list = self.controller.directory_list
            print(self.controller.directory_list)
            #            directory_list = []
            #    #        file_list_test = []
            #
            #            for (dirpath, dirnames, filenames) in os.walk(self.controller.SystemParam["DriveLetter"]):
            #                for k in range(1):
            #    #            for dir in dirpath:
            #    #                f_test.append(dir)
            #                    directory_list.append(dirpath)
            #                    print(dirpath)
            #    #                file_list_test.append(os.path.join(dirpath+"\\"+dir))
            info = win32api.GetVolumeInformation(self.controller.SystemParam["DriveLetter"])
            print("disk serial number = %d" % info[1])
            directory_list.insert(0, info[1])
            directory_list.insert(0, info[0])
            print(pd.DataFrame(directory_list))

            self.new_data = directory_list

            messagebox.showinfo("Scan Complete", "Selected drive scanned successfully!")

    def set_save_filepath(self, controller):

        #        print(self.CableDatabase_Entry.index("end"))
        try:
            self.entry2.delete(0, END)
            filepath = filedialog.askopenfilename(initialdir="/", title="Open file for Database",
                                                  filetypes=(("xlsx files", "*.xlsx"), ("all files", "*.*")))
            self.controller.SystemParam["SaveFile"] = filepath
            print(self.controller.SystemParam["SaveFile"])
            self.entry2.insert(END, filepath)
        except:
            self.entry2.insert(END, "There was an error opening ")
            self.entry2.insert(END, filepath)
            self.entry2.insert(END, "\n")

        self.save_data(controller)

    def save_data(self, controller):

        if not self.controller.SystemParam["SaveFile"].get():
            messagebox.showwarning("File Name Missing", "File Name not entered")
        else:
            filename = self.controller.SystemParam["SaveFile"].get()
            print(filename)

            directory_list = pd.DataFrame(self.new_data)
            directory_list.to_csv(filename, header=None, index=False,sep='\t')
            messagebox.showinfo("Save Successful", "Directory Names saved successfully!")


if __name__ == "__main__":
    app = HardDiskContent()
    app.geometry("600x200")
    app.mainloop()
