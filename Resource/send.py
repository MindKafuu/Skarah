import crc8
from binascii import unhexlify
import serial
from array import *
import sys

def crc(data):
    total = ""
    for byte in range(len(data)):
        data[byte] = str(format( data[byte], '02x'))
        total = total + data[byte]
        data[byte] = int(data[byte],16)
    hash = crc8.crc8()
    hash.update(unhexlify(total))
    check = int(str(hash.hexdigest()),16)
    data.append(check)
    return data

def SendProtocal(data):
    BAUDRATE = 9600
    PORT = 'COM8'
    microcontroller = serial.Serial()
    microcontroller.baudrate = BAUDRATE
    microcontroller.port = PORT
    microcontroller.timeout = 1
    microcontroller.dtr = 0
    microcontroller.rts = 0

    data = crc(data)
    protocal = bytes(data)

    microcontroller.open()
    microcontroller.write(protocal)
    print("send")
    microcontroller.flush()
    print(data)
    microcontroller.close()

def OneProtocal(data):
    list = []
    list.insert(0, 0)
    list.insert(1, 0)
    list.insert(2, 0)
    list.insert(3, 0)
    list.insert(4, 0)
    list.insert(5, 0)
    list.insert(6, 0)
    list.insert(7, 0)
    list.insert(8, 0)
    list.insert(9,  data[0])
    if data[1] == 1 or data[1] == 3 or data[1] == 5:
        list.insert(10, 1)
    elif data[1] == 2 or data[1] == 4 or data[1] == 6:
        list.insert(10, 2)
    elif data[1] == 7 or data[1] == 9 or data[1] == 11 or data[1] == 13:
        list.insert(10, 3)
    elif data[1] == 8 or data[1] == 10 or data[1] == 12 or data[1] == 14:
        list.insert(10, 4)
    list.insert(11, data[1])
    return list


def SentPosition(data):
    set = OneProtocal(data)
    #print(crc(set))
    SendProtocal(set)


#ส่งมาแค่ว่าจะ in หรือ out 253, 254
#ส่งที่อยู่กล่อง

status = int(sys.argv[1])
box = int(sys.argv[2])
print(box)
data = [status, box]
SentPosition(data)
print("E")