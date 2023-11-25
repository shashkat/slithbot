import time
import json

from common.utilities import *
from findSnakeEyes.SSnFindSnakes import *
from recordInput.recordKeyboard import *
from findSnakePixels.findSnakePixels import *
from testing.testFunctions import *

# NOTE- a pixel of an image is stored as (row, col) and not (x, y)

if __name__ == '__main__':

    time.sleep(5) # to begin the game

    refSS = Screenshot(0, 0, 900, 1440)
    gridDimension = 30
    refArea = 100
    scanArea = 150
    coorArray = MakeCoorArray(gridDimension)
    # dirArray = dirMotionArray(coorArray, refArea, scanArea) # for making arrow showing image
    snakePixels = findSnakePixels(gridDimension, refArea, scanArea)

    # make arrows on refSS
    # refSS2 = makeArrows(coorArray, dirArray, refSS)
    # image = np.uint8(refSS2)
    # cv2.imwrite('newupdates/outputImages/snakeDetect3_arrows.png', image)
    
    # whiten the snake pixels in refSS
    for itr, coor in enumerate(coorArray):
        if snakePixels[itr]:
            WhitenPixel(refSS, coor[0], coor[1])
    image = np.uint8(refSS) 
    cv2.imwrite('newupdates/outputImages/snakeDetect3.png', image)
    


    # # testing the directions found at each spot
    # refSS = Screenshot(0, 0, 900, 1440)
    # coorArray = MakeCoorArray(50)
    # # print(coorArray)
    # dirArray = dirMotionArray(coorArray, refArea=50, scanArea=100)
    # refSS = makeArrows(coorArray, dirArray, refSS)
    # # save the image
    # image = np.uint8(refSS) 
    # cv2.imwrite('newupdates/outputImages/snakeDetect1.png', image)

    # testing where a point appears on the image
    # refSS = Screenshot(0, 0, 900, 1440)
    # point = (300, 500)
    # WhitenPixel(refSS, point[0], point[1])
    # image = np.uint8(refSS)
    # cv2.imwrite('newupdates/outputImages/snakeDetect1.png', image)    



    # coorArray = [(300, 300), (400, 400), (500, 500), (600, 600), (700, 700), (800, 800)]
    # directionArray = dirMotionArray(coorArray)
    # print(directionArray)

    # testDirMotionArray()

    # fullBlackPixelArray = []
    # fullSnakePixelArray = []
    # fullDirArray = []
    # fullKeyArray = []
    # timeDuration = 10 # number of seconds
    # timePeriod = 1 # number of seconds per screenshot
    # gridDimension = 100

    # for i in range(int(timeDuration/timePeriod)):
    #     time.sleep(timePeriod)
    #     # blackPixels = SSnFindSnakes(i) # iterator i is just for naming the image files uniquely
    #     # fullBlackPixelArray.append(blackPixels)

    #     mouseData = []
    #     dir = dirMotion(800,1250)
    #     fullDirArray.append(dir)

    #     start = time.time()
    #     snakePixels = findSnakePixels(gridDimension, dir)
    #     middle = time.time()
    #     fullSnakePixelArray.append(snakePixels)
    #     end = time.time()

    #     print('time taken to find snake pixels:', middle-start)
    #     print('time taken to find snake pixels and append to array:', end-start)

    #     # just to test
    #     ssTest = Screenshot(0, 0, 900, 1440)
    #     for row in range(snakePixels.shape[0]):
    #         for col in range(snakePixels.shape[1]):
    #             if snakePixels[row, col]:
    #                 WhitenPixel(ssTest, row*gridDimension, col*gridDimension)

    #     image = np.uint8(ssTest)
    #     cv2.imwrite('newupdates/outputImages/snakeDetect'+str(i)+'.png', image)
                
    #     # record keyboard at the instant (0 is left and 1 is right and 2 is none)
    #     key = recordKeyboard()
    #     fullKeyArray.append(key)

    #     print('iteration', i, 'done')

    # # with open ('newupdates/outputMatrices/output_matrix.json', 'w') as f:
    # #     json.dump(fullBlackPixelArray, f)

    # with open ('newupdates/outputMatrices/dir_matrix.json', 'w') as f:
    #     json.dump(fullDirArray, f)

    # with open ('newupdates/outputMatrices/key_matrix.json', 'w') as f:
    #     json.dump(fullKeyArray, f)

    # with open ('newupdates/outputMatrices/snake_matrix.json', 'w') as f:
    #     json.dump(fullSnakePixelArray, f)

    # _____________________
    

    # time.sleep(1)
    # # dir = dirMotion()
    # key = recordKeyboard()
    # print(key)

    # print(len(blackPixels))
    #### testing part below ####

    # for pixel in blackPixels:
    #     data = WhitenPixel(data, pixel[0], pixel[1])
    # image = np.uint8(data)
    # cv2.imwrite('image.png', image)

# i am close, there is just some offset in the template matching, in the direction of motion of the snake
# done, the offset was because of the reverse order of the coordinates returned by the matchTemplate function

# current issue: findSnakes taking a lot of time, need to optimize it. Solved!
# current issue: the corners of the whole image are detected as snake pixels, as the direction of motion is changing there, need to fix it. Solved
# Next thing: need to implement the save image thing (both, snakes detected and arrows make) inside the dirMotionArray function, so that the arrows/snakes are superimposed on the same (correct) image
