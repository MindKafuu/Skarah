import math
import numpy as np

def rot(axis, d):

    if axis == "X":

        result = np.array([[1, 0, 0, 0],
                           [0, math.cos(d), -math.sin(d), 0],
                           [0, math.sin(d), math.cos(d), 0],
                           [0, 0, 0, 1]])
    elif axis == "Y":

        result = np.array([[math.cos(d), 0, math.sin(d), 0],
                           [0, 1, 0, 0],
                           [-math.sin(d), 0, math.cos(d), 0],
                           [0, 0, 0, 1]])
    else:

        result = np.array([[math.cos(d), -math.sin(d), 0, 0],
                           [math.sin(d), math.cos(d), 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])

    return result

def trans(axis, length):

    if axis == "X":

        result = np.array([[1, 0, 0, length],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])
    elif axis == "Y":

        result = np.array([[1, 0, 0, 0],
                           [0, 1, 0, length],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]])
    else:   # z-axis

        result = np.array([[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 1, length],
                           [0, 0, 0, 1]])

    return result

def dhTrans(theta, d, a, alpha):

    zAxis = np.dot(rot("Z", theta),trans("Z", d))
    xAxis = np.dot(trans("X", a), rot("X", alpha))
    result = np.dot(zAxis, xAxis)

    return result
