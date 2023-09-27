import cv2
import numpy as np
import time
import math
from common.utilities import Screenshot, distCoor

# function to find the direction of motion of elements on screen
def dirMotion():
    takeSS = Screenshot(0, 0, 900, 1440, 1)
    time.sleep(0.02)
    takeSS2 = Screenshot(0, 0, 900, 1440, 1)
    # takeSS = cv2.equalizeHist(takeSS)
    # takeSS2 = cv2.equalizeHist(takeSS2)

    coor1 = (1600, 2500) # reference point
    refArea = 100
    takeSS = takeSS[coor1[0]-refArea:coor1[0]+refArea , coor1[1]-refArea:coor1[1]+refArea]
    
    scanArea = 150
    takeSS2 = takeSS2[coor1[0]-scanArea:coor1[0]+scanArea , coor1[1]-scanArea:coor1[1]+scanArea]
    # find coordinates of takeSS in takeSS2
    coor2_temp = findCoor(takeSS, takeSS2)
    coor2 = (coor1[0]+coor2_temp[0]-scanArea+refArea, coor1[1]+coor2_temp[1]-scanArea+refArea) # adding coor1 because the coordinates are relative to takeSS2
    # print(coor1, coor2)
    # print(coor2[0] - coor1[0], distCoor(coor1, coor2))

    if distCoor(coor1, coor2):
        direction = math.asin((coor2[0] - coor1[0])/distCoor(coor1, coor2))
    else:
        direction = 0
    takeSS2[coor2_temp[0], coor2_temp[1]] = 255
    # cv2.imwrite('overlayed.png', overlayImages(takeSS, takeSS2, coor2_temp))
    cv2.imwrite('SS1.png', takeSS)
    cv2.imwrite('SS2.png', takeSS2)

    return direction

# function to find the coordinates of a smaller image in a larger image
def findCoor(smallImg, largeImg):
    result = cv2.matchTemplate(smallImg, largeImg, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # print(min_val, max_val)
    reverseCoor = (max_loc[1], max_loc[0]) # required as the coordinates are returned in the opposite order
    return reverseCoor