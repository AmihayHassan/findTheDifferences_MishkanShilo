"""
find the differences in Mishkan Shilo - Shabbat newsletter
download the PDFs from here:
https://kav.meorot.net/category/%D7%A2%D7%9C%D7%95%D7%A0%D7%99-%D7%A9%D7%91%D7%AA/%D7%9E%D7%A9%D7%9B%D7%9F-%D7%A9%D7%99%D7%9C%D7%94/

author: Amihay Hassan
"""

import threading
import tkinter as tk
from tkinter import filedialog, colorchooser
from tkinter import ttk, messagebox

import fitz

import extract_images_from_pdf
import find_the_differences

TITLE_P1 = "מצא את ההבדלים"
TITLE_P2 = "©עמיחי חסן"


class FTD:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(TITLE_P1 + " " * 50 + TITLE_P2)
        self.root.geometry("500x250")
        self.root.resizable(False, False)

        self.document_path = tk.StringVar()
        self.short_path = tk.StringVar()
        self.document_path.trace("w", lambda *args: threading.Thread(target=self.short_path_and_pages_num).start())
        self.images_for_comparison = []
        self.page_number = tk.IntVar()
        self.page_number.trace("w", lambda *args: self.get_page_images())
        self.found_images_in_page = tk.StringVar()
        self.save_images = tk.BooleanVar()
        self.save_images.set(False)
        self.color_value_rgb = [0, 0, 0]

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        document_path_label = tk.Label(self.controls_frame,
                                       text="בחר את הקובץ")
        document_path_label.grid(row=0, column=2, sticky=tk.E, padx=10, pady=10)

        self.select_file_button = tk.Button(self.controls_frame,
                                            text="בחר קובץ",
                                            command=lambda: self.document_path.set(filedialog.askopenfilename()))
        self.select_file_button.grid(row=0, column=1, sticky=tk.E, padx=10, pady=10)

        document_path_label = tk.Label(self.controls_frame,
                                       textvariable=self.short_path,
                                       width=30)
        document_path_label.grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)

        progress_bar_label = tk.Label(self.controls_frame,
                                      text="התקדמות סריקה")
        progress_bar_label.grid(row=1, column=2, sticky=tk.E, padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(self.controls_frame,
                                            orient="horizontal",
                                            mode="determinate")
        self.progress_bar.grid(row=1, column=1, sticky=tk.E, padx=10, pady=10)

        self.progress_info = tk.Label(self.controls_frame,
                                      text="")
        self.progress_info.grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)

        self.color_pick_label = tk.Label(self.controls_frame, text="סמן הבדלים בצבע")
        self.color_pick_label.grid(row=3, column=2, sticky=tk.E, padx=10, pady=10)
        self.color_pick = tk.Button(self.controls_frame, text="בחר צבע", command=self.pick_color)
        self.color_pick.grid(row=3, column=1, sticky=tk.E, padx=10, pady=10)
        self.color_pick_frame = tk.Frame(self.controls_frame, bg="#000", width=30, height=30)
        self.color_pick_frame.grid(row=3, column=0, sticky=tk.E, padx=10, pady=10)

        self.compare_button = tk.Button(self.controls_frame,
                                        text="מצא את ההבדלים",
                                        command=self.compare_images,
                                        state="disabled")
        self.compare_button.grid(row=4, column=1, sticky=tk.E, padx=10, pady=10)
        self.save_images_checkbox = tk.Checkbutton(self.controls_frame, variable=self.save_images, text="שמור תמונות")
        self.save_images_checkbox.grid(row=4, column=0, sticky=tk.E, padx=10, pady=10)

        self.root.mainloop()

    def pick_color(self):
        color = colorchooser.askcolor()
        self.color_value_rgb = color[0]
        self.color_pick_frame.config(background=color[1])

    def short_path_and_pages_num(self):
        # make sure the file has a pdf extension
        if not self.document_path.get().endswith(".pdf"):
            self.short_path.set("can't open this file")
            return

        short_path_max_length = 40
        self.short_path.set("..." + self.document_path.get()[-short_path_max_length + 3:]
                            if len(self.document_path.get()) > short_path_max_length
                            else self.document_path.get())
        self.progress_bar.config(value=0)
        try:
            self.select_file_button.config(state="disabled")
            self.compare_button.config(state="disabled")
            extract_images_from_pdf.get_page_images(gui_app=self)

            self.compare_button.config(state="normal")
            self.select_file_button.config(state="normal")
        except Exception as e:
            print(e)

    def get_page_images(self):
        images = extract_images_from_pdf.get_page_images(self.document_path.get(), self.page_number.get())
        if len(images) == 0:
            self.found_images_in_page.set("לא נמצאו תמונות")
        else:
            self.found_images_in_page.set("נמצאו " + str(len(images)) + " תמונות להשוואה בדף זה")
        self.images_for_comparison = images

    def compare_images(self):
        if len(self.images_for_comparison) == 0:
            messagebox.showwarning("שגיאה", "לא נמצאו תמונות להשוואה")
            return
        find_the_differences.find_the_differences(img1=self.images_for_comparison[0],
                                                  img2=self.images_for_comparison[1],
                                                  resize=1.25,
                                                  color=self.color_value_rgb,
                                                  save=self.save_images.get())


def main():
    FTD()


if __name__ == "__main__":
    main()
