import cv2
import numpy as np
from PIL import Image


def convert(image):
    if image.mode == 'CMYK':
        rgb_image = image.convert('RGB')
        # use cv2 to convert the image from RGB to BGR
        bgr_image = cv2.cvtColor(np.array(rgb_image), cv2.COLOR_RGB2BGR)
        return bgr_image
    return image


def find_the_differences(img1, img2, resize=0.5, save=False):
    # check if the images are in PIL format
    if isinstance(img1, Image.Image):
        img1 = np.array(convert(img1))
    if isinstance(img2, Image.Image):
        img2 = np.array(convert(img2))

    # find the differences between the images, and concatenate the original images with the difference image
    concatenated = np.concatenate((img1, cv2.absdiff(img1, img2), img2), axis=1)
    # resize the image to fit the screen:
    concatenated = cv2.resize(concatenated, (0, 0), fx=resize, fy=resize)
    # show the concatenated image
    cv2.imshow("diff", concatenated)
    # save the image
    if save:
        cv2.imwrite("diff.png", concatenated)
    # wait for a key press
    cv2.waitKey(0)
    # close the window
    cv2.destroyAllWindows()
