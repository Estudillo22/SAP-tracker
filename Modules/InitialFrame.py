"""
Created on Sunday April 16 2023 23:16 GMT-6
Autor:Alberto Estudillo Moreno 
Last modification: Wednesday June 12 15:57 GMT-6

"""
import cv2
import numpy as np


def lightIntensity(_path: str, _percent: float):
    """ Compute the frame-by-frame darkness of the video until
    the required percentage is reached.

    Parameters
    ----------
    _path : str
        Path to the video to be analyzed.
    _percent : float
        Minimum required percentage of darkness in the video.

    Returns
    -------
    fps, orientation : int, int
        Return the frame where the video reachs the darkness `fps` and the
        orientation of the video `orientation`.
    """    
    captureLI = cv2.VideoCapture(_path)
    orientationLI = captureLI.get(cv2.CAP_PROP_ORIENTATION_META)
    while(captureLI.isOpened()):
        _ret, frameLI = captureLI.read()
        fpsLI = int(captureLI.get(cv2.CAP_PROP_POS_FRAMES))
            
        if _ret == True:
  
         #Convertimos a escala de grises y obtenemos un histograma...
         #...para calcular que tanta intensidad de luz hay en el frame
         gray = cv2.cvtColor(frameLI, cv2.COLOR_BGR2GRAY)
         #calcHist([imagen],[canal(es)], mask, [bins], [rangomin,rangomax+1])
         histogram = cv2.calcHist([gray],[0], None, [256], [0,256])
         #Sumamos el numero de pixeles oscuros en el rango de [0,35]
         darkness = sum(histogram[0:35])
        
         if darkness > (1920*1080)*_percent:
            print('A partir del frame %i' %fpsLI + ' el video tiene poca iluminacion.')
            captureLI.release()
            cv2.destroyAllWindows()
            break
            
         else:
            continue
        
    return fpsLI, orientationLI
    
def auxiliarImage(frameAI, area_pointsAI):
    """Create an auxiliary frame that contains information only in a specified area,
    with the rest of the frame set to black pixels.

    Parameters
    ----------
        frameAI : any
            Frame to be modified.
        area_pointsAI :  NDarray
            Points that specify the area of interest.

    Returns
    -------
    auxiliar_image : any
        Modified frame with the same dimensions as the original.
    """    
    grayAI = cv2.cvtColor(frameAI, cv2.COLOR_BGR2GRAY)
    aux_imageAI = np.zeros(shape=(frameAI.shape[:2]), dtype=np.uint8)
    aux_imageAI = cv2.drawContours(aux_imageAI, [area_pointsAI], -1, (255), -1)
    image_areaAI = cv2.bitwise_and(grayAI, grayAI, mask= aux_imageAI)
        
    return image_areaAI
    
def morphologicTransform(imageMT):
    """Transform the frame to enhance the visibility of the particle using 
    morphological transformations.

    Parameters
    ----------
    imageMT : any
        Frame to be transformed.

    Returns
    -------
    transformed_image : any
        Black-and-white frame with the applied transformations, maintaining the 
        same dimensions as the original.
    """    
    #Kernel para generar estructuras de forma eliptica/circular
    kernelMT = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    #Se aplican transformaciones morfologicas para mejorar la imagen binaria
    img_maskMT = cv2.morphologyEx(imageMT, cv2.MORPH_CLOSE, kernelMT)
    img_dilMT = cv2.dilate(img_maskMT, None, iterations= 1)
    demosMT = cv2.demosaicing(img_dilMT, code= cv2.COLOR_BayerBG2GRAY)
    bnMT = cv2.inRange(demosMT, np.array([25]), np.array([255]))
        
    return bnMT

def minimumArea(frameMA):
    """Compute the area of the particle in pixels and set the minimum area required
    for detecting particle movement.

    Parameters
    ----------
    frameMA : any
        Frame to be analyzed.

    Returns
    -------
    minimum_area : float
        Minimum area required for detecting particle movement.
    """    
    _contour, ex = cv2.findContours(frameMA, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    _area = cv2.contourArea(_contour[0])
    _min_area = _area * 2

    return _min_area
    
def movementDetector(path: str, fps: int, area_points):
    """Find the frame number where the particle begins to move. This function uses the
    superposition of five frames to detect a change in the area occupied by the particle, 
    based on a threshold of 2 times the area of the single particle.

    Parameters
    ----------
    path : str
        Path to the video to be analyzed.
    fps : int
        Frame number where the video has the required darkness.
    area_points : NDarray
        Area of interest to search for particle movement, avoiding noise from other areas.

    Returns
    -------
    initial_frame : int
        Frame number where the particle begins to move in the video.
    """    
    frames = []
    frames_count = []
    min_area = 0

    capture = cv2.VideoCapture(path)
    capture.set(cv2.CAP_PROP_POS_FRAMES, fps)
        
    while(capture.isOpened()):
        ret , frame = capture.read()
        fps = int(capture.get(cv2.CAP_PROP_POS_FRAMES))
            
        if ret == True:
            aux_img = auxiliarImage(frame, area_points)
            img_mask = morphologicTransform(aux_img)
            # cv2.imshow('mask', img_mask); cv2.waitKey(0)
            
            #Se calcula el area minima de movimiento
            if min_area == 0:
                min_area = minimumArea(img_mask)
            
            #Guarda el frame en una lista
            frames.append(img_mask)
            #Guarda el numero de frame que se esta guardando en la lista anterior
            frames_count.append(fps)
        
            #Superpone los frames guardados cuando la lista tiene un tamaño de 6
            if len(frames) == 5:
                sum_frames = sum(frames)
                #Encuentra el contorno del frame donde se sumaron los 6 frames
                contour, _ = cv2.findContours(sum_frames, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                #Calcula el area del frame resultante de la suma
                contour_area = cv2.contourArea(contour[0])
                
                #Si el area dentro del contorno no supera los 1400 pixeles, se detiene el calculo...
                #...y se avanza con el siguiente ciclo del While
                if contour_area < min_area:
                #Borra el primer frame guardado en las listas
                    del frames[0]
                    del frames_count[0]
                    continue
            
                else:
                    cv2.imshow('suma', sum_frames); cv2.waitKey(0)
                    print('Se detecto movimiento entre estos frames: ')
                    print(frames_count)
                    break
            
        else: 
            continue
    
    capture.release()   
    init_frame = frames_count[0]
    return init_frame


##################################
# Parametros para leer la ubicacion del archivo
path_vid = "F:\\VParticles\\Puerta14\\"
vid_name = "Video01.mp4"
full_path = path_vid + vid_name
##################################
#Parametro adicionales
percent = 0.97

##################################
#DEFINE EL FRAME CON BAJA ILUMINACION
#Y OBTIENE LA ORIENTACION DEL VIDEO
##################################
fps, orientation = lightIntensity(full_path, percent)

###############################################
# DETECCION DE MOVIMIENTO EN UN AREA ESPECIFICA.
###############################################
#Parametros
#Creamos los puntos del area, sera un rectangulo centrado en la imagen.
area_points = np.array([[1201,697],[1201,381],[767,381],[767,697]])
# Si el video esta vertical, se invierten las coordenadas de cada punto.
if orientation == 90:
    inverse = []

    for point in area_points:
        new_point = point[::-1]
        inverse.append(new_point)
    
    area_points = np.array(inverse)
    
frame_inicial = movementDetector(path_vid + vid_name, fps, area_points)
print('El frame inicial del video es: '+ str(frame_inicial))