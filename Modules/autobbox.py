"""
Created on Saturday March 25 2023 17:16 GMT-6
Autor:Alberto Estudillo Moreno 
Last modification: Sunday January 14 2024 23:22 GMT-6

"""

import numpy as np
import cv2
import pandas as pd

def get_auto_bbox(first_fps: int, path: str, area_points: np.ndarray,
                  orientation: int = 0, show: bool =False):
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
        
        # Se crea un area especifica para buscar la particula y evitar el mayor ruido posible
        gray = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
        aux_image = np.zeros(shape=(_frame.shape[:2]), dtype=np.uint8)
        aux_image = cv2.drawContours(aux_image, [area_points], -1, (255), -1)
        image_area = cv2.bitwise_and(gray, gray, mask= aux_image)
        # Se pasa de la escala de grises a escala binaria para reducir el ruido alrededor...
        #... de la particula.
        bn = cv2.inRange(image_area, np.array([15]), np.array([255]))
        # Convierte la escala binaria a escala de grises con..
        #... la conversion de -> pixel = 1 entonces pixel = 255.
        bn[bn>=1] = 255

        estimate = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT_ALT, 1, 2000, param1=50, 
                                    param2=0.85, minRadius=5, maxRadius=30)
        estims = np.round(estimate[0,:]).astype('int')
        estim = np.round(estims[0,:]).astype('int')
        (a,b,r) = estim
        
    except TypeError:
        print("No se encontro la particula en el frame " + str(first_fps) + 
              " --> siguiente: ", first_fps + 1)
        first_fps = first_fps + 1
        
        if _attempts > 10:
            print("Se ha excedido el numero de intentos.")
            print("No se encontro la particula. Ultimo frame analizado: ",
                  first_fps)
            
            return None
    
        continue
        
    else:
        # Se crea una imagen completamente en negro para...
        #... dibujar el circulo encontrado y estimar mejor la bbox.
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
            cv2.imshow('bbox', rect); cv2.waitKey(0)
    
        return bbox_delta, first_fps

########## Rutas de acceso #########
pathvid = 'F:\\VParticles\\ControlP5\\'
namevid = '1-GH010648.MP4' 
path = pathvid + namevid

frame_ini = 545
area_points = np.array([[1201,697],[1201,381],[767,381],[767,697]]) 
orientation = 0

boundingbox, _fps= get_auto_bbox(frame_ini, path, area_points, orientation, True)
print(boundingbox)
