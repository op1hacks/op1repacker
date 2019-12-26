#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""GUI for op1repacker."""


import os
import tkinter
from tkinter import ttk
from op1repacker.main import unpack, repack, modify
from op1repacker import op1_repack
from tkinter import filedialog, messagebox
from pathlib import Path

modifications = [
    {
        "id": "iter",
        "name": "Enable ITER",
        "descr": "Enable the hidden ITER synth",
        "enabled": 0,
    },
    {
        "id": "presets-iter",
        "name": "Enable ITER Presets",
        "descr": "Add community presets from op1.fun to the ITER synth",
        "enabled": 0,
    },
    {
        "id": "filter",
        "name": "Enable FILTER",
        "descr": "Enable the hidden filter effect",
        "enabled": 0,
    },
    {
        "id": "subtle-fx",
        "name": "Enable Subtle FX Defaults",
        "descr": "Lower the default intensity of effects. This allows you to turn effects on without affecting the sound too much. You can then turn them up as you like. This helps with live performances and avoids a sudden change to the sound when an effect is enabled.",
        "enabled": 0,
    },
    {
        "id": "gfx-iter-lab",
        "name": "Add ITER Graphics",
        "descr": "Add custom lab themed visuals to the ITER synth.",
        "enabled": 0,
    },
    {
        "id": "gfx-tape-invert",
        "name": "Invert Tape Track Position",
        "descr": "Move the tracks to the top of the tape screen to make them much easier to see at certain angles.",
        "enabled": 0,
    },
    {
        "id": "gfx-cwo-moose",
        "name": "Enable Moose Graphics",
        "descr": "Swap the cow in the CWO effect with a moose, because why not.",
        "enabled": 0,
    },
]

# Global Styles and Colors
style = {
    "scale": 1,
    "window": {
        "bg": "#010101",  # OP-1 Black
        "fg": "#DFD9FF",
    },
    "color": {
        "blue": {"light": "#698EFF", "dark": "#383572"},
        "green": {"light": "#00ED95", "dark": "#00475B"},
        "white": {"light": "#DFD9FF", "dark": "#656579"},
        "red": {"light": "#FF3A5D", "dark": "#512132"},
    },
    "font": "monospace",
    "relief": tkinter.FLAT,
    "border-width": 2,
}


def default_attributes(**attr):
    defaults = {
        "background": style["window"]["bg"],
        "relief": style["relief"],
    }
    for key, value in attr.items():
        defaults[key] = value
    return defaults


def default_attributes_label(**attr):
    defaults = default_attributes(
        foreground=style["window"]["fg"],
        font=style["font"],
    )
    for key, value in attr.items():
        defaults[key] = value
    return defaults


class AnimatedCanvas:
    # TODO: Make this a loading spinner
    def __init__(self, parent, state=0, label=""):
        self.parent = parent
        self.width = 50
        self.height = 50
        self.pad = 0

        self.widget = tkinter.Canvas(
            self.parent,
            width=self.width,
            height=self.height,
            background=style["window"]["bg"]
        )

        self.border = self.widget.create_rectangle(
            2+self.pad,
            2+self.pad,
            self.width-self.pad,
            self.height-self.pad,
            outline=style["color"]["blue"]["light"],
            width=style["border-width"],
        )

        self.update()

    def update(self):
        self.pad += 1

        if self.pad > self.width:
            self.pad = 0

        self.widget.coords(
            self.border,
            self.pad+2,
            self.pad+2,
            self.width-self.pad,
            self.height-self.pad
        )

        self.parent.after(9, self.update)


