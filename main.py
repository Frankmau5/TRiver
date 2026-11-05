#!/usr/bin/env python3

import argparse
import datetime
import json
import os
try:
    import tkinter
    from tkinter import filedialog as fd
    from tkinter import messagebox as mb
except ImportError:
    tkinter = None
    fd = None
    mb = None

import humanize
import torrent_parser as tp

PLACEHOLDER_TEXT = "Please open a torrent file to view the metadata."
ABOUT_TEXT = (
    "TRiver - version 1.1.0\n"
    "Author: Frank Mulvie\n"
    "GitHub: https://github.com/Frankmau5/TRiver"
)
TORRENT_FILETYPES = [("Torrent files", "*.torrent"), ("All files", "*.*")]


class Win_ui:
    def __init__(self, initial_file=None):
        self.window = tkinter.Tk()
        self.window.title("TRiver")
        self.window.geometry("800x600")
        self.tr_backend = TRiver_Backend()
        self.file_loaded = False

        m = self.mk_menu()
        self.window.config(menu=m)
        self.mk_text()
        self.bind_shortcuts()

        if initial_file:
            self.load_torrent_file(initial_file)

        self.window.mainloop()

    def mk_menu(self):
        menu_bar = tkinter.Menu(self.window)
        filem = tkinter.Menu(menu_bar, tearoff=0)
        filem.add_command(label="Open", accelerator="Ctrl+O", command=self.on_open)
        filem.add_command(label="Save As", accelerator="Ctrl+S", command=self.save_as)
        filem.add_separator()
        filem.add_command(label="Exit", accelerator="Ctrl+Q", command=self.on_exit)

        aboutm = tkinter.Menu(menu_bar, tearoff=0)
        aboutm.add_command(label="About", command=self.on_about)

        menu_bar.add_cascade(label="File", menu=filem)
        menu_bar.add_cascade(label="About", menu=aboutm)
        return menu_bar

    def mk_text(self):
        scrollbar = tkinter.Scrollbar(self.window, orient="vertical")
        scrollbar.pack(side=tkinter.RIGHT, fill="y")

        self.t = tkinter.Text(self.window, yscrollcommand=scrollbar.set)
        self.t.insert(tkinter.INSERT, PLACEHOLDER_TEXT)
        self.t.config(state=tkinter.DISABLED)  # Read-Only until a file is opened
        self.t.pack(expand=True, fill=tkinter.BOTH)
        scrollbar.config(command=self.t.yview)

    def bind_shortcuts(self):
        self.window.bind("<Control-o>", lambda _event: self.on_open())
        self.window.bind("<Control-s>", lambda _event: self.save_as())
        self.window.bind("<Control-q>", lambda _event: self.on_exit())

    def on_exit(self):
        self.window.destroy()

    def save_as(self):
        if not self.file_loaded:
            mb.showwarning("No Torrent Loaded", "Please open a torrent file before saving.")
            return

        my_json_str = self.t.get("1.0", tkinter.END).strip()
        try:
            json_dict = json.loads(my_json_str)
        except json.JSONDecodeError as err:
            mb.showerror("Invalid JSON", f"Cannot save torrent because the JSON is invalid:\n{err}")
            return

        name = fd.asksaveasfilename(
            defaultextension=".torrent",
            filetypes=TORRENT_FILETYPES,
        )
        if not name:
            return

        if not name.lower().endswith(".torrent"):
            name = f"{name}.torrent"

        try:
            tp.create_torrent_file(name, json_dict)
        except Exception as err:
            mb.showerror("Save Error", f"Failed to save torrent file:\n{err}")

    def on_about(self):
        mb.showinfo("About", ABOUT_TEXT)

    def load_torrent_file(self, name):
        try:
            data = self.tr_backend.get_torrent_json(name)
        except Exception as err:
            mb.showerror("Open Error", f"Failed to open torrent file:\n{err}")
            return

        self.t.config(state=tkinter.NORMAL)
        self.t.delete("1.0", tkinter.END)
        self.t.insert(tkinter.INSERT, data)
        self.file_loaded = True
        self.window.title(f"TRiver - {os.path.basename(name)}")

    def on_open(self):
        name = fd.askopenfilename(filetypes=TORRENT_FILETYPES)
        if not name:
            return
        self.load_torrent_file(name)

    def format_data_str(self, data):
        formatted_str = ""
        for item in data:
            for key in item:
                formatted_str = f"{formatted_str} {key} : {item[key]}\n"
        return formatted_str

    # Keep backwards-compatible alias
    FormatDataStr = format_data_str


