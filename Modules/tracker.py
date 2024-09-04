"""
Created on Monday March 20 2023 23:16 GMT-6
Autor:Alberto Estudillo Moreno 
Last modification: Monday January 15 2024 0:13 GMT-6

Using autobbox module
"""

import numpy as np
import pandas as pd
import cv2
import time
import matplotlib.pyplot as plt


def liveTracking(fps: int, frame:str, points: np.ndarray, boundingbox: tuple):
    """Shows the tracking in real-time by painting the points computed by the
    tracker in red and the bounding box in white.

    Parameters
    ----------
    fps : int
        Frame number of the video.
    frame : str
        Current frame used by the tracker.
    points : np.ndarray
        Array of the points computed by the tracker.
    boundingbox : tuple
        Bounding box of the particle in the current frame.
    """    
    windowN = "Tracking"
    font = cv2.FONT_HERSHEY_SIMPLEX
    pts=np.array(points, dtype=np.int32)
    p1 = (int(boundingbox[0]), int(boundingbox[1]))
    p2 = (int(boundingbox[0]+boundingbox[2]), int(boundingbox[1]+boundingbox[3]))
    
    cv2.polylines(frame, [pts], isClosed= False, color=(0,0,255), thickness=2)
    cv2.rectangle(frame, p1, p2, (255,255,255), 2, 1)
    
    cv2.namedWindow(windowN, cv2.WINDOW_NORMAL)
    cv2.putText(frame, 'Tracker V1.12?', (200,30), font, 1, (0,255,0), 2)
    cv2.putText(frame, 'Frame: ', (200,70), font, 1, (0,255,0), 2)
    cv2.putText(frame, str(fps), (335,70), font, 1, (0,255,0), 2)
    cv2.namedWindow(windowN, cv2.WINDOW_NORMAL)
    cv2.moveWindow(windowN, 179, 139)    
    cv2.resizeWindow(windowN, (1280,720))
    cv2.imshow(windowN, frame)    
    cv2.waitKey(1)
    
def getRotation(video_path: str):
    """Gets the rotation of the video.

    Parameters
    ----------
    video_path : str
        Path to the video to be analyzed.

    Returns
    -------
    orientation : int
        
    """    
    video = cv2.VideoCapture(video_path)
    orientation = video.get(cv2.CAP_PROP_ORIENTATION_META)
    orientation = int(orientation)

    return orientation

