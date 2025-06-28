import cv2
import numpy as np

def colorChange(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #Esto solo es para el color rojo
    #Crear una funcion para sacar los valores minimos
    #del color que se quiere buscar, con ROI maybe.
    lwColor1 = np.array([0,50,20])
    upColor1 = np.array([10,255,255])
    lwColor2 = np.array([150,50,20])
    upColor2 = np.array([180,255,255])
    firstRange = cv2.inRange(frame, lwColor1, upColor1)
    secondRange = cv2.inRange(frame, lwColor2, upColor2)
    fullRange = firstRange + secondRange
    
    kernel = np.ones((5,5), np.uint8)
    openFrame = cv2.morphologyEx(fullRange, cv2.MORPH_OPEN, kernel)
    
    bboxes, hierarchy = cv2.findContours(openFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in bboxes:
        moments = cv2.moments(c)
        x,y,w,h = cv2.boundingRect(c)
        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            cv2.rectangle(openFrame, (x,y), (w+x,h+y), (255,255,255), 2)
            cv2.circle(openFrame, (cx,cy), 5, (0,0,0), -1)
    
    cv2.imshow("fullrange", openFrame)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

fullPath = "/Users/estudillo/Documents/Multiparticulas/video17captura_8.MP4"

cap = cv2.VideoCapture(fullPath)
cap.set(cv2.CAP_PROP_POS_FRAMES, 590)
_, frame = cap.read()
colorChange(frame)