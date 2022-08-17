import fitz
from PIL import Image

MIN_WIDTH = 600
MAX_WIDTH = 810
MIN_HEIGHT = 600
MAX_HEIGHT = 810


def get_page_images(document_path, page_number,
                    min_width=MIN_WIDTH,
                    max_width=MAX_WIDTH,
                    min_height=MIN_HEIGHT,
                    max_height=MAX_HEIGHT):
    doc = fitz.Document(document_path)

    all_images = []
    for image_from_pdf in doc.get_page_images(page_number):
        try:
            xref = image_from_pdf[0]
            pix = fitz.Pixmap(doc, xref)
            width = int(str(pix.width))
            height = int(str(pix.height))
            all_images.append(Image.frombytes("CMYK", (width, height), pix.samples))

        except:
            continue

    images_for_comparison = []
    for idx1, img1 in enumerate(all_images):
        for idx2, img2 in enumerate(all_images):
            if idx1 == idx2:
                continue
            img1_size = img1.size
            img2_size = img2.size
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
