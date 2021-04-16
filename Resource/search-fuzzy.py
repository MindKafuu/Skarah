import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
import sys
from fuzzywuzzy import process

def delete_data(box):
    for n in range(200):
        df['name'+str(box)][n] = np.nan
        df['room' + str(box)][n] = np.nan
        df['address' + str(box)][n] = np.nan

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
df = pd.read_csv('database.csv', index_col=0)


input_class = sys.argv[1]



#print(df['name3'])





#-----------convert-----------------
real_input = []
for i in input_class:
    count = 0
    for j in charclass:
        if (i == j):
            real_input.append(numclass[count])
        count = count + 1
print(real_input)


box_accuracy = []
count = 1
for i in df:
    box_data = []
    for j in df[i]:
        if (str(j) != 'nan'):
            box_data.append(int(j))
    accuracy = fuzz.token_sort_ratio(box_data, real_input)
    box_accuracy.append(accuracy)
    # print('box' + str(count) + ' = ' + str(box_data))
    # print(str(accuracy) + '%')
    # print()
    count = count + 1


m = max(box_accuracy)
count = 1
for i in box_accuracy:
    if (i == m):
        box = count
        box = box % 14
    count = count +1
if (box == 0):
    box = 14




print('box' + str(box))

delete_data(box)
df.to_csv('database.csv')
print("E")