import tkinter
import shared
from tkinter import Entry, Label, Button
from gui_methods import GuiMethods, JSON


class JsonEdit(tkinter.Tk):  # TODO: ezt
    def __init__(self):
        self.dict = {}
        self.data_depth = len(shared.chosen_data)
        self.line_choice = shared.chosen_data[0]
        if self.data_depth > 1:
            self.process_choice = shared.chosen_data[1]

    def remove(self):
        if self.data_depth == 1:
            text = f"{self.line_choice} line"
            shared.treedata.pop(self.line_choice)
        elif self.data_depth == 2:
            text = (f"{self.process_choice} process\
                \nfrom {self.line_choice} line")
            shared.treedata[self.line_choice].pop(self.process_choice)
        elif self.data_depth > 2:
            stations = shared.treedata[self.line_choice][self.process_choice]["stations"]
            text = (
                f"{stations[int(shared.chosen_data[2])]} station\
                \nfrom {self.line_choice} - {self.process_choice} process")
            stations.pop(int(shared.chosen_data[2]))
        return text

    def edit(self, button):
        if button == "add":
            GuiMethods().errormsg(
                f"Add function currently under development.\
                \n\nPlease edit {JSON} instead."
            )
            return
        super().__init__()
        self.title("ITS Cockpit")
        self.iconbitmap(default="rooster.ico")
        self.eval('tk::PlaceWindow . center')
        max_columns = 4
        for i in range(max_columns):
            self.columnconfigure(i, weight=1)

        Label(self, text="Line: ").grid(column=0, row=1, sticky="W", padx=5, pady=5)
        self.line = Entry(self, width=50, text="asdasd")
        self.line.grid(column=1, row=1, padx=5, pady=5, columnspan=4)

        if self.data_depth > 1:
            Label(self, text="Process: ").grid(column=0, row=2, sticky="W", padx=5, pady=5)
            self.process = Entry(self, width=50)
            self.process.grid(column=1, row=2, padx=5, pady=5, columnspan=4)

        if self.data_depth > 2 or button == "add" and self.data_depth > 1:
            Label(self, text=".mdb file name: ").grid(column=0, row=3, sticky="W", padx=5, pady=5)
            self.mdb = Entry(self, width=50)
            self.mdb.grid(column=1, row=3, padx=5, pady=5, columnspan=4)

            Label(self, text="MES link: ").grid(column=0, row=4, sticky="W", padx=5, pady=5)
            self.mes = Entry(self, width=50)
            self.mes.grid(column=1, row=4, padx=5, pady=5, columnspan=4)

            Label(self, text="BS line link: ").grid(column=0, row=5, sticky="W", padx=5, pady=5)
            self.bulk = Entry(self, width=50)
            self.bulk.grid(column=1, row=5, padx=5, pady=5, columnspan=4)

            Label(self, text="BS .mdb link: ").grid(column=0, row=6, sticky="W", padx=5, pady=5)
            self.bulk_mdb = Entry(self, width=50)
            self.bulk_mdb.grid(column=1, row=6, padx=5, pady=5, columnspan=4)

            Label(self, text="Station: ").grid(column=0, row=7, sticky="W", padx=5, pady=5)
            self.station = Entry(self, width=50)
            self.station.grid(column=1, row=7, padx=5, pady=5, columnspan=4)

        save_button = Button(
            self,
            text="Save",
            width=10,
            command=lambda: self.save_button(button))
        save_button.grid(column=3, row=8, sticky="E", padx=10, pady=10)

        cancel_button = Button(
            self,
            text="Cancel",
            width=10,
            command=self.cancel_button)
        cancel_button.grid(column=4, row=8, sticky="W", padx=10, pady=10)

        if button == "edit":
            add_edit = "Edit Line:"
            self.line.insert(0, self.line_choice)
            if self.data_depth > 1:
                add_edit = "Edit Process:"
                self.process.insert(0, self.process_choice)
                self.line.config(state="readonly")
            if self.data_depth > 2:
                choice = shared.treedata[self.line_choice][self.process_choice]
                self.mdb.insert(0, choice["DB"])
                self.mes.insert(0, choice["MESlink"])
                self.bulk.insert(0, choice["BSlink"])
                self.bulk_mdb.insert(0, choice["BulkDB"])
                self.station.insert(0, choice["stations"])
                self.process.config(state="readonly")
        else:
            add_edit = "Add to ITS HUD:"
            if self.data_depth > 1:
                self.line.insert(0, self.line_choice)
                self.line.config(state="readonly")

        add_edit_var = tkinter.StringVar(self, add_edit)
        Label(self, textvariable=add_edit_var).grid(column=0, row=0, sticky="W", padx=5, pady=10)

        self.mainloop()

    def cancel_button(self):
        self.destroy()

    def save_button(self, button):
        if button == "edit":
            temp_dict = {}

            if self.data_depth == 1:
                for key in shared.treedata:
                    if key == self.line_choice:
                        temp_dict[self.line.get()] = shared.treedata[key]
                    else:
                        temp_dict[key] = shared.treedata[key]
                shared.treedata = temp_dict
            elif self.data_depth == 2:
                for key in shared.treedata[self.line_choice]:
                    if key == self.process_choice:
                        temp_dict[self.process.get()] = shared.treedata[self.line_choice][key]
                    else:
                        temp_dict[key] = shared.treedata[self.line_choice][key]
                shared.treedata[self.line_choice] = temp_dict
            elif self.data_depth > 2:
                data = {
                        "DB": self.mdb.get(),
                        "MESlink": self.mes.get(),
                        "BSlink": self.bulk.get(),
                        "BulkDB": self.bulk_mdb.get(),
                        "stations": self.station.get().split(" ")
                        }
                shared.treedata[self.line_choice].pop(
                    self.process_choice)
                shared.treedata[self.line_choice][self.process.get()] = data
            self.quit()
            self.withdraw()
            return
        if button == "add":
            if self.data_depth == 1:
                if self.line.get() in shared.treedata.keys():
                    text = self.line.get()
                    GuiMethods().errormsg(
                        f"Line '{text}' already exists.")
                    self.attributes('-topmost', True)
                    self.attributes('-topmost', False)
                else:
                    shared.treedata[self.line.get()] = {}
                    shared.chosen_data[0] = self.line.get()
                    self.data_depth = 2
                    self.quit()
                    self.withdraw()
                    self.edit("add")
            else:
                if self.line_choice and self.process.get() in shared.treedata[self.line_choice].keys():
                    text = self.process.get()
                    GuiMethods().errormsg(
                        f"Process '{text}' already exists.")
                    self.attributes('-topmost', True)
                    self.attributes('-topmost', False)
                else:
                    shared.treedata[self.line.get()][self.process.get()]
