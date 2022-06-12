"""
find the differences in Mishkan Shilo - Shabbat newsletter
download the PDFs from here:
https://kav.meorot.net/category/%D7%A2%D7%9C%D7%95%D7%A0%D7%99-%D7%A9%D7%91%D7%AA/%D7%9E%D7%A9%D7%9B%D7%9F-%D7%A9%D7%99%D7%9C%D7%94/

author: Amihay Hassan
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import fitz
import threading

import extract_images_from_pdf
import find_the_differences

TITLE_P1 = "מצא את ההבדלים"
TITLE_P2 = "©עמיחי חסן"


class FTD:
    def __init__(self, master):
        self.root = tk.Tk()
        self.root.title(TITLE_P1 + " " * 50 + TITLE_P2)
        self.root.geometry("600x150")
        self.root.resizable(False, False)

        self.document_path = tk.StringVar()
        self.short_path = tk.StringVar()
        self.document_path.trace("w", lambda *args: threading.Thread(target=self.short_path_and_pages_num).start())
        self.images_for_comparison = []
        self.page_number = tk.IntVar()
        self.found_images_in_page = tk.StringVar()

        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        document_path_label = tk.Label(self.controls_frame, text="בחר את הקובץ")
        document_path_label.grid(row=0, column=2, sticky=tk.E, padx=10, pady=10)

        button = tk.Button(self.controls_frame, text="בחר קובץ",
                           command=lambda: self.document_path.set(filedialog.askopenfilename()))
        button.grid(row=0, column=1, sticky=tk.E, padx=10, pady=10)

        document_path_label = tk.Label(self.controls_frame, textvariable=self.short_path)
        document_path_label.grid(row=0, column=0, sticky=tk.E, padx=10, pady=10)

        page_number_label = tk.Label(self.controls_frame, text="בחר מספר דף")
        page_number_label.grid(row=1, column=2, sticky=tk.E, padx=10, pady=10)
        self.page_number.trace("w", lambda *args: self.get_page_images())
        self.page_number_combobox = ttk.Combobox(self.controls_frame,
                                                 textvariable=self.page_number,
                                                 state="readonly",
                                                 width=5,
                                                 justify=tk.CENTER)

        self.page_number_combobox.grid(row=1, column=1, sticky=tk.E, padx=10, pady=10)

        self.found_images_label = tk.Label(self.controls_frame, textvariable=self.found_images_in_page)
        self.found_images_label.grid(row=1, column=0, sticky=tk.E, padx=10, pady=10)

        # add a button to compare the images
        self.compare_button = tk.Button(self.controls_frame, text="מצא את ההבדלים", command=self.compare_images)
        self.compare_button.grid(row=2, column=1, sticky=tk.E, padx=10, pady=10)

        # show the main window
        self.root.mainloop()

    def short_path_and_pages_num(self):
        self.short_path.set("..." + self.document_path.get()[-50:]
                            if len(self.document_path.get()) > 50
                            else self.document_path.get())
        try:
            doc = fitz.Document(self.document_path.get())
            page_nums = []
            for page in range(doc.page_count):
                if extract_images_from_pdf.get_page_images(self.document_path.get(), page):
                    page_nums.append(page)
            self.page_number_combobox.config(values=[str(i) for i in page_nums])
        except Exception as e:
            print(e)
            self.page_number_combobox.config(values=[])

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
        find_the_differences.find_the_differences(self.images_for_comparison[0], self.images_for_comparison[1])


def main():
    FTD(None)


if __name__ == "__main__":
    main()

# TODO:
# 1. add checkbox to select if the images should be saved
# 2. add a frame to show the images
# 3. allow the user to select the min/max size of the images
