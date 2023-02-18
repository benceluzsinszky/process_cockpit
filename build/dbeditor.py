import os
import sys
import glob
import time
import json
import subprocess
import datetime
from gui_methods import GuiMethods
import tkinter
import shared
import multiprocessing


class DBEditor():
    """class for database editor and corresponding functions"""

    def __init__(self):
        self.parent = os.path.dirname(os.path.abspath(''))
        self.data = None
        self.meslink = None
        self.mesdb = None
        self.bulklink = None
        self.bulkdb = None
        self.download_time = None
        self.modification_time = None
        self.reload_result = False
        self.count = 0
        self.appdb = "db.txt"
        self.now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.user = os.getlogin()
        self.dbedit = "parametereditor.txt"
        with open("last_choice.json", encoding="utf-8") as f:
            self.last_choice = json.load(f)
        # load data from treeview
        self.get_tree_data()

    def upload_gui(self, gui):
        """tkinter gui for upload button"""
        self.upload_button = tkinter.Tk()
        self.upload_button.attributes("-topmost", True)
        self.upload_button.geometry('57x26+0+0')
        self.upload_button.overrideredirect(True)
        upload_button = tkinter.Button(
            self.upload_button,
            text="UPLOAD",
            command=lambda: self.upload_db(gui, self.appdb))
        upload_button.grid(column=1, row=1)
        self.upload_gui_close_condition(gui)
        self.upload_button.mainloop()

    def upload_gui_close_condition(self, gui):
        if not self.process_ruestdaten.is_alive():
            self.upload_db(gui, self.appdb)
            self.upload_button.withdraw()
            self.upload_button.mainloop()
        self.upload_button.after(
            100, lambda: self.upload_gui_close_condition(gui))

    def reload(self):
        """reload last opened database without downloading a new one"""
        list_of_files = glob.glob(".\\archive\\*.txt")
        latest = os.path.basename(max(list_of_files, key=os.path.getatime))
        latest_file = latest[23::]
        self.reload_result = GuiMethods().yes_no(
            "Reload last opened db",
            f"Do you want to reload the last opened database?\
            \n\nLast opened database: {latest_file}\
            \nFrom: {self.last_choice[0]}, {self.last_choice[1]}"
        )

    def get_tree_data(self):
        """load treedata from MainGui"""
        self.data = (shared.treedata[shared.chosen_data[0]][shared.chosen_data[1]])
        self.meslink = self.data["MESlink"]
        self.mesdb = self.meslink + "\\" + self.data["DB"]
        self.bulklink = self.data["BSlink"]
        self.bulkdb = self.bulklink + self.data["BulkDB"] + "\\" + self.data["DB"]

    def download_db(self, gui):
        """download db from fileshare"""
        with open("last_choice.json", "w", encoding="utf-8") as json_file:
            json.dump(shared.chosen_data, json_file)
        archivedb = f"{self.parent}\\Archive\\{self.now}_{self.user}_{self.data['DB']}"
        GuiMethods().gui_update(
            gui,
            20,
            "Connecting to bulk storage"
        )
        GuiMethods().open_conn(self.bulklink)
        GuiMethods().gui_update(
            gui,
            40,
            "Downloading database"
        )
        status_appdb = subprocess.call(
            f'copy "{self.bulkdb}" "{self.appdb}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        GuiMethods().gui_update(
            gui,
            60,
            "Downloading database"
        )
        subprocess.call(
            f'copy "{self.bulkdb}" "{archivedb}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        GuiMethods().close_conn(self.bulklink)
        # if download unsuccesful
        if status_appdb != 0:
            GuiMethods().errormsg('Database cannot be downloaded')
        GuiMethods().gui_update(
            gui,
            100,
            "Opening Database editor"
        )
        # return value to dbeditor
        return status_appdb

    def upload_db(self, gui, file):
        """upload db to fileshares"""
        # Used to see if file wa modified:
        # self.modification_time = os.path.getmtime(file)
        # if not self.download_time:
        #     self.download_time = 0

        # if (file != self.appdb or self.modification_time - self.download_time > 8):

        upload = GuiMethods().yes_no(
            'New database',
            'Do you want to upload the latest database?'
        )
        if upload:
            # connect to fileshares+
            GuiMethods().gui_update(gui, 20, "Opening connections")
            GuiMethods().open_conn(self.bulklink)
            GuiMethods().open_conn(self.meslink)
            # upload new db
            GuiMethods().gui_update(
                gui,
                40,
                "Uploading new database"
            )
            status_bulkdb_up = subprocess.call(
                f'copy {file} {self.bulkdb}', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
            GuiMethods().gui_update(
                gui,
                60,
                "Uploading new database"
            )
            status_mesdb_up = subprocess.call(
                f'copy {file} {self.mesdb}', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)
            # close connection to fileshares
            GuiMethods().gui_update(
                gui,
                80,
                "Uploading new database"
            )
            GuiMethods().close_conn(self.bulklink)
            GuiMethods().close_conn(self.meslink)
            # feedback from upload
            if status_bulkdb_up != 0:
                GuiMethods().errormsg(
                    'Could not upload to bulk storage\
                    \n\nTip: Try re-logging to windows to close off connections'
                )
                sys.exit()
            if status_mesdb_up != 0:
                GuiMethods().errormsg(
                    'Could not upload to MES server\
                    \n\nTip: Try re-logging to windows to close off connections'
                )
                sys.exit()
            if status_bulkdb_up + status_mesdb_up == 0:
                GuiMethods().gui_update(
                    gui,
                    100,
                    "Upload succesfull!"
                )
                GuiMethods().msgbox(
                    'Success',
                    'The new databases were uploaded succesfully.'
                )
        return

    def open_ruest(self):
        ruest_status = subprocess.call(
            self.dbedit, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if ruest_status != 0:
            GuiMethods().errormsg("ParameterEditor can not be opened")
        self.modification_time = os.path.getmtime(self.appdb)

    def ruestendaten(self, gui):
        """downloads, runs the database editor SW then uploads"""
        # if treeview data is the same as the last opened ask for reload
        if self.last_choice == shared.chosen_data:
            self.reload()
        if self.reload_result is None:
            return
        # connect to databases, download files
        GuiMethods().gui_update(
            gui,
            100,
            "Opening Database editor"
        )
        gui.update()
        if not self.reload_result:
            self.download_db(gui)
        # open database editor, save current time for later
        self.download_time = time.time()

        # start ruestdaten.exe as another process
        self.process_ruestdaten = multiprocessing.Process(
            target=self.open_ruest)
        self.process_ruestdaten.start()
        self.upload_gui(gui)

        GuiMethods().gui_update(gui, 0, " ")
