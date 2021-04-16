from matplotlib import pyplot as plt
import pylab
import cv2
import numpy as np
from scipy import ndimage
from skimage.morphology import medial_axis, skeletonize, skeletonize_3d
from PIL import Image
import sys

#---------------------------------------------------model---------------------------------------------------
import keras
from keras.models import Sequential
from keras import optimizers
from keras.layers import (Dense, Dropout, Flatten,Activation,Add,concatenate, BatchNormalization, Convolution2D, Dense,Flatten, Input, MaxPooling2D, ZeroPadding2D, UpSampling2D,Conv2D, MaxPooling2D)
# from keras.models import Model, load_model
from keras.initializers import glorot_uniform

# model1 = load_model('resnetlevel1_1.h5')
# model2 = load_model('resnetlevel2_1.h5')
# model3 = load_model('resnetlevel3_2.h5')

charclass = ['ก','ข','ฃ','ค','ฅ','ฆ','ง','จ','ฉ','ช','ซ','ฌ','ฎ','ฏ','ฑ'
    ,'ฒ','ณ','ด','ต','ถ','ท','ธ','น','บ','ป','ผ','ฝ','พ','ฟ','ภ','ม','ย'
    ,'ร','ฤ','ล','ฦ','ว','ศ','ษ','ส','ห','ฬ','อ','ฮ','ฯ','า','เ','โ','ใ','ไ'
    ,'ๆ','0','1','2','3','4','5','6','7','8','9','/','ญ','ฐ','ั'
    ,'ิ','ี','ึ','ื','็','่','้','๊','๋','์','ำ'
    ,'ุ','ู'
    ,'-','ะ']
numclass = [0,1,12,23,34,44,54,62,63,64,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17
    ,18,19,20,21,22,24,25,26,27,28,29,30,31,32,33,35,36,37,38,39,40,41,42
    ,43,45,46,47,48,49,50,51,52,53,55,56,57,58,59,60,61
    ,71,72,73,74,75,76,77,78,79,80,81
    ,101,102
    ,1000,200]
#-----------------------------------------------------------------------------------------------------------



def crop_image(img1, img2, w, tol=0):
    mask = img2 > tol
    ins = np.zeros(shape=(1000, 1000))
    x = np.ix_(mask.any(0))
    y = np.ix_(mask.any(1))
    tY = y[0][0]
    bY = y[0][len(y[0]) - 1]
    tX = x[0][0]
    bX = x[0][len(x[0]) - 1]
    lX = w - (w - tX)
    rX = w - bX
    ins[tY - 1 :bY + 1, tX + 1 - lX:bX + rX] = 1
    mask1 = ins > tol
    cp = img1[np.ix_(mask1.any(1), mask1.any(0))]
    return cp

def crop_image2(img1, img2, tol=0):
    mask = img2 > tol
    ins = np.zeros(shape=(300, 300))
    x = np.ix_(mask.any(0))
    y = np.ix_(mask.any(1))
    lenX = np.shape(x)
    lenY = np.shape(y)
    tY = y[0][0]
    bY = y[0][len(y[0]) - 1]
    tX = x[0][0]
    bX = x[0][len(x[0]) - 1]
    #     print(lenX)
    cp = img1[np.ix_(mask.any(1), mask.any(0))]
    if lenX[1] < 20:
        rX = 28 - lenX[1]
        rX = round(rX / 2)
        ins[tY:bY, tX - rX:bX + rX + 1] = 1
        # print("rX", rX)
        if rX < 0:
            rX = lenX[1]
            ins[tY:bY, tX - rX:bX + rX + 1] = 1
        mask1 = ins > tol
        cp = img1[np.ix_(mask.any(1), mask1.any(0))]
    elif lenY[1] < 20:
        rY = 28 - lenY[1]
        rY = round(rY / 2)
        # print("rY", rY)
        ins[tY - rY:bY + rY + 1, tX:bX] = 1
        if rY < 0:
            rY = lenY[1]
            ins[tY:bY, tX - rY:bX + rY + 1] = 1
        mask1 = ins > tol
        cp = img1[np.ix_(mask1.any(1), mask.any(0))]
    return cp

