# SAP-Tracker

## About <a name = "about"></a>
This project was created to obtain trajectories of synthetic active particles in 2D, which contributed to the publication of the article with DOI: https://doi.org/10.1039/D3SM01407J. The main idea was to have a simple and fast tracker taking advantage of what the OpenCV library offers for image analysis.

The project consists of three modules, each with its functions to facilitate the detection and tracking of particles. These functions are adaptable based on the experimental setup's conditions. Currently, this code only considers the experimental configuration used in the article mentioned above.

## Prerequisites
The libraries you need to install for this are:
- OpenCV-contrib
- Numpy
- Matplotlib
- Pandas

## How to Use
The easiest way to use this tracker is by using the `tracker.py` module and calling the functions `selectBoundingbox` and `trackingParticleCSRT`.
The first function allows you to select the area where the particle is located and the second function tracks the particle. This approach works if you know beforehand the
frame number where the particle begins its motion.

```python
...
bbox = selectBoundingbox(first_fps, video_path)
trajectory = trackingParticleCSRT(video_path, first_fps, bbox, 0, 0, True)

#Converting the list to a numpy ndarray
trajectory = np.array(trajectory)

# Saving the array
np.savetxt(save_path + 'trajectory_name.dat', trajectory)

```

## Examples
![Example1](https://github.com/user-attachments/assets/02d2e87e-b920-4093-b725-f9e3e60e795e)



https://github.com/user-attachments/assets/c23e055e-10ed-4b0e-9f78-b5593f8218a9

