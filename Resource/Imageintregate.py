
import numpy as np
from math import *
import serial
import time
import struct
from scipy.spatial import distance as dist
import cv2
import sys
import pandas as pd

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,1024)
cv2.namedWindow("test")
img_counter = 0
# -------------save size-----------------
def crop_image(img1, img2, tol=0):
    mask = img2 > tol
    ins = np.zeros(shape=(1000, 1000))
    x = np.ix_(mask.any(0))
    y = np.ix_(mask.any(1))
    # print('y[0]',y[0])
    # print('x[0]', x[0])
    tY = y[0][0]
    bY = y[0][len(y[0]) -1]
    tX = x[0][0]
    bX = x[0][len(x[0]) -1]

    ins[tY -5 :bY+5 , tX-5 :bX+5 ] = 1
    mask1 = ins > tol
    cp = img1[np.ix_(mask1.any(1), mask1.any(0))]
    return cp

def func():
    img = cv2.imread("image.png")
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, th1 = cv2.threshold(imgray, 10, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(th1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        # print(cv2.contourArea(c))
        if cv2.contourArea(c) < 3000:
            continue
        if cv2.contourArea(c) > 580000:
            print('Big')
            boxId = 'Big'
            f = open("type.txt", "wb")
            f.write("Big".encode())
            f.close()
        else:
            print('Small')
            boxId = 'Small'
            f = open("type.txt", "wb")
            f.write("Small".encode())
            f.close()
        print('contoureiei=', cv2.contourArea(c))
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        count = 0
        # contour1 = cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
        contour1 = cv2.drawContours(th1, [box], 0, (0, 0, 255), 2)
        x = []
        y = []
        for i in box:
            for j in i:
                count = count + 1
                if count % 2 == 0:
                    y = np.append(y, j)
                else:
                    x = np.append(x, j)
        x_min = abs(int(min(x)))
        x_max = abs(int(max(x)))
        y_min = abs(int(min(y)))
        y_max = abs(int(max(y)))
        crop1gray = imgray[y_min:y_max, x_min:x_max]
        crop1 = img[y_min:y_max, x_min:x_max]  # BGR
        crop2 = th1[y_min:y_max, x_min:x_max]  # THRESH
        crop3 = crop2[15:575, 20:870]  # CROP_THRESH
        crop2gray = crop1gray[15:575, 20:870]
        crop4 = np.invert(crop3)
        cv2.imshow("crop4", crop4)
        cv2.waitKey(0)
        crop5 = crop_image(crop2gray, crop4)
        cv2.imshow('crop5',crop5)
        cv2.waitKey(0)
        img_name = 'imagePredict.png'
        cv2.imwrite(img_name, crop5)
        return True, boxId

while True:
    ret, frame = cam.read()

    cv2.imshow("test", frame)
    if not ret:
        break
    k = cv2.waitKey(1)
    if k%256 == 32:
        # SPACE pressed
        cv2.imwrite("image.png", frame)
        print("written!")
        img_counter += 1
        Ispressed, boxId = func()
        if Ispressed == True:
            print("E")
            break 

cam.release()
cv2.destroyAllWindows()




