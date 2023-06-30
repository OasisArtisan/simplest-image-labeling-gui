"""
General simple labeling GUI

Requirements:
    - PIL
    
Usage Example:
    python main.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pathlib import Path
import math
from functools import partial
import json

# pip install pillow
from PIL import Image, ImageTk


class Main:
    supported_formats = {".jpg", ".jpeg", ".png"}
    label_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",  # TODO
                    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

    class GalleryItem:
        def __init__(self, frame, tk_img, label_bar):
            self.frame = frame
            self.tk_img = tk_img
            self.label_bar = label_bar
            self.labels = dict()

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("600x400")
        self.root.state('zoomed')
        self.root.title("LightLabel")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.path_frame = tk.Frame(self.main_frame)
        self.path_frame.pack(side=tk.TOP, fill=tk.X)

        self.path_label = tk.Label(self.path_frame, text="Working Directory: ")
        self.path_label.pack(side=tk.LEFT, padx=2)

        self.path_var = tk.StringVar()
        self.img_paths = None
        self.path_entry = tk.Entry(self.path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.path_entry.config(state="disabled")

        self.path_button = tk.Button(self.path_frame, text="Browse", command=self.browse)
        self.path_button.pack(side=tk.LEFT, padx=5)

        self.path_imgs_label = tk.Label(self.path_frame, text="# imgs:")
        self.path_imgs_label.pack(side=tk.LEFT, padx=5)

        self.path_imgs_var = tk.IntVar()
        self.path_imgs_entry = tk.Entry(self.path_frame, width=8, textvariable=self.path_imgs_var)
        self.path_imgs_entry.pack(side=tk.LEFT, padx=5)
        self.path_imgs_entry.config(state="disabled")

        self.label_frame = tk.Frame(self.main_frame)
        self.label_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.label_var = tk.StringVar()
        self.label_label = tk.Label(self.label_frame, text="LLabel:")
        self.label_label.pack(side=tk.LEFT, padx=2)
        self.label_entry = tk.Entry(self.label_frame, width=20, textvariable=self.label_var)
        self.label_entry.pack(side=tk.LEFT, padx=5)

        self.rlabel_var = tk.StringVar()
        self.rlabel_label = tk.Label(self.label_frame, text="RLabel:")
        self.rlabel_label.pack(side=tk.LEFT, padx=2)
        self.rlabel_entry = tk.Entry(self.label_frame, width=20, textvariable=self.rlabel_var)
        self.rlabel_entry.pack(side=tk.LEFT, padx=5)

        self.rows_var = tk.IntVar(value=3)
        self.rows_label = tk.Label(self.label_frame, text="# Rows:")
        self.rows_label.pack(side=tk.LEFT, padx=2)
        self.rows_entry = tk.Entry(self.label_frame, width=6, textvariable=self.rows_var)
        self.rows_entry.pack(side=tk.LEFT, padx=5)

        self.cols_var = tk.IntVar(value=4)
        self.cols_label = tk.Label(self.label_frame, text="# Cols:")
        self.cols_label.pack(side=tk.LEFT, padx=2)
        self.cols_entry = tk.Entry(self.label_frame, width=6, textvariable=self.cols_var)
        self.cols_entry.pack(side=tk.LEFT, padx=5)
        self.refresh_button = tk.Button(self.label_frame, text="Refresh", command=self.refresh_gallery)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.gallery_frame = tk.Frame(self.main_frame, bg="white")
        self.gallery_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        self.gallery_item_buffer = dict()

        self.navigation_frame = tk.Frame(self.main_frame)
        self.navigation_frame.pack(side=tk.TOP, fill=tk.X)
        self.next_button = tk.Button(self.navigation_frame, text="Next", command=self.next)
        self.next_button.pack(side=tk.RIGHT, padx=5)
        self.prev_button = tk.Button(self.navigation_frame, text="Prev", command=self.prev)
        self.prev_button.pack(side=tk.RIGHT, padx=5)

        self.total_pages_var = tk.IntVar(value=1)
        self.total_pages_entry = tk.Entry(self.navigation_frame, width=6, textvariable=self.total_pages_var)
        self.total_pages_entry.config(state="disabled")
        self.total_pages_entry.pack(side=tk.RIGHT, padx=5)

        tk.Label(self.navigation_frame, text="/").pack(side=tk.RIGHT)

        self.page_var = tk.IntVar(value=1)
        self.page_entry = tk.Entry(self.navigation_frame, width=6, textvariable=self.page_var)
        self.page_entry.pack(side=tk.RIGHT, padx=5)
        self.page_entry.bind("<FocusOut>", self.set_page)
        self.page_entry.bind("<Return>", self.set_page)

        self.page_label = tk.Label(self.navigation_frame, text="Page:")
        self.page_label.pack(side=tk.RIGHT, padx=5)

        self.labels = dict()

    def save(self):
        if not self.path_var.get():
            return
        saved_labels_path = os.path.join(self.path_var.get(), "labels.json")
        with open(saved_labels_path, "w") as f:
            json.dump(self.labels, f, indent=4)

    def load(self):
        if not self.path_var.get():
            return
        saved_labels_path = os.path.join(self.path_var.get(), "labels.json")
        if os.path.isfile(saved_labels_path):
            try:
                with open(saved_labels_path) as f:
                    self.labels = json.load(f)
                    num_labels = sum([len(x) for x in self.labels.values()])
                    messagebox.showinfo(title="Labels found",
                                        message=f"{num_labels} Existing labels loaded from {saved_labels_path}")
            except Exception as e:
                ans = messagebox.askyesno(title="Exception",
                                          message=f"The labels file {saved_labels_path} seems to be corrupted.\n"
                                                  f"The program encountered this exception:\n{str(e)}.\n"
                                                  f"Would you like to overwrite it and continue?")
                if ans:
                    os.remove(saved_labels_path)
                else:
                    exit(1)

    def label(self, img_path, event=None):
        if event:
            l = self.label_var.get() if event.num == 1 else self.rlabel_var.get()
        else:
            l = self.label_var.get()
        if not l:
            return
        l = l.lower()
        if img_path in self.labels.keys():
            if l in self.labels[img_path]:
                return
            self.labels[img_path].append(l)
        else:
            self.labels[img_path] = [l]

        gi = self.gallery_item_buffer[img_path]
        cmd = partial(self.remove_label, img_path, l)
        label_btn = tk.Button(gi.label_bar, text=l, bg="#1ee131", fg="white", command=cmd)
        label_btn.pack(side=tk.LEFT)
        gi.labels[l] = label_btn
        self.save()

    def remove_label(self, img_path, label, event=None):
        gi = self.gallery_item_buffer[img_path]
        gi.labels[label].destroy()
        del gi.labels[label]
        self.labels[img_path].remove(label)
        self.save()

    def refresh_gallery(self, event=None):
        if not self.img_paths:
            return
        page = self.page_var.get()-1
        pics_per_image = self.rows_var.get() * self.cols_var.get()
        imgs = self.img_paths[page*pics_per_image: (page+1)*pics_per_image]
        total_pages = math.ceil(len(self.img_paths) / pics_per_image)
        self.total_pages_var.set(total_pages)
        page = min(self.total_pages_var.get(), max(1, self.page_var.get()))
        self.page_var.set(page)

        pad = 5
        pads_w = self.cols_var.get()*pad*2
        pads_h = self.rows_var.get()*pad*2

        img_w = (self.gallery_frame.winfo_width()-pads_w) // self.cols_var.get()
        img_h = (self.gallery_frame.winfo_height()-pads_h) // self.rows_var.get()
        for c in self.gallery_frame.winfo_children():
            c.destroy()
        self.gallery_item_buffer.clear()

        for i, img_path in enumerate(imgs):
            c = i % self.cols_var.get()
            r = i // self.cols_var.get()
            if img_path in self.labels.keys():
                labels = self.labels[img_path]
            else:
                labels = list()
            item_bg_clr = "#0067ff"
            item = tk.Frame(self.gallery_frame, width=img_w, bg=item_bg_clr, height=img_h)
            item.grid(row=r, column=c, padx=5, pady=5, sticky="WENS")
            pil_img = Image.open(img_path)
            h_ratio = img_h/pil_img.height
            w_ratio = img_w/pil_img.width
            ratio = min(w_ratio, h_ratio)
            h = int(pil_img.height*ratio)
            w = int(pil_img.width*ratio)
            pil_img = pil_img.resize(size=(w, h))
            tk_img = ImageTk.PhotoImage(pil_img)
            img_control = tk.Label(item, image=tk_img, bg=item_bg_clr)
            cmd = partial(self.label, img_path)
            img_control.bind("<Button-1>", cmd)
            img_control.bind("<Button-3>", cmd)
            img_control.place(relx=0.5, rely=0.5, relheight=0.97, relwidth=0.97, anchor=tk.CENTER)
            label_bar = tk.Frame(item)
            label_bar.place(x=0, y=0)
            gi = Main.GalleryItem(item, tk_img, label_bar)
            for j, l in enumerate(sorted(labels)):
                cmd = partial(self.remove_label, img_path, l)
                label_btn = tk.Button(label_bar, text=l, bg="#1ee131", fg="white", command=cmd)
                label_btn.pack(side=tk.LEFT)
                gi.labels[l] = label_btn

            self.gallery_item_buffer[img_path] = gi

    def browse(self):
        directory = filedialog.askdirectory()
        if not directory:
            return
        try:
            img_paths = [str(x) for x in (p.resolve() for p in Path(directory).glob("**/*")
                         if p.suffix in Main.supported_formats)]
            img_paths.sort()
            ans = messagebox.askokcancel(title=None, message=f"Found {len(img_paths)} supported images. Continue?")
            if ans:
                self.img_paths = img_paths
                self.path_var.set(directory)
                self.path_imgs_var.set(len(img_paths))
                self.page_var.set(1)
                pics_per_image = self.rows_var.get() * self.cols_var.get()
                total_pages = math.ceil(len(img_paths) / pics_per_image)
                self.total_pages_var.set(total_pages)
                self.load()
        except Exception as e:
            messagebox.showerror(title="Exception", message=str(e))
            return

        self.refresh_gallery()

    def next(self):
        self.page_var.set(min(self.total_pages_var.get(), self.page_var.get()+1))
        self.refresh_gallery()

    def prev(self):
        self.page_var.set(max(1, self.page_var.get()-1))
        self.refresh_gallery()

    def set_page(self, event=None):
        page = min(self.total_pages_var.get(), max(1, self.page_var.get()))
        self.page_var.set(page)
        self.refresh_gallery()

    def wait(self):
        self.root.mainloop()


if __name__ == "__main__":
    main = Main()
    main.wait()
