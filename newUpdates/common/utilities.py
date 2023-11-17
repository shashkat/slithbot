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
def WhitenPixel(img, x, y, plusSize = 20):
    for i in range(-plusSize, plusSize):
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

# function to find the direction of motion of an array of coordinates on screen (returns an 
# array of directions). refArea is the area around the reference point to be considered and
# scanArea is the area around the reference point to be scanned for the reference point
def dirMotionArray(coorArray, refArea = 100, scanArea = 150):
    takeSSOrig = Screenshot(0, 0, 900, 1440)
    time.sleep(0.0001)
    takeSS2Orig = Screenshot(0, 0, 900, 1440)
    directionArray = []
    
    for coor in coorArray:
        topCoor1 = max(0,coor[0]-refArea)
        botCoor1 = min(900,coor[0]+refArea)
        leftCoor1 = max(0,coor[1]-refArea)
        rightCoor1 = min(1440,coor[1]+refArea)
        takeSS = takeSSOrig.copy()
        takeSS = takeSS[topCoor1:botCoor1, leftCoor1:rightCoor1]

        topCoor2 = max(0,coor[0]-scanArea)
        botCoor2 = min(900,coor[0]+scanArea)
        leftCoor2 = max(0,coor[1]-scanArea)
        rightCoor2 = min(1440,coor[1]+scanArea)
        takeSS2 = takeSS2Orig.copy()
        takeSS2 = takeSS2[topCoor2:botCoor2, leftCoor2:rightCoor2]
        
        # find coordinates of takeSS in takeSS2
        coor2_temp = findCoor(takeSS, takeSS2)

        # image of below calculation is inside backup/offsetCalculation.jpeg for reference
        # basically coor2_temp results are relative to takeSS2, so we need to modify them
        topCornerOffset = coor[0]-topCoor1
        leftCornerOffset = coor[1]-leftCoor1
        topOriginOffset = coor[0]-topCoor2
        leftOriginOffset = coor[1]-leftCoor2

        coor2 = (coor[0]+coor2_temp[0]-topOriginOffset+topCornerOffset, coor[1]+coor2_temp[1]-leftOriginOffset+leftCornerOffset) # adding coor1 because the coordinates are relative to takeSS2

        # Refer to backup/dirCalculationQuadrantDetails.jpeg for details on the calculation below
        # Note1: coor2 is the final coordinate of the reference point in the second screenshot, so if we 
        # are taking snake in top right direction, then coor2 will be to bottom left of coor
        # Note2: the way our coordinate system works, the y axis is inverted, so quadrant 1 is bottom right,
        # quadrant 2 is bottom left, quadrant 3 is top left and quadrant 4 is top right
        if distCoor(coor, coor2):
            sinValue = math.asin((coor2[0] - coor[0])/distCoor(coor, coor2))
            # since coor2 is the final coordinate of the reference point, the coordinates of coor2 will be
            # in opposite quadrant to that of snake motion

            if coor2[1] - coor[1] < 0: # if the x coordinate of coor2 is less than that of coor, then the direction is 180 degrees from the calculated direction
                # note that if in 2nd quadrant, then need to subtract from pi, if in 3rd quadrant, then need to do -pi+angle
                if sinValue >= 0:
                    direction = math.pi - sinValue
                elif sinValue < 0:
                    direction = -math.pi - sinValue
            else: # case when coor2 is in quadrants 1 and 4 wrt coor
                direction = sinValue
        else:
            direction = 0
        directionArray.append(direction)
        # just showing the detected spots on the image and saving for testing
        # takeSSOrig = WhitenPixel(takeSS, coor[0], coor[1])
        # cv2.imwrite('newUpdates/outputImages/' + str(coor[0]) + ',' + str(coor[1]) + '_1.png', takeSSOrig) 
        # takeSS2Orig = WhitenPixel(takeSS2, coor2_temp[0], coor2_temp[1]) 
        # cv2.imwrite('newUpdates/outputImages/' + str(coor[0]) + ',' + str(coor[1]) + '_2.png', takeSS2Orig)

    return directionArray
        
# function to find the direction of motion of elements on screen
def dirMotion(x, y):
    takeSS = Screenshot(0, 0, 900, 1440)
    time.sleep(0.02)
    takeSS2 = Screenshot(0, 0, 900, 1440)
    # takeSS = cv2.equalizeHist(takeSS)
    # takeSS2 = cv2.equalizeHist(takeSS2)

    coor1 = (x, y) # reference point
    refArea = 100 # the area around the reference point to be considered

    # ensuring that the ref area is within the image
    topCoor1 = max(0,coor1[0]-refArea)
    botCoor1 = min(900,coor1[0]+refArea)
    leftCoor1 = max(0,coor1[1]-refArea)
    rightCoor1 = min(1440,coor1[1]+refArea)
    takeSS = takeSS[topCoor1:botCoor1, leftCoor1:rightCoor1]
    
    scanArea = 150 # the area around the reference point to be scanned for the reference point
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

    # Refer to backup/dirCalculationQuadrantDetails.jpeg for details on the calculation below
    # Note1: coor2 is the final coordinate of the reference point in the second screenshot, so if we 
    # are taking snake in top right direction, then coor2 will be to bottom left of coor1
    # Note2: the way our coordinate system works, the y axis is inverted, so quadrant 1 is bottom right,
    # quadrant 2 is bottom left, quadrant 3 is top left and quadrant 4 is top right
    if distCoor(coor1, coor2):
        sinValue = math.asin((coor2[0] - coor1[0])/distCoor(coor1, coor2))
        # since coor2 is the final coordinate of the reference point, the coordinates of coor2 will be
        # in opposite quadrant to that of snake motion

        if coor2[1] - coor1[1] < 0: # if the x coordinate of coor2 is less than that of coor1, then the direction is 180 degrees from the calculated direction
            # note that if in 2nd quadrant, then need to subtract from pi, if in 3rd quadrant, then need to do -pi+angle
            if sinValue >= 0:
                direction = math.pi - sinValue
            elif sinValue < 0:
                direction = -math.pi - sinValue
        else: # case when coor2 is in quadrants 1 and 4 wrt coor1
            direction = sinValue
    else:
        direction = 0
    takeSS2[coor2_temp[0], coor2_temp[1]] = 255
    # cv2.imwrite('overlayed.png', overlayImages(takeSS, takeSS2, coor2_temp))
    # cv2.imwrite('newUpdates/outputImages/SS1.png', takeSS)
    # cv2.imwrite('newUpdates/outputImages/SS2.png', takeSS2)

    return direction

# function to find the coordinates of a smaller image in a larger image
def findCoor(smallImg, largeImg):
    result = cv2.matchTemplate(smallImg, largeImg, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # print(min_val, max_val)
    reverseCoor = (max_loc[1], max_loc[0]) # required as the coordinates are returned in the opposite order
    return reverseCoor