class CustomCheckbox:
    def __init__(self, parent, state=0, label=""):
        self.parent = parent
        self.state = state
        self.width = 28 * style["scale"]
        self.height = 28 * style["scale"]
        self.padding = 5
        self.color = "green"
        self.state_to_shade = ["dark", "light"]
        self.on_change = None

        self.widget = tkinter.Frame(
            parent,
            relief=tkinter.SUNKEN,
            background=style["window"]["bg"],
            padx=0,
            pady=5*style["scale"],
        )

        self.canvas = tkinter.Canvas(
            self.widget,
            width=self.width,
            height=self.height,
            borderwidth=0,
            highlightthickness=0,
            background=style["window"]["bg"]
        )

        # Border
        self.check_border = self.canvas.create_rectangle(
            1,
            1,
            self.width-1,
            self.height-1,
            outline=style["color"][self.color]["light"],
            width=style["border-width"],
        )

        # Square check mark
        self.check_rectangle = self.canvas.create_rectangle(
            self.padding,
            self.padding,
            self.width-self.padding-1,
            self.height-self.padding-1,
            fill=self.get_current_color(),
        )

        self.label = tkinter.Label(
            self.widget,
            text=label,
            wraplength=400,
            justify=tkinter.LEFT,
            padx=9*style["scale"],
            background=style["window"]["bg"],
            foreground=style["color"]["green"]["light"],
            font=style["font"],
        )

        self.widget.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-1>", self.on_click)
        self.label.bind("<Button-1>", self.on_click)

        self.canvas.grid(row=0, column=0, sticky="NW")
        self.label.grid(row=0, column=1, sticky="W")

    def get_current_color(self):
        return style["color"][self.color][self.state_to_shade[self.state]]

    def set_state(self, state):
        self.state = state

        self.canvas.itemconfig(self.check_border, outline=style["color"][self.color]["light"])
        self.canvas.itemconfig(self.check_rectangle, fill=self.get_current_color())
        self.trigger_changed()

    def toggle(self):
        self.set_state(not self.state)

    def on_click(self, event):
        self.set_state(not self.state)

    def on_enter(self, event):
        self.canvas.itemconfig(self.check_border, outline=style["color"][self.color]["light"])

    def on_leave(self, event):
        self.canvas.itemconfig(self.check_border, outline=style["color"][self.color]["dark"])

    def trigger_changed(self):
        if self.on_change:
            self.on_change(self.state)


