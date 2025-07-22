import cv2
import pandas as pd
import numpy as np
import numpy.random as npr
import matplotlib.pyplot as plt

def randomColors(size):
    colors = [None] * size
    for i in range(size):
        colors[i] = (npr.randint(0,256), npr.randint(0,256), npr.randint(0,256))

    return colors

def liveTracking(fps: int, frame: cv2.typing.MatLike, coordinates: np.ndarray, bboxes: tuple, colors: list):
    """Shows the tracking in real-time by painting the points computed by the
    tracker in red and the bounding box in white.

    Parameters
    ----------
    fps : int
        Frame number of the video.
    frame : str
        Current frame used by the tracker.
    coordinates : np.ndarray
        Array of the points computed by the tracker.
    bboxes : tuple
        Bounding box of the particle in the current frame.
    """    
    windowN = "Tracking"
    font = cv2.FONT_HERSHEY_SIMPLEX
    pts = [None] * len(bboxes)
    p1 = [None] * len(bboxes)
    p2 = [None] * len(bboxes)
    for i, points in enumerate(coordinates):
        pts[i] = np.array(points, dtype=np.int32)
        
    for j, boundingbox in enumerate(bboxes):
        p1[j] = (int(boundingbox[0]), int(boundingbox[1]))
        p2[j] = (int(boundingbox[0]+boundingbox[2]), int(boundingbox[1]+boundingbox[3]))
    
    for k in range(len(bboxes)):
        cv2.polylines(frame, [pts[k]], isClosed= False, color=colors[k], thickness=2)
        cv2.rectangle(frame, p1[k], p2[k], colors[k], 2, 1)
    
    cv2.namedWindow(windowN, cv2.WINDOW_NORMAL)
    cv2.putText(frame, 'MultiTracker', (200,30), font, 1, (0,255,0), 2)
    cv2.putText(frame, 'Frame: ', (200,70), font, 1, (0,255,0), 2)
    cv2.putText(frame, str(fps), (335,70), font, 1, (0,255,0), 2)
    cv2.namedWindow(windowN, cv2.WINDOW_NORMAL)
    cv2.moveWindow(windowN, 179, 139)    
    cv2.resizeWindow(windowN, (1280,720))
    cv2.imshow(windowN, frame)    
    cv2.waitKey(1)

def circleShapeROI(frame):
    roi = np.zeros(frame.shape[:2], np.uint8)
    roi = cv2.circle(roi, (970, 555), 360, 255, cv2.FILLED)
    mask = np.ones_like(frame) * 255
    mask = cv2.bitwise_and(mask, frame, mask=roi) 
    
    return mask

