
import glob
import os
import random
import sys
import random
import math
import json
from collections import defaultdict

import cv2
from PIL import Image, ImageDraw
import numpy as np
from scipy.ndimage.filters import rank_filter

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,1024)
cv2.namedWindow("test")
img_counter = 0

def dilate(ary, N, iterations):
    """Dilate using an NxN '+' sign shape. ary is np.uint8."""

    kernel = np.zeros((N, N), dtype=np.uint8)
    kernel[(N - 1) // 2, :] = 1  # Bug solved with // (integer division)

    dilated_image = cv2.dilate(ary / 255, kernel, iterations=iterations)

    kernel = np.zeros((N, N), dtype=np.uint8)
    kernel[:, (N - 1) // 2] = 1  # Bug solved with // (integer division)
    dilated_image = cv2.dilate(dilated_image, kernel, iterations=iterations)
    return dilated_image


def props_for_contours(contours, ary):
    """Calculate bounding box & the number of set pixels for each contour."""
    c_info = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        c_im = np.zeros(ary.shape)
        cv2.drawContours(c_im, [c], 0, 255, -1)
        c_info.append({
            'x1': x,
            'y1': y,
            'x2': x + w - 1,
            'y2': y + h - 1,
            'sum': np.sum(ary * (c_im > 0)) / 255
        })
    return c_info


def union_crops(crop1, crop2):
    """Union two (x1, y1, x2, y2) rects."""
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    return min(x11, x12), min(y11, y12), max(x21, x22), max(y21, y22)


def intersect_crops(crop1, crop2):
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    return max(x11, x12), max(y11, y12), min(x21, x22), min(y21, y22)


def crop_area(crop):
    x1, y1, x2, y2 = crop
    return max(0, x2 - x1) * max(0, y2 - y1)


def find_border_components(contours, ary):
    borders = []
    area = ary.shape[0] * ary.shape[1]
    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 0.5 * area:
            borders.append((i, x, y, x + w - 1, y + h - 1))
    return borders


def angle_from_right(deg):
    return min(deg % 90, 90 - (deg % 90))


def remove_border(contour, ary):
    """Remove everything outside a border contour."""
    # Use a rotated rectangle (should be a good approximation of a border).
    # If it's far from a right angle, it's probably two sides of a border and
    # we should use the bounding box instead.
    c_im = np.zeros(ary.shape)
    r = cv2.minAreaRect(contour)
    degs = r[2]
    if angle_from_right(degs) <= 10.0:
        box = cv2.boxPoints(r)
        box = np.int0(box)
        cv2.drawContours(c_im, [box], 0, 255, -1)
        cv2.drawContours(c_im, [box], 0, 0, 4)
    else:
        x1, y1, x2, y2 = cv2.boundingRect(contour)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 255, -1)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 0, 4)

    return np.minimum(c_im, ary)


def find_components(edges, max_components=16):
    """Dilate the image until there are just a few connected components.

    Returns contours for these components."""
    # Perform increasingly aggressive dilation until there are just a few
    # connected components.

    count = 21
    dilation = 5
    n = 1
    while count > 16:
        n += 1
        dilated_image = dilate(edges, N=3, iterations=n)
        dilated_image = np.uint8(dilated_image)
        contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        count = len(contours)
    # print dilation
    # Image.fromarray(edges).show()
    # Image.fromarray(255 * dilated_image).show()
    return contours


