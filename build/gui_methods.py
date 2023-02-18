import os
from tkinter import messagebox
import sys
import win32wnet
import tkinter
import json
import shared

USER = ""
PASS = ""
FILESHARE_NAME = ""
FILESHARE_IP = ""

JSON = "links.json"


class GuiMethods(tkinter.Tk):
    """Useful methods"""
    def __init__(self):
        pass

    def sure(self, title, message, icon="question"):
        """ask ok/cancel messagebox with output"""
        sure = messagebox.askokcancel(
            title=title,
            message=message,
            icon=icon
            )
        return sure

    def errormsg(self, text):
        """tkinter error message box"""
        super().__init__()
        self.wm_attributes('-topmost', 1)
        self.withdraw()
        messagebox.showerror(
            title="Error",
            message=text
            )
        self.destroy()

    def msgbox(self, title, text):
        """tkinter messagebox"""
        super().__init__()
        self.wm_attributes('-topmost', 1)
        self.withdraw()
        messagebox.showinfo(
            title=title,
            message=text
            )
        self.destroy()

    def yes_no(self, title, text):
        """tkinter yes/no choice box"""
        super().__init__()
        self.wm_attributes('-topmost', 1)
        self.withdraw()
        yes_no = messagebox.askyesnocancel(
            title=title,
            message=text
            )
        self.destroy()
        return yes_no

    def open_conn(self, host, n=0):
        """open connection to host
            for demo version, this feature is turned off"""
        if True:
            return
        # if ran multiple times, switches from host name to host ip
        if n > 2:
            if FILESHARE_NAME in host:
                host = host.replace(FILESHARE_NAME, FILESHARE_IP)
        n += 1
        # first tries to write a dummy file on host location
        try:
            dummy_file = f"{host}\\dummy.txt"
            with open(dummy_file, "w", encoding="utf-8"):
                pass
            os.remove(dummy_file)
        # if fails tries to create connection
        except (PermissionError, FileNotFoundError):
            try:
                win32wnet.WNetAddConnection2(0, None, host, None, USER, PASS)
            except win32wnet.error:
                # if can't connect for several times
                # it fails and sw shuts down
                if n > 5:
                    self.errormsg(
                        'Could not connect.\
                        \n\nTip: Try re-logging to windows to close existing connections')
                    self.close_conn(host)
                    sys.exit()
                # if can't connect tries to close the connection
                # and restarts the function
                try:
                    win32wnet.WNetCancelConnection2(host, 0, 0)
                    return self.open_conn(host, n)
                except win32wnet.error:
                    return self.open_conn(host, n)

    def close_conn(self, host):
        """close connection
            for demo version, this feature is turned off"""
        if True:
            return
        try:
            win32wnet.WNetCancelConnection2(host, 0, 0)
        except (win32wnet.error, TypeError):
            try:
                if FILESHARE_NAME not in host:
                    return
                host = host.replace(FILESHARE_NAME, FILESHARE_IP)
                win32wnet.WNetCancelConnection2(host, 0, 0)
            except (win32wnet.error, TypeError):
                return

    def gui_update(self, gui, percent: int, text):
        """update MainGui progressbar"""
        gui.progressbar["value"] = percent
        gui.bottom_label_update(text)
        gui.update_idletasks()

    def dump_json(self):
        with open(JSON, "w", encoding="utf-8") as f_dump:
            json.dump(shared.treedata, f_dump, indent=4)

    def load_json(self):
        """load data for treeview from json file"""
        with open(JSON, encoding="utf-8") as f_load:
            shared.treedata = json.load(f_load)
