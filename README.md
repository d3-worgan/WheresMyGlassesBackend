# Wheres My Glasses (Backend)
This is one of three parts of a final year digital systems project from the University of the West of England. The complete
system was used to implement a voice activated object location assistant for people with dementia. This part of the system
maintains the status of objects and their locations in the room using the Darknet neural network and the YOLO object detection
algorithm. The system waits for MQTT requests (generated by the frontend voice assistant) which specify objects to 
search for. Whilst waiting the system maintains state by taking regular snapshots of the room. When the MQTT request is 
recieved, it then generates location information depending on the outcome of the search of the room and its memory. The 
associated [frontend voice assistant](https://github.com/d3-worgan/WheresMyGlassesFrontend) code can be used to trigger 
the requests and handle the output messages. There is also [associated code](https://github.com/d3-worgan/darknet-docker) 
for data acquisition and training object detection models using docker containers.

Credit to [Joesph Redmon](https://github.com/pjreddie/darknet) and [AlexyAB](https://github.com/AlexeyAB/darknet) for 
YOLO and Darknet.

## Installation
The current implementation has been written and tested for Linux only.
#### 1. Install the RealSense SDK
#### 2. Build and install Darknet & YOLO
#### 3. Setup a conda environment and python dependencies

