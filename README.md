# Wheres My Glasses (Backend)
Object location MQTT server using Intel RealSense, Darknet and YOLO object detection. 

![location demo](location_demo.png)  

Combine with the associated 
[frontend code](https://github.com/d3-worgan/WheresMyGlassesFrontend) to build a voice activated object location assistant. There 
is also [associated code](https://github.com/d3-worgan/darknet-docker) 
for downloading open images dataset and training object detection models using docker containers.

[pjreddie](https://github.com/pjreddie/darknet) and [AlexyAB](https://github.com/AlexeyAB/darknet) for 
YOLO and Darknet.


## Installation (Linux)
### 1. Install the RealSense SDK
Follow the instructions on the [RealSense](https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md) 
github to install the RealSense SDK.

### 2. Build and install Darknet & YOLO
If we want to use a GPU to improve object detection speed we need to build Darknet from source. 
Skip this step if using a CPU and use the ```--opencv``` option to use the opencv CPU implementation of darknet. 
Follow the [instructions](https://github.com/AlexeyAB/darknet#how-to-compile-on-linux-using-make) to build darknet. The easiest way 
is using ```make```. Note the dependencies in the darknet repo like CUDA 10.0, CUDNN 7.0. Other versions may cause issue.

1. Change into a directory and download the darknet code e.g.
```
cd ~
git clone https://github.com/AlexeyAB/darknet.git
cd darknet
```
2. Set the GPU option in the Makefile to 1, also set the LIBSO option to 1 to build for linux. You can also configure 
darknet to use CUDNN if it is installed.
```
sed -i "s/GPU=0/GPU=1/" Makefile
sed -i 's/LIBSO=0/LIBSO=1/' Makefile
sed -i 's/CUDNN=0/CUDNN=1/' Makefile
```
3. Build darknet
```
make
```
4. The result of this should be a ```libdarknet.so``` file in the ```darknet/``` directory.

### 3. Setup the project
Now that RealSense and Darknet are ready we can prepare the WheresMyGlasses project.
1. Change out of the darknet directory and download WheresMyGlasses e.g.
```
cd ../
git clone https://github.com/d3-worgan/WheresMyGlassesBackend.git
cd WheresMyGlassesBackend
```
2. Create a conda python environment
```
conda create -y -n wmg python=3.6 
conda activate wmg
```
3. Install the python dependencies
```
pip install -y -r requirements
```
4. Copy the darknet library file into the WheresMyGlasses project e.g.
```
cp ../darknet/libdarknet.so modules/object_detection
```
### 3. Download and install detection models
Finally we need to give WheresMyGlasses an object detection model to perform the object detection. There are several 
[pre-trained models](https://github.com/AlexeyAB/darknet#pre-trained-models) available on the AlexyAB repository. Or we 
can use a custom trained model. To keep model management simple, each model should be saved into its own folder with its 
corresponding ```.weights```, ```.cfg```, ```.names``` and ```.data``` files inside the ```modules/object_detection/models/``` 
folder. Here is an example.
1. Change into the models directory
```
cd modules/object_detection/models/
```
2. Make a new directory for the detection model
```
mkdir yolov3
cd yolov3
```
3. Download the model files
```
cp ../../../../../darknet/cfg/yolov3.cfg yolov3.cfg
cp ../../../../../darknet/cfg/coco.names coco.names
cp ../../../../../darknet/cfg/coco.data coco.data
wget https://pjreddie.com/media/files/yolov3.weights
```
4. Adjust the ```.data``` file for our project
```
sed -i 's/names = data\/coco.names/names = modules\/object_detection\/models\/yolov3\/coco.names/' coco.data
```
4. Then the model name can be specified on the command line using the ```--model``` option e.g. ```--model yolov3``` 
(see the example usage below). 

## Usage
Now we can test the installation has worked by running
```
python main.py --display
```
Or, if we want to use the CPU version 
```
python main.py --display --opencv
```
To specify which model to use, follow the steps above (i.e. put the model files in a new directory in the models directory) and specify the folder name using the ```--model``` option e.g.
```
python main.py --display --model yolov4
```
To connect the system to MQTT to allow to process and respond to requests try
```
python main.py --display --mqtt
```
To specify the address of the MQTT broker use e.g.
```
python main.py --display --mqtt --broker 192.168.0.123
```