def find_optimal_components_subset(contours, edges):
    """Find a crop which strikes a good balance of coverage/compactness.

    Returns an (x1, y1, x2, y2) tuple.
    """
    c_info = props_for_contours(contours, edges)
    c_info.sort(key=lambda x: -x['sum'])
    total = np.sum(edges) / 255
    area = edges.shape[0] * edges.shape[1]

    c = c_info[0]
    del c_info[0]
    this_crop = c['x1'], c['y1'], c['x2'], c['y2']
    crop = this_crop
    covered_sum = c['sum']

    while covered_sum < total:
        changed = False
        recall = 1.0 * covered_sum / total
        prec = 1 - 1.0 * crop_area(crop) / area
        f1 = 2 * (prec * recall / (prec + recall))
        # print '----'
        for i, c in enumerate(c_info):
            this_crop = c['x1'], c['y1'], c['x2'], c['y2']
            new_crop = union_crops(crop, this_crop)
            new_sum = covered_sum + c['sum']
            new_recall = 1.0 * new_sum / total
            new_prec = 1 - 1.0 * crop_area(new_crop) / area
            new_f1 = 2 * new_prec * new_recall / (new_prec + new_recall)

            # Add this crop if it improves f1 score,
            # _or_ it adds 25% of the remaining pixels for <15% crop expansion.
            # ^^^ very ad-hoc! make this smoother
            remaining_frac = c['sum'] / (total - covered_sum)
            new_area_frac = 1.0 * crop_area(new_crop) / crop_area(crop) - 1
            if new_f1 > f1 or (
                            remaining_frac > 0.25 and new_area_frac < 0.15):
                # print('%d %s -> %s / %s (%s), %s -> %s / %s (%s), %s -> %s' % (
                #     i, covered_sum, new_sum, total, remaining_frac,
                #     crop_area(crop), crop_area(new_crop), area, new_area_frac,
                #     f1, new_f1))
                crop = new_crop
                covered_sum = new_sum
                del c_info[i]
                changed = True
                break

        if not changed:
            break

    return crop


def pad_crop(crop, contours, edges, border_contour, pad_px=15):

    bx1, by1, bx2, by2 = 0, 0, edges.shape[0], edges.shape[1]
    if border_contour is not None and len(border_contour) > 0:
        c = props_for_contours([border_contour], edges)[0]
        bx1, by1, bx2, by2 = c['x1'] + 5, c['y1'] + 5, c['x2'] - 5, c['y2'] - 5

    def crop_in_border(crop):
        x1, y1, x2, y2 = crop
        x1 = max(x1 - pad_px, bx1)
        y1 = max(y1 - pad_px, by1)
        x2 = min(x2 + pad_px, bx2)
        y2 = min(y2 + pad_px, by2)
        return crop

    crop = crop_in_border(crop)

    c_info = props_for_contours(contours, edges)
    changed = False
    for c in c_info:
        this_crop = c['x1'], c['y1'], c['x2'], c['y2']
        this_area = crop_area(this_crop)
        int_area = crop_area(intersect_crops(crop, this_crop))
        new_crop = crop_in_border(union_crops(crop, this_crop))
        if 0 < int_area < this_area and crop != new_crop:
            # print('%s -> %s' % (str(crop), str(new_crop)))
            changed = True
            crop = new_crop

    if changed:
        return pad_crop(crop, contours, edges, border_contour, pad_px)
    else:
        return crop


def downscale_image(im, max_dim=2048):

    a, b = im.size
    if max(a, b) <= max_dim:
        return 1.0, im

    scale = 1.0 * max_dim / max(a, b)
    new_im = im.resize((int(a * scale), int(b * scale)), Image.ANTIALIAS)
    return scale, new_im


