

# check if the first tuple is within (0,0) and second tuple. All corner cases count as not within.
def CheckWithinBounds(coord: tuple, xmax_ymax: tuple) -> bool:
    x_coord, y_coord = coord
    xmax, ymax = xmax_ymax 
    if x_coord <= 0 or x_coord >= xmax:
        return False
    if y_coord <= 0 or y_coord >= ymax:
        return False
    return True









