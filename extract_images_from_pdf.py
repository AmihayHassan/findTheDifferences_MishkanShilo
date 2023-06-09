import tkinter as tk
from concurrent.futures import ProcessPoolExecutor, as_completed
from tkinter import ttk

import fitz
from PIL import Image

MIN_WIDTH = 450
MAX_WIDTH = 810
MIN_HEIGHT = 450
MAX_HEIGHT = 810


def filter_image_for_comparison(all_images: list):
    # the all_images list contains tuples of (image, page_number)
    images_for_comparison = []
    for idx1, img1 in enumerate(all_images):
        for idx2, img2 in enumerate(all_images):
            # skip if the images are the same
            if idx1 == idx2:
                continue

            # extract the image dimensions, and skip if they are not the same
            img1_size = img1[0].size
            img2_size = img2[0].size
            if img1_size != img2_size:
                continue

            # check that all the images dimensions are within the range
            img1_width = img1_size[0]
            img1_height = img1_size[1]
            img2_width = img2_size[0]
            img2_height = img2_size[1]
            if MIN_WIDTH <= img1_width <= MAX_WIDTH and \
                    MIN_WIDTH <= img2_width <= MAX_WIDTH and \
                    MIN_HEIGHT <= img1_height <= MAX_HEIGHT and \
                    MIN_HEIGHT <= img2_height <= MAX_HEIGHT:
                images_for_comparison.append(img1)

    return images_for_comparison


def get_page_images_from_pdf(doc_path: str,
                             page: int):
    doc = fitz.Document(doc_path)
    page_images = []
    for image_from_pdf in doc.get_page_images(page):
        try:
            xref = image_from_pdf[0]
            pix = fitz.Pixmap(doc, xref)
            width = int(str(pix.width))
            height = int(str(pix.height))
            page_images.append((Image.frombytes("CMYK", (width, height), pix.samples),
                                page))

        except Exception as e:
            continue

    return page_images


def get_page_images(min_width=MIN_WIDTH,
                    max_width=MAX_WIDTH,
                    min_height=MIN_HEIGHT,
                    max_height=MAX_HEIGHT,
                    gui_app=None):
    document_path = gui_app.document_path.get()
    doc = fitz.Document(document_path)
    pages = doc.page_count
    gui_app.progress_bar.config(maximum=pages)
    scanned_pages = 0
    all_images = {
        f"{page + 1}": []
        for page in range(pages)
    }

    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(get_page_images_from_pdf,
                            document_path,
                            page)
            for page in range(pages)
        ]

        for future in as_completed(futures):
            scanned_pages += 1
            page_images = future.result()
            all_images[f"{page_images[0][1]}"] = page_images
            gui_app.progress_bar.step()
            gui_app.progress_info.config(text=f"{scanned_pages}/{pages} דפים נסרקו")

    gui_app.progress_bar.config(value=0)
    gui_app.progress_info.config(text="הסריקה הושלמה")

    images_for_comparison = []
    scanned_pages = 0
    gui_app.progress_info.config(text="מסנן תמונות להשוואה")

    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(filter_image_for_comparison,
                            images)
            for page_num, images in all_images.items()
        ]

        for future in as_completed(futures):
            page_images = future.result()
            scanned_pages += 1
            gui_app.progress_bar.step()
            gui_app.progress_info.config(text=f"{scanned_pages}/{pages} דפים נסרקו")

            if page_images:
                images_for_comparison.extend(page_images)

    gui_app.progress_bar.config(value=0)
    gui_app.progress_info.config(text="הסריקה הושלמה")

    gui_app.images_for_comparison = [img for img, page in images_for_comparison]