def getBoundingBox(first_fps: int, path: str, area_points: np.ndarray,
                  orientation: int = 0, show: bool = False):
 """Gets the bounding box that encloses the particle in the initial frame.
 If the function fails to find the bounding box, it increments the frame number by 1
 until it finds the bounding box or reaches the attempt limit (set to 10).

 Parameters
 ----------
 first_fps : int
    Frame number where the particle begins to move.
 path : str
    Path to the video to analyzed.
 area_points : np.ndarray
    Area of interest to search the particle in the frame, 
    avoiding noise from other areas.
 orientation : int, optional
    Orientation of the video, by default 0.
 show : bool, optional
    If True, shows the frame with the computed bounding box. Default is False.

 Returns
 -------
 bounding_box : list
    The bounding box with the upper-left corner (x, y), width, and height.
 first_fps : int
    The frame number used to initialize the tracker, updated if the bounding box was
    not found on the initial frame given.
 """    
 _attempts = 0
 delta = 4
 while True:
    _attempts += 1    
    try:
        _capture = cv2.VideoCapture(path)
        _capture.set(cv2.CAP_PROP_POS_FRAMES, first_fps)
        success, _frame = _capture.read()
        if orientation == 90:
            inverse = []

            for point in area_points:
                new_point = point[::-1]
                inverse.append(new_point)
        
            area_points = np.array(inverse)
        
        # Create an area to find the particle, minimizing the noise
        gray = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
        aux_image = np.zeros(shape=(_frame.shape[:2]), dtype=np.uint8)
        aux_image = cv2.drawContours(aux_image, [area_points], -1, (255), -1)
        image_area = cv2.bitwise_and(gray, gray, mask= aux_image)
        # Change gray scale to binary scale [0,1]
        bn = cv2.inRange(image_area, np.array([15]), np.array([255]))
        bn[bn>=1] = 255

        estimate = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT_ALT, 1, 2000, param1=50, 
                                    param2=0.85, minRadius=5, maxRadius=30)
        estims = np.round(estimate[0,:]).astype('int')
        estim = np.round(estims[0,:]).astype('int')
        (a,b,r) = estim
        
    except TypeError:
        print("Particle not found in frame number " + str(first_fps) + 
              " --> next: ", first_fps + 1)
        first_fps = first_fps + 1
        
        if _attempts > 10:
            print("The limit of attempts has been exceeded.")
            print("Particle not found. Last analyzed frame: ",
                  first_fps)
            
            return None
    
        continue
        
    else:
        # Create a black frame to draw the computed circle
        bn[:,:]=0
        circle_bn = cv2.circle(bn, (a,b), r, (255, 255, 255), 2)

        _circle, check = cv2.findContours(circle_bn, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        bbox = cv2.boundingRect(_circle[0]) # x, y, w, h
        bbox_delta = [bbox[0] - delta, bbox[1] - delta,
                      bbox[2] + delta, bbox[3] + delta]
        
        _capture.release()
    
        if show == True:
            p1 = bbox_delta[0], bbox_delta[1]
            p2 = bbox_delta[2] + bbox[0], bbox_delta[3] + bbox[1]
            rect = cv2.rectangle(circle_bn, p1, p2, (255,255,255), 2, 1)
            cv2.imshow('bbox', rect); cv2.waitKey(500)
    
        return bbox_delta, first_fps

def selectBoundingBox(first_fps: int, path: str):
    """Displays the initial frame to the user and allows them to manually select
    the bounding box by right-clicking and dragging the mouse.

    Parameters
    ----------
    first_fps : int
        Frame number of the initial frame.
    path : str
        Path to the video to be analyzed.

    Returns
    -------
    bbox : Rect
        The bounding box with the upper-left corner (x, y), width, and height.
    """    
    capture = cv2.VideoCapture(path)
    capture.set(cv2.CAP_PROP_POS_FRAMES, first_fps)
    success, frame = capture.read()
    
    window = "BBOX"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.putText(frame, 'Selecciona el area de interes.', (200, 30), font, 1, (0,255,0), 2)
    cv2.putText(frame, 'Presiona ENTER para confirmar.', (200, 70), font, 1, (0,255,0), 2)
    cv2.moveWindow(window, 179, 139)
    bbox = cv2.selectROI(window, frame, True)
    capture.release()
    cv2.destroyAllWindows()
    
    return bbox

def trackingParticleCSRT(path: str, initial_fps: int, bbox: tuple, final_frame: int = 0,
                          orientation: int = 0, irl: bool = False):
    """Tracks the particle's position in each frame of the video until the video ends
    or the `final_frame` limit set by the user is reached.

    Parameters
    ----------
    path : str
        Path to the video to be analyzed.
    initial_fps : int
        Frame number where the tracker starts the analysis.
    bbox : tuple
        Bounding box computed in the initial frame.
    final_frame : int
        Sets the last frame to be analyzed by the tracker, even if the video has more 
        frames afterward. By default 0 (analyzes all the frames in the video)
    orientation : int, optional
        Orientation of the video, by default 0.
    irl : bool, optional
        If True, displays the tracking of the particle in real-time, by default False.

    Returns
    -------
    coords : list
        List of points (x,y) computed by the tracker.
    """    
    
    # Sets the video in the initial frame
    capture = cv2.VideoCapture(path)
    capture.set(cv2.CAP_PROP_POS_FRAMES, initial_fps)
    success, frame = capture.read()
    count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = initial_fps
    
    # Create the tracker variable
    tracker = cv2.TrackerCSRT_create()

    # Begins the tracker with the bounding box
    success_track = tracker.init(frame, bbox)

    while fps < count:
        # Compute the central point of the bbox
        X = int((bbox[0]+bbox[0]+bbox[2])/2)
        Y = int((bbox[1]+bbox[1]+bbox[3])/2)
        
        # Saves the coordinates depending on the orientation
        if orientation == 90:
            coords.append([Y,X])
        
        else:
            coords.append([X,Y])
        
        # Current frame
        fps = int(capture.get(cv2.CAP_PROP_POS_FRAMES))
        success_frame, frame = capture.read()

        if success_frame == True:
          if fps == final_frame:
            break

          # Updating the tracker variable
          success_track, bbox = tracker.update(frame)
          
          # Shows the tracking in real time
          if success_track is True:
            if irl == True:
                liveTracking(fps, frame, coords, bbox)
            
            continue
        
          if success_track is not True:
            print('An error was detected while tracking the particle.')
            break
        
        else:
            break
    
    print('There are no more frames in the video.')
    capture.release()
    cv2.destroyAllWindows()
    
    return coords

def showTracking(points: np.ndarray):
    """Shows with matplotlib the list of points obtained by the tracker.

    Parameters
    ----------
    points : np.ndarray
        List of points.

    """
    plt.figure('rastreo')
    plt.plot(points[:,0],points[:,1])
    plt.show()
    return 0

########## Toma de tiempo ##########
initial_time = time.time()

########## Access and saving paths ######### 
pathvid = 'K:\\VParticles\\14\\'
pathdata = 'K:\\Tracking\\'
namevid = 'Video05H.MP4'
full_path = pathvid + namevid

########## Parameters #########
frame_ini = 490
frame_end = 590
area_points = np.array([[1201,697],[1201,381],[767,381],[767,697]])
coords = []

rotation = getRotation(full_path)
bbox, frame_ini = getBoundingBox(frame_ini, full_path, area_points, rotation)
rastreo = trackingParticleCSRT(full_path, frame_ini, bbox, rotation, True)

######## Saving data ##########
coordinates = np.array(rastreo)
np.savetxt(pathdata+'Tracking2'+namevid[5:7]+'.dat', coordinates)

final_time = time.time()
op_time = (final_time-initial_time)/60
print('The tracking of the video ' + namevid + ' lasted: %.2f'%(op_time)+' minutes.')

showTracking(coordinates)


