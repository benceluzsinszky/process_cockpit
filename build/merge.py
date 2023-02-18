import glob
import os
import csv
import subprocess
from datetime import datetime
import shared
from gui_methods import GuiMethods
import tkinter
from tkinter import scrolledtext


class Merge():
    def __init__(self):
        self.output_path = "output.csv"
        self.filename = None
        self.failed_files = []
        self.get_tree_data()

    def get_tree_data(self):
        self.date_from = shared.date_from
        self.date_to = shared.date_to
        self.choice_from_tree = (
            shared.treedata[shared.chosen_data[0]][shared.chosen_data[1]])
        self.bslink = self.choice_from_tree["BSlink"]
        station = next(iter(self.choice_from_tree["stations"]))
        self.basic_link = f"{self.bslink}\\{station}\\Data"

    def merge_button(self, gui, input_type):

        def file_date(filename):

            file_modification_time = datetime.fromtimestamp(
                os.path.getmtime(filename)).strftime("%Y%m%d")
            if self.date_from <= file_modification_time and file_modification_time <= self.date_to:
                return True
            return False

        GuiMethods().gui_update(gui, 0, "Loading files, please wait...")
        if input_type == "results":
            filepath_ending = f"Data\\{shared.partnumber}"
        elif input_type == "errors":
            filepath_ending = "Data\\Logs"
        elif input_type == "selftest":
            filepath_ending = "Data\\Selftest"

        # file counter
        list_of_files = []
        if len(shared.chosen_data) == 2:
            for station in self.choice_from_tree["stations"]:
                filepath = os.path.join(self.bslink, station, filepath_ending)
                list_of_files_per_station = [
                    file for file in glob.glob(os.path.join(filepath, "*.csv")) if file_date(file)]
                list_of_files.extend(list_of_files_per_station)
            total_files = len(list_of_files)
        else:
            station = self.choice_from_tree["stations"][int(
                shared.chosen_data[2])]
            filepath = os.path.join(self.bslink, station, filepath_ending)
            list_of_files = [
                file for file in glob.glob(os.path.join(filepath, "*.csv")) if file_date(file)]
            total_files = len(list_of_files)

        # file merger
        output_data = []
        number_of_files_loaded = 0
        i = 0
        for file in list_of_files:
            new_data = self.list_from_csv(file)
            if new_data == 0:
                pass
            elif i == 0 and output_data == []:
                output_data = new_data
                i += 1
            else:
                output_data = self.column_comber(output_data, new_data, file)
                i += 1
            number_of_files_loaded += 1
            gui_percent = int((number_of_files_loaded/total_files)*100)
            GuiMethods().gui_update(
                gui,
                gui_percent,
                f"{number_of_files_loaded}/{total_files} files loaded"
            )
        if input_type == "errors":
            # remove empty columns and rows from array
            # and rows with useless data
            temp_list = [line[:3]+line[7:]
                         for line in output_data if line != [] and line[10] != '']
            output_data = temp_list
            output_data[1:] = sorted(
                output_data[1:], key=lambda row: row[2], reverse=False)
        else:
            output_data[1:] = sorted(
                output_data[1:], key=lambda row: row[3], reverse=False)

        # output writer
        try:
            with open(self.output_path, 'w', newline='', encoding="UTF-8") as output:
                writer = csv.writer(output, delimiter=";")
                writer.writerows(output_data)
            if self.failed_files:
                shared.failed_files = self.failed_files
                GuiMethods().gui_update(
                    gui,
                    100,
                    "Some files did not load properly, click here for more info"
                )
                self.log(gui)
            else:
                GuiMethods().gui_update(
                    gui,
                    100,
                    "Opening output.csv..."
                )
            subprocess.Popen(f'explorer "{self.output_path}"')
        except PermissionError:
            GuiMethods().gui_update(
                gui,
                0,
                "Please close output.csv!"
            )

    def log(self, gui):
        def log_popup(event):
            root = tkinter.Tk()
            root.title("Log")
            log_entry = scrolledtext.ScrolledText(
                root, width=150, height=35, wrap=tkinter.WORD)
            log_entry.pack(side="bottom", pady=10, padx=10)
            log_str = ""
            for i in shared.failed_files:
                log_str += f"{i}\n"
            log_entry.insert(tkinter.END, log_str)
            log_entry.config(state="disabled")
            root.mainloop()
            gui.bottom_label.unbind("<Button-1>")

        gui.bottom_label.bind("<Button-1>", log_popup)

    def list_from_csv(self, input_file):
        """makes list from csv rows"""
        temp_list_data = []
        with open(input_file, 'r', encoding="UTF-8-sig") as csvfile:
            list_data = csv.reader(csvfile, delimiter=";")
            try:
                for row in list_data:
                    temp_list_data.append(row)
                list_data = temp_list_data
                return list_data
            # if there is an issue with the file
            except (csv.Error, UnicodeDecodeError):
                return 0

    def column_comber(self, master, new_input, filepath):
        master_header = master[0]
        new_input_header = new_input[0]
        # if headers are the same, then just extend master
        if master_header == new_input[0]:
            master.extend(new_input[1:])
            return master

        if len(master_header) >= len(new_input_header):
            shorter = new_input
            longer = master
        elif len(master_header) < len(new_input_header):
            shorter = master
            longer = new_input
            # checks if any of new_input is in master master,
            # if not something is wrong with headers
        if not any(item in new_input_header for item in master_header):
            self.failed_files.append(
                f"ERROR: Headers are not recognised in {filepath}")
            return

        shorter_header = shorter[0]
        longer_header = longer[0]

        temp_longer = longer_header
        for idx, i in enumerate(shorter_header):
            if i not in longer_header:
                if idx == 0 or idx-1 not in longer_header:
                    temp_longer.append(i)
                elif idx-1 in longer_header:
                    temp_longer.insert(idx, i)
        longer[0] = temp_longer

        # creates a 2d array with:
        # as many columns (lists) as headers in longer and
        # as many rows as rows in shorter
        temp_array = [["" for _ in range(len(longer[0]))]
                      for _ in range(len(shorter))]

        # goes through shorter headers, finds it in longer[0]
        for idx, i in enumerate(shorter_header):
            index = longer[0].index(i)

            # copies whole column (j[idx]) to array[idy][index]
            for idy, j in enumerate(shorter):
                temp_array[idy][index] = j[idx]

        longer.extend(temp_array[1:])
        return longer