def multiBoundingBoxes(path, initial_fps, show = False):
    capture = cv2.VideoCapture(path)
    capture.set(cv2.CAP_PROP_POS_FRAMES, initial_fps)
    success, frame = capture.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lwColor1 = np.array([0,70,30])
    upColor1 = np.array([10,255,255])
    lwColor2 = np.array([160,50,10])
    upColor2 = np.array([180,255,255])
    firstRange = cv2.inRange(frame, lwColor1, upColor1)
    secondRange = cv2.inRange(frame, lwColor2, upColor2)
    fullRange = firstRange + secondRange
    kernel = np.ones((8,8), np.uint8)
    openFrame = cv2.morphologyEx(fullRange, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(openFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Create a list of None elements with same size of 'contours'
    bboxes = [None]* len(contours)
    for i, c in enumerate(contours):
        bboxes[i] = cv2.boundingRect(c)
    
    if show == True:
     for i in range(len(contours)):
        color = (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0,256))
        cv2.rectangle(openFrame, (int(bboxes[i][0]), int(bboxes[i][1])),
                        (int(bboxes[i][0]+bboxes[i][2]), int(bboxes[i][1]+bboxes[i][3])), color, 2)
     print(len(bboxes))
     plt.imshow(frame)
     plt.show()
    
    return bboxes

def findingMoments(frame, boxes):
    centers = []
    areas = []
    print("-----------")
    add = 15
    boxes = np.array(boxes, dtype=np.uint16)
    for box in boxes:
        # Mask creation
        roi = np.zeros(frame.shape[:2], np.uint8)
        mask = np.ones_like(frame) * 255
        p1 = (box[0] - add,box[1] - add)
        p2 = (box[0] + box[2] + add, box[1] + box[3] + add)
        roi = cv2.rectangle(roi, p1, p2, (255,255,255), -1)
        masked = cv2.bitwise_and(mask, frame, mask=roi)
        
        # Red color filter
        hsvFrame = cv2.cvtColor(masked, cv2.COLOR_BGR2HSV)
        # This lowers and uppers are only for red color in HSV
        lwColor1 = np.array([0,70,30])
        upColor1 = np.array([10,255,255])
        lwColor2 = np.array([160,50,10])
        upColor2 = np.array([180,255,255])
        firstRange = cv2.inRange(hsvFrame, lwColor1, upColor1)
        secondRange = cv2.inRange(hsvFrame, lwColor2, upColor2)
        fullRange = firstRange + secondRange
        kernel = np.ones((5,5), np.uint8)
        openFrame = cv2.morphologyEx(fullRange, cv2.MORPH_OPEN, kernel)

        # Finding center with moments
        contours, _ = cv2.findContours(openFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for j in contours:
            # print(cv2.contourArea(j))
            if cv2.contourArea(j) > 100:
                moments = cv2.moments(j)
                if moments["m00"] != 0:
                    x = moments["m10"] / moments["m00"]
                    y = moments["m01"] / moments["m00"]
                    point = np.array([x, y])
                    centers.append(point)
                areas.append([cv2.contourArea(j)])
    print(np.mean(areas), np.std(areas), np.max(areas), np.min(areas))
    return centers

def findingMoments2(frame, box):
    box = np.array(box, dtype=np.uint16)
    # Mask creation
    roi = np.zeros(frame.shape[:2], np.uint8)
    mask = np.ones_like(frame) * 255
    p1 = (box[0]-5,box[1]-5)
    p2 = (box[0]+box[2]+5, box[1]+box[3]+5)
    roi = cv2.rectangle(roi, p1, p2, (255,255,255), -1)
    masked = cv2.bitwise_and(mask, frame, mask=roi)
    
    # Red color filter
    hsvFrame = cv2.cvtColor(masked, cv2.COLOR_BGR2HSV)
    # This lowers and uppers are only for red color in HSV
    lwColor1 = np.array([0,70,30])
    upColor1 = np.array([10,255,255])
    lwColor2 = np.array([160,50,10])
    upColor2 = np.array([180,255,255])
    firstRange = cv2.inRange(hsvFrame, lwColor1, upColor1)
    secondRange = cv2.inRange(hsvFrame, lwColor2, upColor2)
    fullRange = firstRange + secondRange
    kernel = np.ones((5,5), np.uint8)
    openFrame = cv2.morphologyEx(fullRange, cv2.MORPH_OPEN, kernel)
    # cv2.imshow("prueba", openFrame)
    # cv2.waitKey(0)
    # Finding center with moments
    contours, _ = cv2.findContours(openFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print(len(contours))
    # exit()
    point = np.array([0, 0])
    for j in contours:
        if cv2.contourArea(j) >= 30:
            (x,y), r = cv2.minEnclosingCircle(j)
            point = np.array([x, y])
    # for j in contours:
    #     moments = cv2.moments(j)
    #     if moments["m00"] != 0:
    #         x = moments["m10"] / moments["m00"]
    #         y = moments["m01"] / moments["m00"]
    #         point = np.array([x, y])

    return point
    
def multiTracker(path: str, initial_fps: int, bboxes: tuple, final_frame: int = 0,
                 irl: bool = False):
    
    capture = cv2.VideoCapture(path)
    capture.set(cv2.CAP_PROP_POS_FRAMES, initial_fps)
    success, frame = capture.read()
    count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = initial_fps
    deb = 0
    
    random_colors = randomColors(len(bboxes))
    num_part = len(bboxes)
    particle_trajectories = [[] for _ in range(num_part)]
    
    multitracker = cv2.legacy.MultiTracker_create()
    for box in bboxes:
        multitracker.add(cv2.legacy.TrackerCSRT_create(), frame, box)

    while fps < count:
        # if(deb % 50 == 0):
            # print(str(deb))
        #Obtaining coordinate from every bbox
        # for i, box in enumerate(bboxes):
        #     X = (box[0]+box[0]+box[2])/2
        #     Y = (box[1]+box[1]+box[3])/2
        #     new_position = np.array([X, Y])
        #     particle_trajectories[i].append(new_position)
        # PARA LOS MOMENTOS USAR EL FOR DE ARRIBA Y HACER LA FUNCION PARA UN BOX POR BOX
        # New way to get coords
        # deb = deb + 1
        # print(len(bboxes))
        # for k, box in enumerate(bboxes):
        #     pos = findingMoments2(frame, box)
        #     particle_trajectories[k].append(pos)
        pos = findingMoments(frame, bboxes)
        print(len(pos))
        for k in range(len(pos)):
            particle_trajectories[k].append(pos[k])
        #Current frame
        fps = int(capture.get(cv2.CAP_PROP_POS_FRAMES))
        success_frame, frame = capture.read()
        
        if success_frame == True:
          if fps == final_frame:
            break

          # Updating the tracker variable
          success_track, bboxes = multitracker.update(frame)
        
          # Shows the tracking in real time
          if success_track is True:
            if irl == True:
                liveTracking(fps, frame, particle_trajectories, bboxes, random_colors)
        
            continue
    
          if success_track is not True:
            print('An error was detected while tracking the particle.')
            break
    
        else:
            break
    capture.release()
    
    return particle_trajectories

def plotting(data):
    for i in range(10):
        plt.plot(data["Frame"], data[f"X_{i}"])
    
    plt.show()

video_path = "/Users/estudillo/Documents/Multiparticulas/Videos/"
video_name = "Experimento_08.MP4"
full_path = video_path + video_name
name_data = "Prueba.csv"
full_data = "/Users/estudillo/Documents/Multiparticulas/Trackings/" + name_data
ini_frame = 1300
fin_frame = 1500
# EN LUGAR DE USAR EL MULTITRACK, CREAR UN ARRAY DE TRACKERS
# trackers = [cv2.TrackerCSRT_create() for _ in range(num_part)]
# LUEGO POR CADA FRAME (o X frames) VERIFICAR QUE LA BB NO ESTE TAN DESPLAZADA
# COLOCANDO UN MARGEN DE ERROR TOMANDO LA DISTANCIA ENTRE CENTROS DE LA BB ANTERIOR
# Y LA BB ACTUAL. PARA EVITAR QUE SE PIERDA LA PARTICULA O QUE NO CAMBIE DE OBJETIVO EL TRACKER
# USAR LO DE LAS DISTANCIAS DE CENTROS O HACER QUE EL MASK SOLO DETECTE LA PARTICULA DESEADA.
bboxes = multiBoundingBoxes(full_path, ini_frame)
tracking_list = multiTracker(full_path, ini_frame, bboxes, fin_frame, True)
tracks = np.array(tracking_list)
# Guardado en un dataFrame
numParticles, numFrames, aux = tracks.shape
data = {}

for id in range(numParticles):
    data[f"X_{id}"] = tracks[id, :, 0]
    data[f"Y_{id}"] = tracks[id, :, 1]

df = pd.DataFrame(data)
df.insert(0, "Frame", np.arange(numFrames))
plotting(df)

df.to_csv(full_data)

    

