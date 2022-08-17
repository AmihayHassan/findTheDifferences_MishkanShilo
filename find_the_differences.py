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


def mark_clusters(diff_image, img1, img2, color, clusters=10):
    """
    Mark clusters of color on black background
    :param diff_image:
    :param clusters:
    :return:
    """

    # Convert to HSV
    hsv = cv2.cvtColor(diff_image, cv2.COLOR_BGR2HSV)

    # Define lower and upper range of HSV
    lower_range = np.array([0, 0, 0])
    upper_range = np.array([15, 15, 15])

    # Threshold the HSV image
    mask = cv2.inRange(hsv, lower_range, upper_range)

    # blur the mask
    blurred = cv2.GaussianBlur(mask, (5, 5), 0)

    # Find contours
    contours, hierarchy = cv2.findContours(255 - blurred, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Find the biggest contours
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:clusters]

    # Draw contours on the images
    cv2.drawContours(img1, contours, -1, color, 2)
    cv2.drawContours(img2, contours, -1, color, 2)

    img1 = cv2.copyMakeBorder(img1, 5, 5, 2, 2, cv2.BORDER_CONSTANT, value=(0, 0, 0))
    img2 = cv2.copyMakeBorder(img2, 5, 5, 2, 2, cv2.BORDER_CONSTANT, value=(0, 0, 0))

    # concatenate the images
    concatenated = np.concatenate((img1, img2), axis=1)

    return concatenated


def find_the_differences(img1, img2, color=(0, 0, 0), resize=0.5, save=False):
    if save:
        img1.convert('RGB').save('img1.png')
        img2.convert('RGB').save('img2.png')

    # convert the color from RGB to BGR
    color = tuple(reversed(color))

    # check if the images are in PIL format
    if isinstance(img1, Image.Image):
        img1 = np.array(convert(img1))
    if isinstance(img2, Image.Image):
        img2 = np.array(convert(img2))

    # the difference between the two images
    diff = cv2.absdiff(img1, img2)

    concatenated = mark_clusters(diff, img1, img2, color)

    # resize the image to fit the screen:
    concatenated = cv2.resize(concatenated, (0, 0), fx=resize, fy=resize)
    # show the concatenated image
    cv2.imshow("diff", concatenated)
    # save the image
    if save:
        cv2.imwrite("diff.png", diff)
    # wait for a key press
    cv2.waitKey(0)
    # close the window
    cv2.destroyAllWindows()