def process_image(path):
    orig_im = Image.open(path)
    scale, im = downscale_image(orig_im)

    edges = cv2.Canny(np.asarray(im), 100, 200)

    # TODO: dilate image _before_ finding a border. This is crazy sensitive!
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    borders = find_border_components(contours, edges)
    borders.sort(
        key=lambda i_x1_y1_x2_y2: (i_x1_y1_x2_y2[3] - i_x1_y1_x2_y2[1]) * (i_x1_y1_x2_y2[4] - i_x1_y1_x2_y2[2]))

    border_contour = None
    if len(borders):
        border_contour = contours[borders[0][0]]
        edges = remove_border(border_contour, edges)

    edges = 255 * (edges > 0).astype(np.uint8)

    # Remove ~1px borders using a rank filter.
    maxed_rows = rank_filter(edges, -4, size=(1, 20))
    maxed_cols = rank_filter(edges, -4, size=(20, 1))
    debordered = np.minimum(np.minimum(edges, maxed_rows), maxed_cols)
    edges = debordered

    contours = find_components(edges)
    # if len(contours) == 0:
    #     print('%s -> (no text!)' % path)
    #     return

    crop = find_optimal_components_subset(contours, edges)
    crop = pad_crop(crop, contours, edges, border_contour)

    crop = [int(x / scale) for x in crop]  # upscale to the original image size.

    text_im = orig_im.crop(crop)

    open_cv_image = np.array(text_im)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    # print(open_cv_image)

    #text_im.save(out_path)
    cv2.imshow('open_cv_image',open_cv_image)
    cv2.imwrite('imagePredict.png', open_cv_image)
    cv2.waitKey(500)

def capture():
    while True:
        ret, frame = cam.read()

        cv2.imshow("test", frame)
        if not ret:
            break
        # cv2.waitKey(5000)
        k = cv2.waitKey(1)
        if k % 256 == 32:
            # SPACE pressed
            cv2.imwrite("image.png", frame)
            break
    return True

    cam.release()


a = capture()
if a:
    process_image('image.png')
    print("E")

# process_image('image12.png')









from matplotlib import pyplot as plt
import pylab
import cv2
import numpy as np
from skimage.morphology import medial_axis, skeletonize, skeletonize_3d
from PIL import Image
import sys


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





from matplotlib import pyplot as plt
import pylab
import cv2
import numpy as np
from skimage.morphology import medial_axis, skeletonize, skeletonize_3d
from PIL import Image

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
cv2.waitKey(1000)

#ret,img = cv2.threshold(img,40,255,cv2.THRESH_BINARY_INV)#binary
img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,19,16)
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

cv2.imshow('threshold.png', img)
cv2.waitKey(1500)



img = np.transpose(img)
#---------Histogram Projection---------------
(rows,cols)=img.shape
h_projection = np.array([ x/255/rows for x in img.sum(axis=0)])
plt.plot(range(cols), h_projection.T)
#plt.show()

#--------Line segmentation--------
img = np.transpose(img)
count = 0
count2 = 0
num = 0
blank_space = []

while (count < cols):
    if (h_projection[count] > 0.02):
        num = num + 1
        lst = []
        lst.append(img[count - 1])
        while (True):
            lst.append(img[count])
            count = count + 1
            if (count >= cols):
                break
            else :
                if (h_projection[count] == 0):
                    if (count2 < 6):       #distance of character
                        count2 = count2 + 1
                    else :
                        break
                else :
                    count2 = 0
        lst = np.array(lst)
        cv2.imwrite(str(num) + '.png', lst)
        #cv2.imshow('line' + str(num) + '.png', lst)
        cv2.waitKey(1000)
    if (count2 > 0):
        blank_space.append(count2)
    count2 = 0
    count = count + 1
print(blank_space)

#-------Crop------------
for i in range(1 ,num + 1):
    im = []
    img = cv2.imread(str(i) + '.png',0)
    y, x = img.shape
    for n in range(y - blank_space[i-1] + 0):
        im.append(img[n])
    im = np.array(im)
    cv2.imwrite(str(i) + '.png', im)
    cv2.imshow(str(i) + '.png', im)
    cv2.waitKey(1000)








