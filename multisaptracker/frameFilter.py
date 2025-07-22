import cv2
import numpy as np
from random import randint
import sort

def getBoundingBoxes(path, initialFrame):
    
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, initialFrame)
    success, frame = cap.read()
    
    result = frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    bboxArray = []
    colors = []
    #Esto solo es para el color rojo
    #Crear una funcion para sacar los valores minimos
    #del color que se quiere buscar, con ROI maybe.
    lwColor1 = np.array([0,70,30])
    upColor1 = np.array([10,255,255])
    lwColor2 = np.array([160,50,10])
    upColor2 = np.array([180,255,255])
    firstRange = cv2.inRange(frame, lwColor1, upColor1)
    secondRange = cv2.inRange(frame, lwColor2, upColor2)
    fullRange = firstRange + secondRange
    
    kernel = np.ones((5,5), np.uint8)
    openFrame = cv2.morphologyEx(fullRange, cv2.MORPH_OPEN, kernel)
    result = cv2.bitwise_and(result, result, mask=openFrame)
    
    bboxes, hierarchy = cv2.findContours(openFrame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in bboxes:
        moments = cv2.moments(c)
        x,y,w,h = cv2.boundingRect(c)
        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            newBbox = [cx - 5, cy - 5,
                       cx + 5, cy + 5]
            bboxArray.append(newBbox)
            colors.append([randint(0,255), randint(0,255), randint(0,255)])
            cv2.rectangle(openFrame, (x,y), (w+x,h+y), (255,255,255), 2)
            cv2.circle(openFrame, (cx,cy), 5, (0,0,0), -1)
    cv2.imshow('Show', openFrame); cv2.waitKey(0)
    bboxArray = np.array(bboxArray)
    cv2.destroyAllWindows()
    cap.release()
    return bboxArray, colors

def multiTrackerCSRT(path, bboxes, initialFrame, finalFrame, colorList):
    # Load and position of the video
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, initialFrame)
    success, frame = cap.read()
    
    # First modification
    # area_points = np.array([[1201,697],[1201,381],[767,381],[767,697]])
    # hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # auxImage = np.zeros(shape=(frame.shape[:2]), dtype=np.uint8)
    # auxImage = cv2.drawContours(auxImage, [area_points], -1, (255), -1)
    # newFrame = cv2.bitwise_and(hsvFrame, hsvFrame, mask=auxImage)
    
    # Multi tracker creation
    trackerType = cv2.legacy.TrackerCSRT_create()
    multiTracker = cv2.legacy.MultiTracker_create()
    for bbox in bboxes:
        multiTracker.add(trackerType, frame, bbox)
        
    # Updating MOT
    while cap.isOpened():
        success, frame = cap.read()
        # Frame modification
        # area_points = np.array([[1201,697],[1201,381],[767,381],[767,697]])
        # hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # auxImage = np.zeros(shape=(frame.shape[:2]), dtype=np.uint8)
        # auxImage = cv2.drawContours(auxImage, [area_points], -1, (255), -1)
        # newFrame = cv2.bitwise_and(hsvFrame, hsvFrame, mask=auxImage)
        if not success:
            print("Particle not found.")
            
        success, bboxes = multiTracker.update(frame)
        for j, newbox in enumerate(bboxes):
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, colorList[j], 2, 1)
        
        cv2.imshow('Multitracker', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
fullPath = "/Users/estudillo/Documents/Multiparticulas/video17captura_8.MP4"

boxes, colors = getBoundingBoxes(fullPath, 780)
multiTrackerCSRT(fullPath, boxes, 780, 980, colors)
# cap = cv2.VideoCapture(fullPath)
# cap.set(cv2.CAP_PROP_POS_FRAMES, 780)
# succes, frame = cap.read()
# tracker = sort.Sort()
# boxesid = []
# i=0
# newframe = np.ones((1080, 1920, 3), dtype=np.uint8)
# trays = {}
# while succes == True and i <= 200:
#     detections = getBoundingBoxes(frame)
#     objTracker = tracker.update(detections)
#     for x1,y1,x2,y2,trackid in objTracker:
#         cx = (x1+x2) / 2
#         cy = (y1+y2) / 2
#         trackid = int(trackid)
        
#         if trackid not in trays:
#             trays[trackid] = []
            
#         trays[trackid].append([cx, cy])
#         cv2.rectangle(newframe, (int(x1), int(y1)), (int(x2), int(y2)), (0,0,255), 2)
#         cv2.imshow("prueba", newframe)
#         cv2.waitKey(1)

#     succes, frame = cap.read()
#     i= i+1

# boxesid = np.array(boxesid)

