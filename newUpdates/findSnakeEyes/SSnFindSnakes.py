import cv2
import numpy as np
from common.utilities import *

def SSnFindSnakes(i):
    blackPixels = []
    data = Screenshot(0, 0, 900, 1400)
    # data = ReadnBW('new_updates/img1.png')
    maxy = data.shape[0]
    maxx = data.shape[1]

    # identify black regions of screen
    print(maxy, maxx)
    topMargin = 160
    scanningPrecision = 3 # how many pixels to skip while scanning
    for row in range(topMargin, maxy-50, scanningPrecision): # -50 to avoid the bottom and right extreme as some black spots there
        for col in range(0, maxx-50, scanningPrecision):
            if data[row, col] == 0:
                blackPixels.append((row, col))

    # combine the closeby black regions into one
    blackPixels = combineBlackPixels(blackPixels)

    for _ in range(10-len(blackPixels)):
        blackPixels.append((0, 0))

    for pixel in blackPixels:
        data = WhitenPixel(data, pixel[0], pixel[1])
    image = np.uint8(data)
    cv2.imwrite('image_'+str(i)+'.png', image)

    return blackPixels

# combine the closeby black regions into one
def combineBlackPixels(blackPixels):
    # Create a new list to store the pixels to keep
    pixels_to_keep = []

    for pixel in blackPixels:
        should_keep = True
        for pixel2 in pixels_to_keep:
            if distCoor(pixel, pixel2) < 50:
                should_keep = False
                break
        if should_keep:
            pixels_to_keep.append(pixel)

    return pixels_to_keep