#-------------------delete noise-------------
for i in range(1 ,num + 1):
    img = cv2.imread(str(i) + '.png',0)
    #---------Histogram Projection---------------
    (rows,cols)=img.shape
    h_projection = np.array([ x/255/rows for x in img.sum(axis=0)])
    plt.plot(range(cols), h_projection.T)
    #plt.show()
    #--------Line segmentation--------
    img = np.transpose(img)
    count = 0
    count2 = 0
    num2 = 0
    blank_space = []
    while (count < cols):
        if (h_projection[count] > 0.2):
            num2 = num2 + 1
            lst = []
            lst.append(img[count - 1])
            while (True):
                lst.append(img[count])
                count = count + 1
                if (count >= cols):
                    break
                else :
                    if (h_projection[count] == 0):
                        if (count2 < 50):       #distance of character
                            count2 = count2 + 1
                        else :
                            break
                    else :
                        count2 = 0
            lst = np.transpose(lst)
            lst = np.array(lst)
            cv2.imwrite(str(i) + '.png', lst)
            cv2.imshow(str(i) + '.png', lst)
            cv2.waitKey(1000)
        count2 = 0
        count = count + 1
#-----------------------------------------







#---------Character segmentation------------
real_class = []
for t in range(1 ,num + 1):

    img = cv2.imread(str(t) + '.png', 0)
    img = np.transpose(img)
    ret, labels = cv2.connectedComponents(img)

    x, y = labels.shape
    middle_y = int(y/2) + 5
    n = x*y
    n = np.arange(n)

    im = []
    lst_x = []
    lst_y = []
    lst_sort = []
    for i in range(1,ret):
        b = np.array(labels)
        b = b.flatten()
        b = np.array(b, dtype=np.uint8)
        b[n[b!=i]] = 0
        b = b.reshape(x, y)
        b = b*255

        a = True
        c = 0
        count_x = 0
        for r in b:
            if (a == True):
                count_y = 0
                count_x = count_x + 1
                for j in r:
                    if (j == 0):
                        count_y = count_y + 1
                    else:
                        c = c + 1
                        if (c == 6):            #########
                            a = False
                            break
            else:
                break
        lst_sort.append(count_x)
        lst_x.append(count_x)
        lst_y.append(count_y)
        b = np.transpose(b)
        im.append(b)
        cv2.imwrite('labels' + str(i) + '.png', b)
        #cv2.imshow('labeled.png', b)
        #cv2.waitKey()
    #print('x = ' + str(lst_x))
    #print('y = ' + str(lst_y))



    #--------Find level of charecter---------
    lst_level = []
    check = True
    for n in range(1, ret):
        img = cv2.imread('labels' + str(n) + '.png', 0)
        for i in img[middle_y]:
            if (i != 0):
                check = True
                level = 1
                lst_level.append(1)
                break
            else :
                check = False
        if (check == False):
            if (lst_y[n-1] < middle_y):
                level = 2
                lst_level.append(2)
            else :
                level = 3
                lst_level.append(3)
    print('level = ' + str(lst_level))


    lst_x2 = []
    lst_x2.append(0)
    lst_x2.extend(lst_x)
    lst_x2.append(0)
    #print(lst_x2)
    #-------------crop---------------
    ret2 = ret
    for n in range(1, ret):
        im = cv2.imread('labels' + str(n) + '.png')
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret,img_thresh = cv2.threshold(gray,80,255,cv2.THRESH_BINARY)
        #level 1 -> crop_middle
        #level 2, 3 -> crop_image2
        #if (lst_level[n-1] == 1):
        crop = crop_middle(gray, img_thresh)
        #else :
            #crop = crop_image2(gray, img_thresh)
        resize = cv2.resize(crop,(28, 28), Image.ANTIALIAS)

        #ret,thresh = cv2.threshold(resize,80,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        skeleton3d = skeletonize_3d(resize)
        edges = cv2.Canny(resize,28,28)
        ar_im = np.asarray(resize)
        ar_skeleton = np.asarray(skeleton3d)
        ar_edges = np.asarray(edges)
        stack = np.stack((ar_skeleton, ar_edges, ar_im), axis = 2)
        cv2.imwrite('labels' + str(n) + '.png', stack)
        #cv2.imshow('img', stack)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()