import numpy as np
import cv2
import time
import cv2.cv as cv
cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

# Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Display the resulting frame
    cv2.imshow('frame',frame)

#time.sleep(01)
    Capture = cv.CaptureFromCAM(0)
    time.sleep(5)
    ret, frame = cap.read()
    image = cv.QueryFrame(Capture) #here you have an IplImage
    imgarray = np.asarray(image[:,:]) #this is the way I use to convert it to numpy array

    cv2.imshow('capImage', imgarray)
    cv2.waitKey(0)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()