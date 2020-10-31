#!/usr/bin/env python3
import argparse
import sys
import tkinter
from os import mkdir, path, rename, scandir
from shutil import make_archive
from PIL import Image, ImageTk
import logging

class EntryWindow(tkinter.Frame):
    def __init__(self, master, input_dir="input/", output="./data/", image_type="png", logger = logging.getLogger("Captcha22 Label Typer")):
        super().__init__(master)
        self.logger = logger
        self.write_dir = output
        self.read_dir = input_dir
        self.file_type = image_type

        self.master = master
        self.pack(fill=tkinter.BOTH, expand=1)

        try:
            mkdir(self.write_dir)
        except FileExistsError:
            pass

        self.read_files(self.read_dir)
        if len(self.files) == 0:
            self.logger.info("No " + self.file_type + " files found")
            sys.exit(2)
        self.index = -1
        self.create_gui()
        self.update_image()

    def read_files(self, read_dir):
        self.files = []
        for file in scandir(read_dir):
            if (file.is_file and path.splitext(file.name)[1] == "." + self.file_type):
                self.files.append(path.normpath(
                    path.join(read_dir, file.name)))

    def close(self, event=None):
        self.master.destroy()
        return True

    def update_image(self):
        self.index += 1
        try:
            image = self.files[self.index]
        except IndexError:
            make_archive('data', 'zip', base_dir="data")
            return self.close()
        try:
            load = Image.open(image)
            render = ImageTk.PhotoImage(load, master=self)
        except Exception:
            self.logger.info("Could not open file:", image, file=sys.stderr)
            raise OSError
        self.image.configure(image=render)
        self.image.image = render
        return True

    def get_next(self, event=None):
        entry_value = self.entry.get() + "." + self.file_type
        rename(self.files[self.index], path.normpath(
            path.join(self.write_dir, entry_value)))
        self.files[self.index] = entry_value
        self.entry.delete(0, tkinter.END)
        self.update_image()

    def create_gui(self):
        self.master.bind("<Escape>", self.close)
        self.image = tkinter.Label(self, image=None)
        self.image.pack()
        self.entry = tkinter.Entry(self)
        self.entry.bind("<Return>", self.get_next)
        self.entry.pack()
        self.entry.focus()


def main():
    root = tkinter.Tk()
    entry_window = EntryWindow(root)
    root.title = "F-Secure Captcha Renamer"
    entry_window.mainloop()


if __name__ == "__main__":
    main()