class Flet_ui:
    def __init__(self, initial_file=None):
        import flet as ft

        self.ft = ft
        self.tr_backend = TRiver_Backend()
        self.file_loaded = False
        self.initial_file = initial_file
        ft.run(self.build)

    def build(self, page):
        ft = self.ft
        page.title = "TRiver"
        page.window.width = 800
        page.window.height = 600

        file_picker = ft.FilePicker()

        editor = ft.TextField(
            value=PLACEHOLDER_TEXT,
            multiline=True,
            read_only=True,
            expand=True,
            min_lines=20,
            text_style=ft.TextStyle(font_family="monospace"),
        )

        def show_message(title, message):
            dialog = ft.AlertDialog(
                title=ft.Text(title),
                content=ft.Text(message, selectable=True),
                actions=[
                    ft.TextButton("OK", on_click=lambda _e: page.pop_dialog()),
                ],
            )
            page.show_dialog(dialog)

        def load_torrent_file(filepath):
            try:
                data = self.tr_backend.get_torrent_json(filepath)
            except Exception as err:
                show_message("Open Error", f"Failed to open torrent file:\n{err}")
                return

            editor.value = data
            editor.read_only = False
            self.file_loaded = True
            page.title = f"TRiver - {os.path.basename(filepath)}"
            page.update()

        async def on_open(_e=None):
            files = await file_picker.pick_files(
                dialog_title="Open Torrent File",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["torrent"],
            )
            if not files or not files[0].path:
                return
            load_torrent_file(files[0].path)

        async def on_save_as(_e=None):
            if not self.file_loaded:
                show_message("No Torrent Loaded", "Please open a torrent file before saving.")
                return

            my_json_str = (editor.value or "").strip()
            try:
                json_dict = json.loads(my_json_str)
            except json.JSONDecodeError as err:
                show_message("Invalid JSON", f"Cannot save torrent because the JSON is invalid:\n{err}")
                return

            save_path = await file_picker.save_file(
                dialog_title="Save Torrent File As",
                file_name="output.torrent",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["torrent"],
            )
            if not save_path:
                return

            if not save_path.lower().endswith(".torrent"):
                save_path = f"{save_path}.torrent"

            try:
                tp.create_torrent_file(save_path, json_dict)
            except Exception as err:
                show_message("Save Error", f"Failed to save torrent file:\n{err}")

        def on_about(_e=None):
            show_message("About", ABOUT_TEXT)

        async def on_exit(_e=None):
            await page.window.close()

        menu_bar = ft.MenuBar(
            expand=True,
            controls=[
                ft.SubmenuButton(
                    content=ft.Text("File"),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Open"),
                            leading=ft.Icon(ft.Icons.FOLDER_OPEN),
                            on_click=on_open,
                        ),
                        ft.MenuItemButton(
                            content=ft.Text("Save As"),
                            leading=ft.Icon(ft.Icons.SAVE),
                            on_click=on_save_as,
                        ),
                        ft.MenuItemButton(
                            content=ft.Text("Exit"),
                            leading=ft.Icon(ft.Icons.EXIT_TO_APP),
                            on_click=on_exit,
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text("About"),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("About"),
                            leading=ft.Icon(ft.Icons.INFO_OUTLINE),
                            on_click=on_about,
                        ),
                    ],
                ),
            ],
        )

        page.add(
            ft.Row([menu_bar]),
            editor,
        )

        if self.initial_file:
            load_torrent_file(self.initial_file)


class TRiver_Backend:
    def __init__(self):
        self.data = None

    def get_torrent_json(self, filepath):
        self.data = tp.parse_torrent_file(filepath)
        return json.dumps(self.data, indent=4)

    # Keep backwards-compatible alias
    GetTorrentData = get_torrent_json

    def get_torrent_data(self, filepath):
        self.data = tp.parse_torrent_file(filepath)
        text = ""

        for key, value in self.data.items():
            if key == "creation date":
                try:
                    dt = datetime.date.fromtimestamp(value)
                    text += f"{key} = {dt}\n\n"
                    continue
                except (OverflowError, OSError, TypeError, ValueError) as err:
                    print(str(err))

            if key == "announce-list":
                text += f"{key} = "
                for tier in value:
                    for tracker in tier:
                        text += f"{tracker} ,\n"
                text += "\n\n"
                continue

            if key == "info":
                if "files" in value:
                    text += "Files =\n"
                    for file_info in value["files"]:
                        size_str = self.human_readable_size(file_info["length"])
                        path_str = "/".join(str(p) for p in file_info["path"])
                        text += f"Size : {size_str} , Filename : {path_str}\n"
                else:
                    if "name" in value:
                        text += f"File = {value['name']}\n"
                    if "length" in value:
                        size_str = self.human_readable_size(value["length"])
                        text += f"Size : {size_str}\n"
                text += "\n"
                continue

            if key == "nodes":
                text += f"{key} = "
                for node in value:
                    text += f"{node[0]}:{node[1]} , "
                text += "\n\n"
                continue

            text += f"{key} = {value}\n\n"

        return text

    def human_readable_size(self, byte_size):
        return humanize.naturalsize(byte_size, gnu=True)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="TRiver (Torrent River) - Torrent metadata viewer and editor."
    )
    parser.add_argument(
        "--flet",
        action="store_true",
        help="Use Flet as the GUI instead of Tkinter.",
    )
    parser.add_argument(
        "-f",
        "--file",
        dest="file",
        metavar="FILE",
        help="Path to a .torrent file to open on startup.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.flet:
        Flet_ui(initial_file=args.file)
    else:
        Win_ui(initial_file=args.file)


if __name__ == "__main__":
    main()



