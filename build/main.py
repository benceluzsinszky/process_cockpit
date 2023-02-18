import glob
import sys
import subprocess
import tkinter
import tkinter.font as font
from tkinter import ttk, Menu, Button, Label, filedialog
from datetime import datetime
from tkcalendar import DateEntry
import babel.numbers  # noqa  # imported for py-to-exe
import shared
from merge import Merge
from gui_methods import GuiMethods
from dbeditor import DBEditor
from json_edit import JsonEdit
from multiprocessing import freeze_support


class GuiMain(tkinter.Tk):
    """Class for main interface"""

    def __init__(self):
        super().__init__()
        self.partnumbers = []
        self.count = 0

        GuiMethods().load_json()

        self.center_window()
        self.title("Process Cockpit")
        self.iconbitmap(default="rooster.ico")
        self.protocol("WM_DELETE_WINDOW", sys.exit)

        self.bottom_label_text = tkinter.StringVar()

        self.build_tree()

        button_font = font.Font(family="Arial", size=16, weight="bold")

        self.popup = Menu(self, tearoff=0)
        self.popup.add_command(label="Add", command=self.add_button)
        self.popup.add_command(label="Edit", command=self.edit_button)
        self.popup.add_command(label="Remove", command=self.remove_button)

        self.bind("<Button-3>", self.do_popup)
        self.bind('<Double-Button-1>', self.double_click)
        self.bind('<Button-1>', self.fill_partnumbers)

        ruest_button = Button(self, text="DBEditor",
                              command=self.dbeditor_button, width=10, height=2)
        ruest_button.grid(column=1, row=0, columnspan=2, padx=10, pady=5)
        ruest_button['font'] = button_font

        separator_1 = ttk.Separator(self, orient='horizontal')
        separator_1.grid(column=1, row=1, columnspan=2, sticky="WE", pady=5)

        folders_label = Label(
            self, text="Folders", font=font.Font(
                family="Arial", size=12, weight="bold"))
        folders_label.grid(column=1, columnspan=2, row=2)

        open_mes_button = Button(
            self, text="MES Server", command=self.open_mes, width=10, height=2, font=font.Font(
                family="Arial", size=11, weight="bold"))
        open_mes_button.grid(column=1, row=3, padx=2, pady=5)

        open_bulk_button = Button(
            self, text="Bulk Storage", command=self.open_bulk, width=10, height=2, font=font.Font(
                family="Arial", size=11, weight="bold"))
        open_bulk_button.grid(column=2, row=3, padx=2, pady=5)

        separator_2 = ttk.Separator(self, orient='horizontal')
        separator_2.grid(column=1, row=4, columnspan=2, sticky="WE", pady=5)

        merger_label = Label(
            self, text="Merger", font=font.Font(
                family="Arial", size=12, weight="bold"))
        merger_label.grid(column=1, columnspan=2, row=5)

        canvas = tkinter.Canvas(
            self, width=225, height=110, highlightthickness=1, highlightbackground="black")
        canvas.grid(column=1, row=6, columnspan=2, rowspan=4)

        filters_label = Label(
            self, text="Filters", font=font.Font(
                family="Arial", size=12))
        filters_label.grid(column=1, columnspan=2, row=6, pady=5)

        pnr_label = Label(self, text="PNR:")
        pnr_label.grid(column=1, row=7, sticky="W", padx=10)

        self.combo = ttk.Combobox(
            self, state="readonly", values=list(self.partnumbers), width=12)
        self.combo.grid(column=2, row=7, sticky="W", padx=10)

        date_from = Label(self, text="Date from:")
        date_from.grid(column=1, row=8, sticky="WS", padx=10)
        date_to = Label(self, text="Date to:")
        date_to.grid(column=2, row=8, sticky="WS", padx=10)
        self.cal_from = DateEntry(
            self,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy/mm/dd',
            maxdate=datetime.today()
        )
        self.cal_from.set_date(datetime.today().replace(day=1))
        self.cal_from.grid(column=1, row=9, padx=10, pady=10)

        self.cal_to = DateEntry(
            self,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy/mm/dd',
            maxdate=datetime.today()
        )
        self.cal_to.grid(column=2, row=9, padx=10, pady=10)

        results_button = Button(
            self, text="Results", command=self.results_button, width=10, height=2)
        results_button.grid(column=1, row=10, columnspan=2, padx=2, pady=5)
        results_button['font'] = button_font

        errors_button = Button(
            self, text="Errors", command=self.errors_button, width=10, height=2)
        errors_button.grid(column=1, row=11, columnspan=2, padx=2, pady=5)
        errors_button['font'] = button_font

        selftest_button = Button(
            self, text="Selftests", command=self.selftest_button, width=10, height=2)
        selftest_button.grid(column=1, row=12, columnspan=2, padx=2, pady=5)
        selftest_button['font'] = button_font

        self.info_label = Label(
            self, background="white",
            foreground="blue",
            text="Info",
            cursor="hand2",
            font=font.Font(
                family="Arial", slant="italic", underline=1, size=10))
        self.info_label.grid(
            column=0, row=12, columnspan=3, sticky="WS", pady=10, padx=10)
        self.info_label.bind("<Button-1>", self.version_info)

        self.bottom_label = Label(
            self, textvariable=self.bottom_label_text)
        self.bottom_label.grid(
            column=0, row=13, columnspan=3, sticky="WS", padx=10)

        self.progressbar = ttk.Progressbar(
            self, orient="horizontal", mode="determinate")
        self.progressbar.grid(column=0, row=14, columnspan=4,
                              padx=10, pady=5, sticky="WE")

    def center_window(self):
        """setting up windopw in apx. middle of screen"""
        w = 450
        h = 615
        # get screen width and height
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen
        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2) - 75
        # set the dimensions of the screen
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.resizable(False, False)

    def build_tree(self):
        """build treeview containing lines, processes and stations"""
        self.tree = ttk.Treeview(self)
        self.tree.heading("#0", text="Line", anchor=tkinter.W)

        for line in shared.treedata:
            lineid = line
            self.tree.insert("", tkinter.END, text=line,
                             iid=lineid, open=False)
            for idx, process in enumerate(shared.treedata[line]):
                processid = (line, process)
                self.tree.insert(
                    "", tkinter.END, text=process, iid=processid, open=False)
                self.tree.move(processid, lineid, idx)
                for idy, station in enumerate(shared.treedata[line][process]["stations"]):
                    stationid = (line, process, idy)
                    self.tree.insert(
                        "", tkinter.END, text=station, iid=stationid, open=False)
                    self.tree.move(stationid, processid, idy)

        self.tree.grid(row=0, column=0, rowspan=13,
                       sticky="NS", pady=5, padx=5)

    def bottom_label_update(self, text):
        """update label above progress bar"""
        self.bottom_label_text.set("")
        self.bottom_label_text.set(text)
        self.update()

    def get_tree_data(self):
        """get user selection from treeview"""
        GuiMethods().load_json()
        if self.tree.focus() == "":
            self.update_idletasks()
            self.after(100, self.bottom_label_update("No Selection!"))
            return False
        shared.chosen_data = self.tree.focus().split(" ")
        try:
            self.data_depth = len(shared.chosen_data)
        except TypeError:
            return
        if self.data_depth <= 1:
            self.bottom_label_update("Select a process!")
            return False
        shared.date_from = self.cal_from.get_date().strftime("%Y%m%d")
        shared.date_to = self.cal_to.get_date().strftime("%Y%m%d")
        return True

    def do_popup(self, event):
        """Right click popup menu on treeview"""
        x_coordinate = event.x_root - self.winfo_rootx()
        y_coordinate = event.y_root - self.winfo_rooty()
        tree_row = self.tree.identify_row(event.y)
        tree_column = self.grid_location(x_coordinate, y_coordinate)[0]
        if tree_column == 0 and tree_row != "":
            self.tree.focus(tree_row)
            self.tree.selection_set(tree_row)
            try:
                data_length = len(self.tree.focus().split(" "))
                # check if there is upload option on processes,
                # if there is not, insert it into popup
                if data_length > 1 and self.popup.index("end") == 2:
                    self.popup.add_separator()
                    self.popup.add_command(
                        label="Upload database", command=self.upload_new_database)
                # check if click was not on process level,
                # if so delete upload option
                if data_length <= 1 and self.popup.index("end") > 2:
                    try:
                        self.popup.delete(3)
                        self.popup.delete("Upload database")
                    except tkinter.TclError:
                        pass
                self.popup.tk_popup(event.x_root + 39, event.y_root + 10, 0)
            finally:
                self.popup.grab_release()

    def double_click(self, event):
        """double click on parameter to start dbeditor"""
        x_coordinate = event.x_root - self.winfo_rootx()
        y_coordinate = event.y_root - self.winfo_rooty()
        tree_row = self.tree.identify_row(event.y)
        tree_column = self.grid_location(x_coordinate, y_coordinate)[0]
        if tree_column == 0 and tree_row != "":
            data_depth = len(self.tree.focus().split(" "))
            if data_depth > 1:
                self.tree.item(tree_row, open=False)
            self.dbeditor_button()

    def dbeditor_button(self):
        """start dbeditor with selected process"""
        if self.get_tree_data():
            DBEditor().ruestendaten(self)

    def results_button(self):
        self.bottom_label_update("")
        if self.get_tree_data():
            try:
                if self.combo.get() == "":
                    if len(shared.chosen_data) >= 1:
                        self.bottom_label_update("Select a Partnumber!")
                    return
                shared.partnumber = self.combo.get()
            except TypeError:
                return
            Merge().merge_button(self, "results")

    def errors_button(self):
        self.bottom_label_update("")
        GuiMethods().msgbox("Error", "This function does not work in the demo version.")

    def selftest_button(self):
        self.bottom_label_update("")
        GuiMethods().msgbox("Error", "This function does not work in the demo version.")

    def upload_new_database(self):
        if self.get_tree_data():
            filepath = filedialog.askopenfilename(
                title="Choose database to upload",
                filetypes=[("mdb", ".mdb .MDB")])
            filepath = filepath.replace("/", "\\")
            if not GuiMethods().sure(
                    title="Warning!",
                    message=f"Are you sure you want to upload this database to\
                        \n{shared.chosen_data[0]} {shared.chosen_data[1]}?",
                    icon="warning"):
                return
            DBEditor().upload_db(gui=self, file=filepath)

    def add_button(self):
        self.get_tree_data()
        self.bottom_label_update("")
        JsonEdit().edit("add")

    def edit_button(self):
        self.tryout = "asdasdasd"
        self.get_tree_data()
        self.bottom_label_update("")
        JsonEdit().edit("edit")
        GuiMethods().dump_json()

        self.tree.grid_forget()
        self.build_tree()

    def remove_button(self):
        self.get_tree_data()
        text = JsonEdit().remove()
        if not GuiMethods().sure(
                title="Warning!",
                message=f"Are you sure you want to delete {text}?",
                icon="warning"):
            return

        GuiMethods().dump_json()

        self.tree.grid_forget()
        self.build_tree()

    def open_mes(self):
        self.open_folder("MESlink")

    def open_bulk(self):
        self.open_folder("BSlink")

    def open_folder(self, link):
        data = self.tree.focus()
        if " " in data:
            data = data.split(" ")[0]
        if data:
            try:
                hostlink = shared.treedata[data][next(
                    iter(shared.treedata[data]))][link]
                GuiMethods().open_conn(hostlink)
                subprocess.Popen(f'explorer "{hostlink}"')
                GuiMethods().close_conn(hostlink)
                return
            except TypeError:
                return
        self.bottom_label_update("Select a line!")

    def fill_partnumbers(self, event):
        """fills partnumbers dropdown list from folders on bulk storage
            only triggers if a process is clicked on"""
        x_coordinate = event.x_root - self.winfo_rootx()
        y_coordinate = event.y_root - self.winfo_rooty()
        tree_row = self.tree.identify_row(event.y)
        tree_column = self.grid_location(x_coordinate, y_coordinate)[0]
        if tree_column == 0 and tree_row != "":
            if " " in self.tree.focus():
                data_depth = len(self.tree.focus().split(" "))
                if data_depth > 1:
                    self.get_tree_data()
                    self.partnumbers = []
                    process = shared.treedata[shared.chosen_data[0]
                                              ][shared.chosen_data[1]]
                    bulkpath = process["BSlink"]
                    station = next(iter(process["stations"]))
                    folders = glob.glob(
                        bulkpath + "\\" + station + "\\Data\\*\\", recursive=True)

                    for folder in folders:
                        pnr = folder[-10:-1]
                        if "Selftest" not in pnr:
                            self.partnumbers.append((folder[-11:-1]))
                    self.combo["values"] = self.partnumbers

    def version_info(self, event):
        GuiMethods().msgbox(
            title="Info",
            text="Process Cockpit\
                \n\nVersion: X.X.X\
                \nRelease date: XX.XX.XX\
                \n\nCreated by: Bence Luzsinszky"
        )


if __name__ == "__main__":
    freeze_support()
    gui = GuiMain()
    gui.mainloop()
