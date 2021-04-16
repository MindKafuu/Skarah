#----------Save data--------------
import pandas as pd
df = pd.read_csv('database.csv', index_col=0)


def add_data(box,real_class):
    name = []
    room = []
    address = []
    check = 0
    for i in real_class:
        if (i != 1000 and check == 0):
            name.append(i)
        elif (i == 1000 and check == 0):
            check = 1
        elif (i != 1000 and check == 1 and i in [47, 48, 49, 50, 51, 52, 53, 55, 56, 57, 58]):
            room.append(i)
        else:
            address.append(i)
    for n in range(len(name)):
        df['name' + str(box)][n] = name[n]
    for n in range(len(room)):
        df['room' + str(box)][n] = room[n]
    for n in range(len(address)):
        df['address' + str(box)][n] = address[n]
    num_to_char(name)
    num_to_char(room)
    num_to_char(address)


#real_class = [33, 54, 0, 26, 40, 15, 10, 80,1000,56, 50, 58, 55, 30, 10, 81, 40, 16, 28, 35, 70, 30, 26, 37, 37, 81, 40, 41, 22, 37,41, 24, 74, 37, 54, 62, 70, 54, 35, 30, 70, 9, 20, 71, 32, 8, 101, 42, 28, 0]

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
#-----------convert-----------------
def num_to_char(real_class):
    real_input = []
    for i in real_class:
        count = 0
        for j in numclass:
            if (i == j):
                real_input.append(charclass[count])
            count = count + 1
    print(real_input)

def char_to_num(real_class):
    real_input = []
    for i in real_class:
        count = 0
        for j in charclass:
            if (i == j):
                real_input.append(numclass[count])
            count = count + 1
    return (real_input)

#real_class = 'สงกรานต์-83/71 ตำบลหัวรอ อำเภอเมือง จังหวัดพิษณุโลก'
real_class = 'นนทพัตน์-47/71 วันดี'
#real_class = 'สุกี้หมู-73/15 ตราด'
#real_class = 'นนธพัตน์-96/12 ป่ากด'
real_class = char_to_num(real_class)

add_data(2,real_class)
df.to_csv('database.csv')
