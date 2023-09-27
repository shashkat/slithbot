import cv2
import numpy as np
import mss
import math
import time

def Screenshot(leftCoor, topCoor, maxy, maxx, reduction_factor = 2, gray = True):
    with mss.mss() as sct:
        # The screen part to capture
        region = {'left': leftCoor, 'top': topCoor, 'width': maxx, 'height': maxy}
        # Grab the data
        img = sct.grab(region)
        if gray:
            result = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2GRAY)
        else:
            result = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR)

        img = result[::reduction_factor, ::reduction_factor]
        return img
    
# function to change the color of a pixel and its neighbors
def changeCoorToWhite(img, x, y, i):
    maxx = img.shape[0]-1
    maxy = img.shape[1]-1
    if x+i < 0 or y+i < 0:
        return
    if x+i > maxx or y+i > maxy:
        return
    img[x+i, y] = 255
    img[x, y+i] = 255

# function to change the color of a pixel and its neighbors
def changeCoorToBlack(img, x, y, i):
    maxx = img.shape[0]-1
    maxy = img.shape[1]-1
    if x+i < 0 or y+i < 0:
        return
    if x+i > maxx or y+i > maxy:
        return
    img[x+i, y] = 0
    img[x, y+i] = 0

# function to whiten a pixel and its neighbors (basically make a plus sign)
def WhitenPixel(img, x, y):
    for i in range(-50, 50):
        changeCoorToWhite(img, x, y, i)
    changeCoorToBlack(img, x, y, 0)
    return img

# function to read an image and convert it to black and white and return it
def ReadnBW(path):
    img = cv2.imread(path)
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# find the distance between two coordinates
def distCoor(coor1, coor2):
    return ((coor1[0]-coor2[0])**2 + (coor1[1]-coor2[1])**2)**0.5

# function to check if a coordinate is in range of an image
def inRange(row, col, img):
    if row < 0 or col < 0:
        return False
    if row >= img.shape[0] or col >= img.shape[1]:
        return False
    return True

# function to find the direction of motion of elements on screen
def dirMotion(x, y):
    takeSS = Screenshot(0, 0, 900, 1440)
    time.sleep(0.02)
    takeSS2 = Screenshot(0, 0, 900, 1440)
    # takeSS = cv2.equalizeHist(takeSS)
    # takeSS2 = cv2.equalizeHist(takeSS2)

    coor1 = (x, y) # reference point
    refArea = 100

    # ensuring that the ref area is within the image
    topCoor1 = max(0,coor1[0]-refArea)
    botCoor1 = min(900,coor1[0]+refArea)
    leftCoor1 = max(0,coor1[1]-refArea)
    rightCoor1 = min(1440,coor1[1]+refArea)
    takeSS = takeSS[topCoor1:botCoor1, leftCoor1:rightCoor1]
    
    scanArea = 150
    # ensuring that the scan area is within the image
    topCoor2 = max(0,coor1[0]-scanArea)
    botCoor2 = min(900,coor1[0]+scanArea)
    leftCoor2 = max(0,coor1[1]-scanArea)
    rightCoor2 = min(1440,coor1[1]+scanArea)
    takeSS2 = takeSS2[topCoor2:botCoor2, leftCoor2:rightCoor2]
    # find coordinates of takeSS in takeSS2
    coor2_temp = findCoor(takeSS, takeSS2)

    # image of calculation inside backup/offsetCalculation.jpeg
    topCornerOffset = coor1[0]-topCoor1
    leftCornerOffset = coor1[1]-leftCoor1

    topOriginOffset = coor1[0]-topCoor2
    leftOriginOffset = coor1[1]-leftCoor2

    coor2 = (coor1[0]+coor2_temp[0]-topOriginOffset+topCornerOffset, coor1[1]+coor2_temp[1]-leftOriginOffset+leftCornerOffset) # adding coor1 because the coordinates are relative to takeSS2
    # print(coor1, coor2)
    # print(coor2[0] - coor1[0], distCoor(coor1, coor2))

    if distCoor(coor1, coor2):
        direction = math.asin((coor2[0] - coor1[0])/distCoor(coor1, coor2))
    else:
        direction = 0
    takeSS2[coor2_temp[0], coor2_temp[1]] = 255
    # cv2.imwrite('overlayed.png', overlayImages(takeSS, takeSS2, coor2_temp))
    cv2.imwrite('newUpdates/outputImages/SS1.png', takeSS)
    cv2.imwrite('newUpdates/outputImages/SS2.png', takeSS2)

    return direction

# function to find the coordinates of a smaller image in a larger image
def findCoor(smallImg, largeImg):
    result = cv2.matchTemplate(smallImg, largeImg, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # print(min_val, max_val)
    reverseCoor = (max_loc[1], max_loc[0]) # required as the coordinates are returned in the opposite order
    return reverseCoor