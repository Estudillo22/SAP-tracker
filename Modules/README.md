# A brief explanation of modules

## Autubbox module
This module is designed to obtain an area of interest for the tracker.

### Function `getBoundingbox()`
This function requires the path to the video and the first frame number where the particle begins its motion.
It is specifically designed for round-shaped particles, as it uses a method for circle detection.

<img src="https://github.com/user-attachments/assets/5a555310-6316-4964-94d5-f29e8994b1d3" width = "40%" >
<img src="https://github.com/user-attachments/assets/0a49faea-2a70-47e1-9e0e-db47be1add78" width = "42%" >

## InitialFrame module
This module is designed to find the frame number where the particle begins its motion.

### FUNCTIONS
### - `lightIntensity()`
Helps to locate the frame with a specific percentage of darkness, based on the experimental setup mentioned in the main README.

<img src="https://github.com/user-attachments/assets/302e78f6-3198-4bfa-983d-99e0b4275fa6" width = 40% >
<img src="https://github.com/user-attachments/assets/27a187a4-5b0c-4813-a89a-ead3b239d184" width = 40% >

### - `auxiliarImage()`
Creates a copy of the original frame but crops it to only the area of interest.

<img src="https://github.com/user-attachments/assets/a12f1a6e-b173-4c6c-a083-9473becdff1b" width = 40% >
<img src="https://github.com/user-attachments/assets/2fabb06b-4f9e-480e-b927-3f97afcd89ab" width = 40% >

### - `morphologicalTransform()`
Enhances the shape of the particle, making it easier to detect (optimized for round-shaped particles).

![beforetransform](https://github.com/user-attachments/assets/efb22b25-434d-4420-ae0c-7606aab2a50b)
![aftertransform](https://github.com/user-attachments/assets/08bb7fa1-570e-4a20-b844-05bd225e3037)

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

