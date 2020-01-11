from WheresMyGlasses.source.ObjectLocator.DetectedObject import ObjectDetected

import cv2
import numpy as np


class ObjectDetector:
    """
    Wrap the YOLO object detector in a class so that the object locator can easily
    process an image and detect objects.
    """
    def __init__(self):
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

        print("Detector initialised.")

    def detect_objects(self, frame):
        """
        Extract objects from an image.
        :param frame: Picture to process
        :return: A list of objects that were detected in the image
        """

        # Prepare image
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
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

        # Reduce double detections and errors
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        # Return a list of objects detected in the image
        detections = []
        for i in range(len(boxes)):
            if i in indexes:
                detections.append(
                    ObjectDetected(class_ids[i], self.classes[class_ids[i]], confidences[i], centers[i][0],
                                   centers[i][1], boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]))

        return detections
