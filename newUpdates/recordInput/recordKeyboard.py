import keyboard

# function to record if the right arrow or left arrow is being pressed
def recordKeyboard():
    if keyboard.is_pressed('left'):
        return 0
    elif keyboard.is_pressed('right'):
        return 1
    else:
        return 2