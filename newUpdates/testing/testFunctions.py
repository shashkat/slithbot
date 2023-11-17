from common.utilities import *

# function to overlay a smaller image on a bigger image at a specified coordinate
def overlayImages(smallImg, bigImg, coor):
    newBigImg = bigImg.copy()
    for row in range(smallImg.shape[0]):
        for col in range(smallImg.shape[1]):
            if inRange(coor[0]+row, coor[1]+col, bigImg):
                newBigImg[coor[0]+row, coor[1]+col] = smallImg[row, col]
    return newBigImg

# function to test the dirMotionArray function
def testDirMotionArray():

    coorArray = [(300, 300)]
    start = time.time()
    dirArray = dirMotionArray(coorArray)
    end = time.time()
    print(dirArray)
    print('time taken:', end-start)