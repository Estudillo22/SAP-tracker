"""
Created on Sunday April 16 2023 23:16 GMT-6
Autor: Alberto Estudillo Moreno 
Version: 1.3.0

"""
import cv2
import numpy as np


def darknessIntensity(path: str, percent: float):
    """ Compute the frame-by-frame darkness of the video until
    the required percentage is reached.

    Parameters
    ----------
    path : str
        Path to the video to be analyzed.
    percent : float
        Minimum required percentage of darkness in the video.

    Returns
    -------
    fps, orientation : int, int
        Return the frame where the video reachs the darkness `fps` and the
        orientation of the video `orientation`.
    """    
    captureLI = cv2.VideoCapture(path)
    orientationLI = captureLI.get(cv2.CAP_PROP_ORIENTATION_META)
    while(captureLI.isOpened()):
        _ret, frameLI = captureLI.read()
        fpsLI = int(captureLI.get(cv2.CAP_PROP_POS_FRAMES))
            
        if _ret == True:
  
         gray = cv2.cvtColor(frameLI, cv2.COLOR_BGR2GRAY)
         histogram = cv2.calcHist([gray],[0], None, [256], [0,256])
         # Sums the range [0,35] that represents darkness
         darkness = sum(histogram[0:35])
        
         if darkness > (1920*1080)*percent:
            print('From the frame number %i' %fpsLI + ' the video has %'+
                  str(int(percent*100)) + ' of darkness.')
            captureLI.release()
            cv2.destroyAllWindows()
            break
            
         else:
            continue
        
    return fpsLI, orientationLI
    
def auxiliarImage(frameAI: cv2.typing.MatLike, area_pointsAI: np.ndarray):
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
    
def morphologicTransform(imageMT: cv2.typing.MatLike):
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
    #Kernel to generate elliptic/circles shapes
    kernelMT = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    img_maskMT = cv2.morphologyEx(imageMT, cv2.MORPH_CLOSE, kernelMT)
    img_dilMT = cv2.dilate(img_maskMT, None, iterations= 1)
    demosMT = cv2.demosaicing(img_dilMT, code= cv2.COLOR_BayerBG2GRAY)
    bnMT = cv2.inRange(demosMT, np.array([25]), np.array([255]))
        
    return bnMT

def minimumArea(frameMA: cv2.typing.MatLike):
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
    
def movementDetector(path: str, fps: int, area_points: np.ndarray):
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
            
            if min_area == 0:
                min_area = minimumArea(img_mask)
            
            # Saves the frame in a list
            frames.append(img_mask)
            # Saves the frame number in a list
            frames_count.append(fps)
        
            # Superposes the frames when the list reaches the size of 5
            if len(frames) == 5:
                sum_frames = sum(frames)
                # Finds the contour of the 5 superposed frames
                contour, _ = cv2.findContours(sum_frames, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                # Compute the area of the superposed frames
                contour_area = cv2.contourArea(contour[0])
                
                if contour_area < min_area:
                # Deletes the 1st element from each list
                    del frames[0]
                    del frames_count[0]
                    continue
            
                else:
                    cv2.imshow('Sum', sum_frames); cv2.waitKey(0)
                    print('Motion detected from frame number: ')
                    print(frames_count[0])
                    break
            
        else: 
            continue
    
    capture.release()   
    init_frame = frames_count[0]
    return init_frame


##################################
# # Paths
# path_vid = "F:\\VParticles\\Puerta14\\"
# vid_name = "Video01.mp4"
# full_path = path_vid + vid_name
# ##################################
# # Parameters
# percent = 0.97
# ##################################
# # Frame with darkness
# fps, orientation = darknessIntensity(full_path, percent)

# ###############################################
# # Motion detection in a specific area.
# area_points = np.array([[1201,697],[1201,381],[767,381],[767,697]])
# if orientation == 90:
#     inverse = []

#     for point in area_points:
#         new_point = point[::-1]
#         inverse.append(new_point)
    
#     area_points = np.array(inverse)
    
# initial_frame = movementDetector(path_vid + vid_name, fps, area_points)
# print('The initial frame of the video: '+ str(initial_frame))