from binascii import unhexlify
import serial
from array import *
import crc8
import sys
import InverseKine as invs

BAUDRATE = 9600
PORT = 'COM8'

microcontroller = serial.Serial()
microcontroller.baudrate = BAUDRATE
microcontroller.port = PORT
microcontroller.timeout = 1
microcontroller.dtr = 0
microcontroller.rts = 0

def SendProtocol(data):
    total = ""
    # print("in")
    for byte in range(len(data)):
        data[byte] = str(format( data[byte], '02x'))
        total = total + data[byte]
        data[byte] = int(data[byte],16)
    hash = crc8.crc8()
    hash.update(unhexlify(total))
    check = int(str(hash.hexdigest()),16)
    data.append(check)
    protocal = bytes(data)

    microcontroller.open()
    microcontroller.write(protocal)
    print("send")
    microcontroller.flush()
    print(data)
    while True:
        Read = microcontroller.readline().decode("utf-8")
        print(Read)
        # print("wait..")    
        if (Read == 'correctcheck\n') or (Read == 'nocheck\n') or (Read == 'sethome\n'):
            Check = Read
            print("Successed!")
            break
    microcontroller.close()
    return  Check

def SetProtocol(data):
    list = []
    set_data =[]
    for i in range(len(data)):
        list.insert(0,int(abs(data[i][0]) / 256))
        list.insert(1,abs(data[i][0]) % 256)
        list.insert(2,int(abs(data[i][1]) / 256))
        list.insert(3,abs(data[i][1]) % 256)
        list.insert(4,int(abs(data[i][2]) / 256))
        list.insert(5,abs(data[i][2]) % 256)
        list.insert(6,int(abs(data[i][3]) / 256))
        list.insert(7,abs(data[i][3]) % 256)
        if data[i][0] >= 0:
            list.insert(8,1)
        elif data[i][0] < 0:
            list.insert(8,0)
        if data[i][1] >= 0:
            list.insert(9,1)
        elif data[i][1] < 0:
            list.insert(9,0)
        if data[i][2] >= 0:
            list.insert(10,0)
        elif data[i][2] < 0:
            list.insert(10,1)
        if data[i][3] != 0:
            list.insert(11,1)
        elif data[i][3] == 0:
            list.insert(11,0)
        set_data.append(list)
        list = []
    return set_data

def OneProtocol(data):
    dl = [0,0,0,0,0,0,0,0,0,0,0]
    dl[0] = 0
    dl[1] = int(data[0])
    dl[2] = 0
    dl[3] = int(data[1])
    dl[4] = 0
    dl[5] = int(data[2])
    dl[6] = 0
    dl[7] = int(data[3])
    
    dl[8] = int(data[0])
    dl[9] = int(data[1])
    dl[10] = int(data[2])

    if dl[8] < 0:
        dl[8] = 0
    elif dl[8] >= 0:
        dl[8] = 1
    if dl[9] < 0:
        dl[9] = 0
    elif dl[9] >= 0:
        dl[9] = 1
    if dl[10] < 0:
        dl[10] = 1
    elif dl[10] >= 0:
        dl[10] = 0

    for i in range(0, 8):
        if(dl[i] > 255):
            s = int(abs(dl[i]) / 256)
            dl[i] = int(abs(dl[i]) % 256)
            dl[i - 1] = s
            # print(dl[i], dl[i - 1])
        else:
            dl[i] = abs(dl[i])
 
    return dl

def SentPositionStep(set_data):
    for i in range(len(set_data)):
        data = set_data[i]
        Check = SendProtocol(data)
        while Check == "nocheck\n":
            data = set_data[i]
            Check = SendProtocol(data)

data = [0,0,0,0,0,0,0,0,0,0,0,0]
data_invs = [0, 0, 0]
# SendProtocol(data)

if(len(sys.argv) > 8):
    # แก้ฝั่ง UI 
    data[0] = int(sys.argv[1])
    data[1] = int(sys.argv[2])
    data[2] = int(sys.argv[3])
    data[3] = int(sys.argv[4])
    data[4] = int(sys.argv[5])
    data[5] = int(sys.argv[6])
    data[6] = int(sys.argv[7])
    data[7] = int(sys.argv[8])
    data[8] = int(sys.argv[9])
    data[9] = int(sys.argv[10])
    data[10] = int(sys.argv[11])
    data[11] = int(sys.argv[12])
    microcontroller.port = sys.argv[13]
    print(data)
    SendProtocol(data)
else:
    # print("mind")
    data_invs[0] = int(sys.argv[1])
    data_invs[1] = int(sys.argv[2])
    data_invs[2] = int(sys.argv[3])
    gripper = int(sys.argv[4])
    servo = int(sys.argv[5])
    microcontroller.port = sys.argv[6]

    result = invs.inverseKine(data_invs, gripper)
    package = OneProtocol(result)
    package.append(servo)
    print(data_invs, gripper)
    print(package)
    SendProtocol(package)

# print(send)
#รอบ 1
# dataIn = [[23, 0, 98, 75],
#         [0, -12, 0, 75],
#         [0, 15, 0, 75],
#         [110, 0, -98, 75]]
# #รอบ 2 - 7
# dataOut = [[-110, 0, 98, 75],
#             [0, -20, 0, 75],
#             [0, 15, 0, 75],
#             [110, 0, -98, 75]]

# SentPositionStep(SetProtocol(dataOut))
# print(data)
# data = [0,0,0,0,0,0,0,0,0,0,0,0]
# servo = 1
# result = invs.inverseKine([570, -270, 100], 0)
# send = OneProtocol(result)
# send.append(servo)
# print(send)
# print(SendProtocol(send))