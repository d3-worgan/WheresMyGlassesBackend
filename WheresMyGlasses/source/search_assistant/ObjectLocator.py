from WheresMyGlasses.source.search_assistant.Snapshot import Snapshot
from WheresMyGlasses.source.search_assistant.DetectedObject import ObjectDetected
from WheresMyGlasses.source.search_assistant.LocatedObject import LocatedObject

import cv2
import numpy as np
import datetime


class ObjectLocator:
    """
    The object locator searches takes snapshots of the room and generates information
    for each one.

    The voice interface can contact the object locator to take a snapshot, and then tell
    the user what the object locator found.
    """

    def __init__(self, buffer_size):
        """
        Initialise the object locator by loading the neural network and object detector.
        Maintain a history of snapshots to be able to check previously for requested objects
        """
        print("Preparing object locator...")

        # Save a number of snapshots to search for object in memory
        self.snapshot_frequency = 10
        self.snapshot_buffer_size = buffer_size
        self.snapshot_history = []

        # Load the neural network
        print("Initalizing YOLO...")
        self.net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")

        # Load the class names
        print("loading class names...")
        self.classes = []
        with open("coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        # Build the network
        print("Building Neural Network...")
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

        # Open the camera stream
        print("Reading camera stream...")
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Could not open video device")

        print("Object locator ready.")

    def take_snapshot(self, id):
        """
        Takes a picture and evaluates it for objects and their locations.
        Saves the information to a Snapshot in the snapshot history.
        :return:
        """

        #print("Taking a snapshot")
        snapshot = Snapshot()

        # Read an image from the camera
        ret, img = self.video_capture.read()
        height, width, channels = img.shape

        snapshot.image = img
        snapshot.timestamp = datetime.datetime.now()
        snapshot.id = id

        # Process the image
        #print("Object detection.")
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)

        # Detection
        outs = self.net.forward(self.output_layers)

        # Store information we extract from the image
        class_ids = []
        confidences = []
        boxes = []
        centers = []

        # Extract detections and information from the image
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    label = self.classes[class_id]
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                    centers.append([center_x, center_y])

        # Reduces double detections and errors
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Add the detected objects to the snapshot
        for i in range(len(boxes)):
            if i in indexes:
                snapshot.objects_detected.append(
                    ObjectDetected(class_ids[i], self.classes[class_ids[i]], confidences[i], centers[i][0],
                                   centers[i][1], boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]))

        # Locate items that are close to each other
        for obj in snapshot.objects_detected:
            for loc in snapshot.objects_detected:
                if loc.cid != obj.cid:
                    if loc.x < obj.center_x < (loc.x + loc.w) and loc.y < obj.center_y < (loc.y + loc.h):
                        snapshot.objects_located.append(LocatedObject(obj.label, loc.label))
                        print("The " + obj.label + " is by the " + loc.label)
                        cv2.circle(img, (obj.center_x, obj.center_y), 20, (255, 0, 0), 3)

        return snapshot

    def add_snapshot_to_history(self, id):
        snapshot = self.take_snapshot(id)
        if len(self.snapshot_history) > self.snapshot_buffer_size:
            self.snapshot_history.pop(0)
        else:
            self.snapshot_history.append(snapshot)

    def locate_object(self, object_name):
        """
        Takes a snapshot of the room and checks if the object is there.
        If the object is not there then search in memory to see if it has been seen before.
        :param object_name: String, the name of the object to search for, needs to match a class name
                            in the object detectors names file
        :return: True or False depe
        """
        print("Searching for items...")

        # Check if the requested object is in the room now
        snapshot = self.take_snapshot("x")
        print("Took a snapshot")

        for obj in snapshot.objects_detected:
            if obj.label == object_name:
                for pair in snapshot.objects_located:
                    print("Checking if the object was located")
                    if pair.object1 == object_name or pair.object2 == object_name:
                        return pair

        # Check in memory to see if the object has been seen before
        else:
            if len(self.snapshot_history) > 0:
                object_located = False
                i = len(self.snapshot_history)
                while not object_located and i >= 0:
                    if object_name in self.snapshot_history[i].objects_located:
                        for pair in snapshot.objects_located:
                            if pair.object1 == object_name or pair.object2 == object_name:
                                object_located = True
                                return pair


