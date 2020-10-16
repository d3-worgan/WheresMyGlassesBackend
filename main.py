import argparse
import os
import socket

from modules.backend_manager import BackendManager

cwd = os.getcwd()
model_folder = os.path.join(cwd, 'modules', 'object_detection', 'models')

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

parser = argparse.ArgumentParser(description='Run the object location system')
parser.add_argument("--model",
                    help="Specify the name of the detection model e.g. yolov3, yolo9000",
                    default="yolov3")
parser.add_argument("--model_folder",
                    help="Specify the path to an alternative base location of the detection models",
                    default=model_folder)
parser.add_argument("--opencv",
                    help="Use the opencv implementation of darknet (CPU)",
                    dest='opencv',
                    action='store_true')
parser.add_argument("--mqtt",
                    help="Switch on the connection to MQTT",
                    dest='mqtt',
                    action='store_true')
parser.add_argument("--broker",
                    help="Specify the IP address of the MQTT broker",
                    default=IPAddr)
parser.add_argument("--display",
                    help="Output the camera streams and object detection",
                    dest='display',
                    action='store_true')
parser.add_argument("--interval",
                    help="Specify an interval to take snapshots in seconds (else fast as possible)",
                    default=0)
parser.add_argument("--width",
                    help="Input res e.g. 1280, 720",
                    default=1280)
parser.add_argument("--height",
                    help="Input height e.g. 1920, 1080",
                    default=720)
parser.add_argument("--fps",
                    help="Frames per second e.g. 30, 15",
                    default=15)
parser.add_argument("--flip",
                    help="Vertically flip the camera images",
                    dest='flip',
                    action='store_true')


if __name__ == "__main__":
    print("Running object locator.")
    args = parser.parse_args()
    backend_manager = BackendManager(args.model, args.model_folder, args.opencv, args.interval, args.width,
                                     args.height, args.fps, args.flip, args.display, args.broker, args.mqtt)
    try:
        backend_manager.idle()
    except KeyboardInterrupt:
        print("User quit.")
    finally:
        print("Exiting object locator")
