# Wheres My Glasses (Backend)
Object location system for the smart home and people with dementia. 

Uses yolo object detection with the darknet neural network framework and intel realsense cameras.

https://github.com/AlexeyAB/darknet

https://github.com/pjreddie/darknet

https://github.com/IntelRealSense/librealsense

Performs object detection and generates location information using the bounding box coordinates 
to give a clue if an object is close to another.

The WheresMyGlassesFrontend can request location information using voice commands over the MQTT connection.

https://github.com/d3-worgan/WheresMyGlassesFrontend
