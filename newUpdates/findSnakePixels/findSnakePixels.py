from common.utilities import *
from scipy import stats

# function to find the snake pixels, returns a boolean array
def findSnakePixels(gridDimension):
    # the // is used to get the integer part of the division

    # this is the coordinate array, which will be given as an input to the dirMotionArray function
    coorArray = MakeCoorArray(gridDimension)

    # this is the direction array, which stores the direction of motion of the snake
    dirArray = dirMotionArray(coorArray)

    # netDirection stores the net direction of motion of the snake (opposite of that actually)
    netDirection = FindNetDirection(dirArray)

    # this is the empty snakePixels array, which stores if a pixel is a snake pixel or not
    snakePixels = MakeSnakePixelsArray(gridDimension)

    # loop through each coordinate in the coordinate array and check if it is a snake pixel
    for itr, coor in enumerate(coorArray):
        if sameDirection(dirArray[itr], netDirection):
            snakePixels[itr] = False
        else:
            snakePixels[itr] = True

    return snakePixels

# function to check if two directions are the same
def sameDirection(dir1, dir2):
    if abs(dir1 - dir2) < 0.2: # this is the threshold value for the directions to be considered the same
        return True
    else:
        return False

# function to check if a pixel is a snake pixel
# def checkIfSnake(row, col):
#     ss1 = Screenshot(0, 0, 900, 1440)
#     time.sleep(0.02)
#     ss2 = Screenshot(0, 0, 900, 1440)
#     snakeDir = dirMotion(row, col)
#     # below we are using a threshold of 0.1 to check if the direction of the snake is the same as the direction of motion of the snake
#     if abs(snakeDir - direction)<0.1:
#         return False
#     else:
#         return True
    
# function to make an array of coordinates
def MakeCoorArray(gridDimension):
    # coorArray should be an array of coordinates
    coorArray = []
    for row in range(900//gridDimension):
        for col in range(1440//gridDimension):
            coorArray.append((row*gridDimension, col*gridDimension))
    return coorArray

# function to make an empty array of snake pixels
def MakeSnakePixelsArray(gridDimension):
    snakePixels = []
    for row in range(900//gridDimension):
        for col in range(1440//gridDimension):
            snakePixels.append(False)
    return snakePixels

# this function will take the dirArray, round off the values to maybe 1 decimal place and return the mode of the array
def FindNetDirection(dirArray):
    # round off the values to 1 decimal place
    dirArray = np.round(dirArray, 1)
    # find the mode of the array
    result = stats.mode(dirArray)
    netDirection = result.mode[0] # extract the mode from the result
    return netDirection