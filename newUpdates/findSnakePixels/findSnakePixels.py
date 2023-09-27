from common.utilities import *

def findSnakePixels(gridDimension, direction):
    ss = Screenshot(0, 0, 900, 1440)

    snakePixels = np.zeros((900//gridDimension, 1440//gridDimension), dtype=bool)

    for row in range(snakePixels.shape[0]):
        for col in range(snakePixels.shape[1]):
            if checkIfSnake(row, col, ss, direction):
                snakePixels[row, col] = True
            else:
                snakePixels[row, col] = False

    return snakePixels

# function to check if a pixel is a snake pixel
def checkIfSnake(row, col, ss, direction):
    snakeDir = dirMotion(row, col)
    # below we are using a threshold of 0.1 to check if the direction of the snake is the same as the direction of motion of the snake
    if abs(snakeDir - direction)<0.1:
        return False
    else:
        return True