def crop_middle(img1, img2, tol = 0):
    mask = img2 > tol
    return img1[np.ix_(mask.any(1), mask.any(0))]




charclass = ['ก','ข','ฃ','ค','ฅ','ฆ','ง','จ','ฉ','ช','ซ','ฌ','ฎ','ฏ','ฑ'
    ,'ฒ','ณ','ด','ต','ถ','ท','ธ','น','บ','ป','ผ','ฝ','พ','ฟ','ภ','ม','ย'
    ,'ร','ฤ','ล','ฦ','ว','ศ','ษ','ส','ห','ฬ','อ','ฮ','ฯ','า','เ','โ','ใ','ไ'
    ,'ๆ','0','1','2','3','4','5','6','7','8','9','/','ญ','ฐ','ั'
    ,'ิ','ี','ึ','ื','็','่','้','๊','๋','์','ำ'
    ,'ุ','ู'
    ,'-','ะ']
numclass = [0,1,12,23,34,44,54,62,63,64,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17
    ,18,19,20,21,22,24,25,26,27,28,29,30,31,32,33,35,36,37,38,39,40,41,42
    ,43,45,46,47,48,49,50,51,52,53,55,56,57,58,59,60,61
    ,71,72,73,74,75,76,77,78,79,80,81
    ,101,102
    ,1000,200]


def crop_image(img1, img2, w, tol=0):
    mask = img2 > tol
    ins = np.zeros(shape=(1000, 1000))
    x = np.ix_(mask.any(0))
    y = np.ix_(mask.any(1))
    tY = y[0][0]
    bY = y[0][len(y[0]) - 1]
    tX = x[0][0]
    bX = x[0][len(x[0]) - 1]
    lX = w - (w - tX)
    rX = w - bX
    ins[tY - 1 :bY + 1, tX + 1 - lX:bX + rX] = 1
    mask1 = ins > tol
    cp = img1[np.ix_(mask1.any(1), mask1.any(0))]
    return cp

def crop_image2(img1, img2, tol=0):
    mask = img2 > tol
    ins = np.zeros(shape=(300, 300))
    x = np.ix_(mask.any(0))
    y = np.ix_(mask.any(1))
    lenX = np.shape(x)
    lenY = np.shape(y)
    tY = y[0][0]
    bY = y[0][len(y[0]) - 1]
    tX = x[0][0]
    bX = x[0][len(x[0]) - 1]
    #     print(lenX)
    cp = img1[np.ix_(mask.any(1), mask.any(0))]
    if lenX[1] < 20:
        rX = 28 - lenX[1]
        rX = round(rX / 2)
        ins[tY:bY, tX - rX:bX + rX + 1] = 1
        # print("rX", rX)
        if rX < 0:
            rX = lenX[1]
            ins[tY:bY, tX - rX:bX + rX + 1] = 1
        mask1 = ins > tol
        cp = img1[np.ix_(mask.any(1), mask1.any(0))]
    elif lenY[1] < 20:
        rY = 28 - lenY[1]
        rY = round(rY / 2)
        # print("rY", rY)
        ins[tY - rY:bY + rY + 1, tX:bX] = 1
        if rY < 0:
            rY = lenY[1]
            ins[tY:bY, tX - rY:bX + rY + 1] = 1
        mask1 = ins > tol
        cp = img1[np.ix_(mask1.any(1), mask.any(0))]
    return cp

def crop_middle(img1, img2, tol = 0):
    mask = img2 > tol
    return img1[np.ix_(mask.any(1), mask.any(0))]



#------------------Start---------------------
img = cv2.imread('imagePredict.png',0)

