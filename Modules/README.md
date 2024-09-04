# A brief explanation of modules

## Autubbox module
This module is designed to obtain an area of interest for the tracker.

### Function `getBoundingbox()`
This function requires the path to the video and the first frame number where the particle begins its motion.
It is specifically designed for round-shaped particles, as it uses a method for circle detection.

## InitialFrame module
This module is designed to find the frame number where the particle begins its motion.

### FUNCTIONS
### - `lightIntensity()`
Helps to locate the frame with a specific percentage of darkness, based on the experimental setup mentioned in the main README.

### - `auxiliarImage()`
Creates a copy of the original frame but crops it to only the area of interest.

### - `morphologicalTransform()`
Enhances the shape of the particle, making it easier to detect (optimized for round-shaped particles).

### - `minimumArea()`
Defines the minimum area in pixels required to detect the beginning of particle motion.

### - `movementDetector()`
Identifies the frame number where the particle begins its motion in the video.

## Tracker module
This module tracks the particle in every frame of the video.

### FUNCTIONS
### - `liveTracking()`
Shows the computed trajectory to the user in real-time.

### - `getRotation()`
Determines the orientation of the video.

### - `getBoundingBox()`
Performs the same function as `getBoundingBox()` in the Autobbox module.

### - `selectBoundingBox()`
Allows the user to select the area where the particle is located using the mouse.

### - `tracinkgParticleCSRT()`
Tracks the particle and computes its position in all video frames or until it reaches the last frame number set by the user.

### - `ShowTracking()`
Plots the trajectory obtained with the `trackingParticleCSRT()` function.