class MainWindow(tkinter.Tk):
    def __init__(self, master=None):
        tkinter.Tk.__init__(self, master)
        self.window_title = "OP-1 Repacker"

        self.height = 600
        self.width = 700

        self._offsetx = 0
        self._offsety = 0

        self.target_file_path = None

        self.create_fw_button_text = tkinter.StringVar()
        self.create_fw_button_text.set("Create Custom FW")


        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("my.TButton", bordercolor="red")

    def dragwin(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry('+{x}+{y}'.format(x=x, y=y))

    def clickwin(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def initialize_scaling(self):
        # Roughly determine the GUI scale based on font size
        # This is used to scale our canvas based custom GUI elements
        default_height = 19
        self.label = tkinter.Label(
            self,
            text="M",
            pady=0,
            padx=0,
        )
        self.label.pack()
        self.label.update()
        current_height = self.label.winfo_height()
        self.label.destroy()
        scale = current_height / default_height
        scale = 1
        style["scale"] = scale
        print("GUI Scale: " + str(scale))

    def center_window(self):
        self.geometry("")
        self.update()
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))

        self.geometry("{}x{}+{}+{}".format(
            window_width,
            window_height,
            x_cordinate,
            y_cordinate
        ))

    def bind_keys(self):
        self.bind("<Escape>", self.exit)
        self.bind("<Control-q>", self.exit)

    def run(self):
        self.title(self.window_title)
        self.configure(
            background=style["window"]["bg"],
            # highlightcolor="cyan",
        )
        self.initialize_scaling()

        self.bind_keys()
        self.setup_window()
        self.center_window()
        self.mainloop()

    def exit(self, event=None):
        self.destroy()

    def setup_window(self):
        root_frame = tkinter.Frame(
            self,
            **default_attributes(
                padx=10*style["scale"],
                pady=10*style["scale"],
            ),
        )

        main_frame = tkinter.Frame(
            root_frame,
            relief=style["relief"],
            background=style["window"]["bg"],
        )

        # Step 1
        step_1_container = tkinter.Frame(
            main_frame,
            **default_attributes(
                padx=10*style["scale"],
                pady=10*style["scale"],
            )
        )
        step_1_container.grid(row=0, column=0, sticky="NWE")
        select_file_button = ttk.Button(
            step_1_container,
            text="Select Firmware File",
            command=self.select_file,
            #background=style["window"]["bg"],
            #foreground=style["color"]["white"]["light"],
            #activeforeground=style["color"]["white"]["light"],
            #activebackground=style["color"]["white"]["dark"],
            #highlightcolor=style["color"]["white"]["light"],
            #highlightbackground=style["color"]["white"]["light"],
            #highlightthickness=style["border-width"],
            #bd=2,
            #font=style["font"],
            #bordercolor="red",
            #relief=style["relief"],
            style="my.TButton"
        )
        select_file_button.pack(fill=tkinter.X, pady=5)
        self.target_label = tkinter.Label(
            step_1_container,
            text="No File Selected",
            justify=tkinter.CENTER,
            **default_attributes_label(
            )
        )
        self.target_label.pack(fill=tkinter.X, pady=5)

        # Step 2
        step_2_container = tkinter.Frame(
            main_frame,
            relief=style["relief"],
            background=style["window"]["bg"],
            padx=10*style["scale"],
            pady=10*style["scale"],
        )
        step_2_container.grid(row=1, column=0, sticky="N")

        checboxes = self.setup_mod_selector(step_2_container)
        checboxes.pack(fill=tkinter.X, pady=5)

        # test = AnimatedCanvas(main_frame)
        # test.widget.pack()

        step_3_container = tkinter.Frame(
            main_frame,
            relief=style["relief"],
            background=style["window"]["bg"],
            padx=10*style["scale"],
            pady=10*style["scale"],
        )
        step_3_container.grid(row=2, column=0, sticky="NWE")

        self.create_fw_button = tkinter.Button(
            step_3_container,
            textvariable=self.create_fw_button_text,
            command=self.run_repacker,
            background=style["window"]["bg"],
            foreground=style["color"]["green"]["light"],
            activeforeground=style["color"]["green"]["light"],
            activebackground=style["color"]["green"]["dark"],
            highlightcolor=style["color"]["green"]["light"],
            highlightbackground=style["color"]["green"]["light"],
            highlightthickness=style["border-width"],
            font=style["font"],
            relief=style["relief"],
        )

        self.create_fw_button.pack(
            fill=tkinter.X,
            pady=5,
        )

        exit_button = tkinter.Button(
            step_3_container, text="Exit", command=self.exit,
            background=style["window"]["bg"],
            foreground=style["color"]["red"]["light"],
            activeforeground=style["color"]["red"]["light"],
            activebackground=style["color"]["red"]["dark"],
            highlightcolor=style["color"]["red"]["light"],
            highlightbackground=style["color"]["red"]["light"],
            highlightthickness=style["border-width"],
            font=style["font"],
            relief=style["relief"],
        )

        exit_button.pack(
            fill=tkinter.X,
            pady=5,
        )

        main_frame.pack(side=tkinter.RIGHT)
        root_frame.pack()

    def setup_mod_selector(self, parent):
        checkbox_frame = tkinter.Frame(
            parent,
            relief=style["relief"],
            background=style["window"]["bg"],
            pady=0,
        )

        def set_value(index, value):
            modifications[index]["enabled"] = value

        row = 0
        for mod in modifications:
            c = CustomCheckbox(checkbox_frame, state=int(mod["enabled"]), label=mod["name"])
            c.widget.grid(row=row, column=0, sticky="NW")
            c.on_change = (lambda row: (
                lambda value: (set_value(row, value))
            ))(row)
            row += 1
        return checkbox_frame

    def set_target_file(self, path):
        self.target_file_path = path

    def select_file(self):
        home = str(Path.home())
        path = filedialog.askopenfilename(
            initialdir=home,
            title="Select an OP-1 firmware to modify",
            filetypes=(("OP-1 Firmware Files", "*.op1"),)
        )

        if not path:
            # Bail out
            return

        self.target_file_path = path
        name = os.path.basename(os.path.normpath(path))
        self.target_label.config(text="Selected: " + name)
        self.create_fw_button.config(state=tkinter.NORMAL)
        # TODO: store the path

    def run_repacker(self):
        if not self.target_file_path:
            messagebox.showwarning(
                "Choose file",
                "Choose an original firmware file first!"
            )
            return

        repacker = op1_repack.OP1Repack(debug=True)
        target_file = self.target_file_path
        target_folder = os.path.splitext(target_file)[0]

        mods = list(map(lambda m: m["id"], filter(lambda m: m["enabled"], modifications)))

        self.create_fw_button.config(state=tkinter.DISABLED)
        self.create_fw_button_text.set("Working...")
        self.update()

        # TODO: run in thread
        unpack(repacker, target_file)
        modify(repacker, target_folder, mods)
        repack(repacker, target_folder)

        self.create_fw_button_text.set("Done!")
        self.create_fw_button.config(state=tkinter.NORMAL)
        print("READY!")


if __name__ == "__main__":
    win = MainWindow()
    win.run()