cv2.imshow('Original.png', img)
# cv2.waitKey(1000)
# blur = cv2.GaussianBlur(img,(3,3),0)
ret,thresh = cv2.threshold(img,40,255,cv2.THRESH_BINARY_INV)#binary
kernel1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
# ret2,thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,19,16)
dilation = cv2.dilate(thresh,kernel1,iterations = 1)
# erosion = cv2.erode(dilation,kernel2,iterations = 1)

#11,12
#15,14
#17,14
#19,16***

#----------eiei--------------------
y, x = img.shape
img[0] = 0
#img[1] = 0
#img[2] = 0
img[y - 1] = 0
#img[y - 2] = 0
#img[y - 3] = 0
img = np.transpose(img)
img[0] = 0
#img[1] = 0
#img[2] = 0
img[x - 1] = 0
#img[x - 2] = 0
#img[x - 3] = 0
img = np.transpose(img)

cv2.imshow('img', thresh)
cv2.imshow('c', dilation)
cv2.waitKey(0)
cv2.destroyAllWindows()


#
# img = np.transpose(img)
# #---------Histogram Projection---------------
# (rows,cols)=img.shape
# h_projection = np.array([ x/255/rows for x in img.sum(axis=0)])
# plt.plot(range(cols), h_projection.T)
# #plt.show()
#
# #--------Line segmentation--------
# img = np.transpose(img)
# count = 0
# count2 = 0
# num = 0
# blank_space = []
#
# while (count < cols):
#     if (h_projection[count] > 0.02):
#         num = num + 1
#         lst = []
#         lst.append(img[count - 1])
#         while (True):
#             lst.append(img[count])
#             count = count + 1
#             if (count >= cols):
#                 break
#             else :
#                 if (h_projection[count] == 0):
#                     if (count2 < 6):       #distance of character
#                         count2 = count2 + 1
#                     else :
#                         break
#                 else :
#                     count2 = 0
#         lst = np.array(lst)
#         cv2.imwrite(str(num) + '.png', lst)
#         #cv2.imshow('line' + str(num) + '.png', lst)
#         cv2.waitKey(1000)
#     if (count2 > 0):
#         blank_space.append(count2)
#     count2 = 0
#     count = count + 1
# print(blank_space)
#
# #-------Crop------------
# for i in range(1 ,num + 1):
#     im = []
#     img = cv2.imread(str(i) + '.png',0)
#     y, x = img.shape
#     for n in range(y - blank_space[i-1] + 0):
#         im.append(img[n])
#     im = np.array(im)
#     cv2.imwrite(str(i) + '.png', im)
#     cv2.imshow(str(i) + '.png', im)
#     cv2.waitKey(1000)
#
#
#
#
#
#
#
# '''
# #-------------------delete noise-------------
# for i in range(1 ,num + 1):
#     img = cv2.imread(str(i) + '.png',0)
#     #---------Histogram Projection---------------
#     (rows,cols)=img.shape
#     h_projection = np.array([ x/255/rows for x in img.sum(axis=0)])
#     plt.plot(range(cols), h_projection.T)
#     #plt.show()
#     #--------Line segmentation--------
#     img = np.transpose(img)
#     count = 0
#     count2 = 0
#     num = 0
#     blank_space = []
#     while (count < cols):
#         if (h_projection[count] > 0.2):
#             num = num + 1
#             lst = []
#             lst.append(img[count - 1])
#             while (True):
#                 lst.append(img[count])
#                 count = count + 1
#                 if (count >= cols):
#                     break
#                 else :
#                     if (h_projection[count] == 0):
#                         if (count2 < 50):       #distance of character
#                             count2 = count2 + 1
#                         else :
#                             break
#                     else :
#                         count2 = 0
#             lst = np.transpose(lst)
#             lst = np.array(lst)
#             cv2.imwrite(str(i) + '.png', lst)
#             cv2.imshow(str(i) + '.png', lst)
#             cv2.waitKey(1000)
#         count2 = 0
#         count = count + 1
# #-----------------------------------------
# '''
#
#
#
#
#
#
# #---------Character segmentation------------
# real_class = []
# for t in range(1 ,num + 1):
#
#     img = cv2.imread(str(t) + '.png', 0)
#     img = np.transpose(img)
#     ret, labels = cv2.connectedComponents(img)
#
#     x, y = labels.shape
#     middle_y = int(y/2) + 5
#     n = x*y
#     n = np.arange(n)
#
#     im = []
#     lst_x = []
#     lst_y = []
#     lst_sort = []
#     for i in range(1,ret):
#         b = np.array(labels)
#         b = b.flatten()
#         b = np.array(b, dtype=np.uint8)
#         b[n[b!=i]] = 0
#         b = b.reshape(x, y)
#         b = b*255
#
#         a = True
#         c = 0
#         count_x = 0
#         for r in b:
#             if (a == True):
#                 count_y = 0
#                 count_x = count_x + 1
#                 for j in r:
#                     if (j == 0):
#                         count_y = count_y + 1
#                     else:
#                         c = c + 1
#                         if (c == 6):            #########
#                             a = False
#                             break
#             else:
#                 break
#         lst_sort.append(count_x)
#         lst_x.append(count_x)
#         lst_y.append(count_y)
#         b = np.transpose(b)
#         im.append(b)
#         cv2.imwrite('labels' + str(i) + '.png', b)
#         #cv2.imshow('labeled.png', b)
#         #cv2.waitKey()
#     #print('x = ' + str(lst_x))
#     #print('y = ' + str(lst_y))
#
#
#
#     #--------Find level of charecter---------
#     lst_level = []
#     check = True
#     for n in range(1, ret):
#         img = cv2.imread('labels' + str(n) + '.png', 0)
#         for i in img[middle_y]:
#             if (i != 0):
#                 check = True
#                 level = 1
#                 lst_level.append(1)
#                 break
#             else :
#                 check = False
#         if (check == False):
#             if (lst_y[n-1] < middle_y):
#                 level = 2
#                 lst_level.append(2)
#             else :
#                 level = 3
#                 lst_level.append(3)
#     print('level = ' + str(lst_level))
#
#
#     lst_x2 = []
#     lst_x2.append(0)
#     lst_x2.extend(lst_x)
#     lst_x2.append(0)
#     #print(lst_x2)
#     #-------------crop---------------
#     ret2 = ret
#     for n in range(1, ret):
#         im = cv2.imread('labels' + str(n) + '.png')
#         gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
#         ret,img_thresh = cv2.threshold(gray,80,255,cv2.THRESH_BINARY)
#         #level 1 -> crop_middle
#         #level 2, 3 -> crop_image2
#         #if (lst_level[n-1] == 1):
#         crop = crop_middle(gray, img_thresh)
#         #else :
#             #crop = crop_image2(gray, img_thresh)
#         resize = cv2.resize(crop,(28, 28), Image.ANTIALIAS)
#
#         #ret,thresh = cv2.threshold(resize,80,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#         skeleton3d = skeletonize_3d(resize)
#         edges = cv2.Canny(resize,28,28)
#         ar_im = np.asarray(resize)
#         ar_skeleton = np.asarray(skeleton3d)
#         ar_edges = np.asarray(edges)
#         stack = np.stack((ar_skeleton, ar_edges, ar_im), axis = 2)
#         cv2.imwrite('labels' + str(n) + '.png', stack)
#         #cv2.imshow('img', stack)
#         #cv2.waitKey(0)
#         #cv2.destroyAllWindows()
#
#
#
#
#
#     #--------------------predict------------------
#     class_char = []
#     for n in range(1, ret2):
#         image = cv2.imread('labels' + str(n) + '.png')
#         image = cv2.resize(image, (28, 28))
#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#         image = np.reshape(image, [1, 28, 28, 3])
#         if (lst_level[n - 1] == 1):
#             classes = model1.predict_classes(image)
#         elif (lst_level[n - 1] == 2):
#             classes = model2.predict_classes(image)
#             classes = classes + 70
#         else :
#             classes = model3.predict_classes(image)
#             classes = classes + 100
#         if (classes in [70,100]):   #add
#             classes = 61
#         class_char.append(int(classes))
#     #print(class_char)
#
#
#     #---------------------------------------------
#
#
#
#
#
#
#     #------------sort-------------
#     count = 0
#     big_vowel = [71,72,73,74,75]
#     for i in class_char:
#         #print(str(i) + ' --> ' + str(lst_level[count]))
#         if (lst_level[count] == 2):
#             if (class_char[count] in big_vowel ):
#                 #print('error')
#                 if (abs(lst_x2[count] - lst_x2[count + 1]) > abs(lst_x2[count + 2] - lst_x2[count + 1])):
#                     #print('Before = ' + str(lst_x2[count]))
#                     #print('After = ' + str(lst_x2[count + 2]))
#                     swap = class_char[count]
#                     #print(swap)
#                     class_char[count] = class_char[count + 1]
#                     class_char[count + 1] = swap
#         count = count + 1
#     print('line ' + str(t) + ' = ' + str(class_char))
#     real_class.extend(class_char)
#     if (t == 1):
#         real_class.append(1000)
#     print()
#
#
#
# #--------------------remove อำ---------------------
# swap_class = real_class
# real_class = []
# count = 0
# for i in swap_class:
#     if (i == 40):
#         if (swap_class[count - 1] == 81):
#             pass
#         else :
#             real_class.append(swap_class[count])
#     else :
#         real_class.append(swap_class[count])
#     count = count + 1
# '''
# #--------------------remove อะ---------------------
# a = [61, 70, 100]
# swap_class = real_class
# real_class = []
# count = 0
# for i in swap_class:
#     if (i == 61):
#         if (swap_class[count - 1] == 61):
#             real_class.remove(swap_class[count - 1])
#             real_class.append(200)
#         else :
#             real_class.append(swap_class[count])
#     else :
#         real_class.append(swap_class[count])
#     count = count + 1
# '''
# print(real_class)
# print()
#
#
# # -----------convert-----------------
# def num_to_char(real_class):
#     real_input = []
#     for i in real_class:
#         count = 0
#         for j in numclass:
#             if (i == j):
#                 real_input.append(charclass[count])
#             count = count + 1
#     print(real_input)
#     return (real_input)
#
#
# def char_to_num(real_class):
#     real_input = []
#     for i in real_class:
#         count = 0
#         for j in charclass:
#             if (i == j):
#                 real_input.append(numclass[count])
#             count = count + 1
#     print(real_input)
#
#
# #----------Save data--------------
# import pandas as pd
# df = pd.read_csv('database.csv', index_col=0)
#
# def add_data(box,real_class):
#     name = []
#     room = []
#     address = []
#     check = 0
#     for i in real_class:
#         if (i != 1000 and check == 0):
#             name.append(i)
#         elif (i == 1000):
#             check = 1
#         elif (i != 1000 and check == 1 and i in [47, 48, 49, 50, 51, 52, 53, 55, 56, 57, 58]):
#             room.append(i)
#         else:
#             address.append(i)
#     for n in range(len(name)):
#         df['name' + str(box)][n] = name[n]
#     for n in range(len(room)):
#         df['room' + str(box)][n] = room[n]
#     for n in range(len(address)):
#         df['address' + str(box)][n] = address[n]
#     num_to_char(name)
#     num_to_char(room)
#     num_to_char(address)
#
# # input_box = int(sys.argv[1])
# input_box = 1
# add_data(input_box,real_class)
# df.to_csv('database.csv')
#
#
# file = open('testfile.txt', 'w', encoding='utf8')
# real_class = num_to_char(real_class)
# for i in real_class:
#     file.write(i)
# file.close()