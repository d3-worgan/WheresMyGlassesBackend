from modules.detected_object import DetectedObject

import cv2
import numpy as np
import os

from modules.object_detection import darknet


class ObjectDetector:
    """
    Darknet and YOLO object detector.
    Either use the original darknet and python bindings or use the opencv implementation of darknet 
    """
    def __init__(self, od_model, model_folder, opencv):
        print("Initialising detector")

        # Find the paths for the specified object detection model
        weights, config, meta_data, names = self.load_specified_model(od_model, model_folder)

        # Load the class names for the detection model
        self.classes = []
        with open(names, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

        if opencv:
            print("Loading Darknet openCV")
            print("config path " + config)
            print("weights path " + weights)
            self.net = cv2.dnn.readNetFromDarknet(config, weights)
            self.layer_names = self.net.getLayerNames()
            self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        else:
            print("Loading Darknet original")
            #self.net = darknet.load_network(config, meta_data, weights, batch_size=1)
            self.net = darknet.load_net_custom(config.encode("ascii"), weights.encode("ascii"), 0, 1)  # batch size = 1
            self.meta = darknet.load_meta(meta_data.encode("ascii"))

        print("Detector initialised.")

    def detect_objects_dn(self, frame, camera_id):
        """
        Extract objects from an image using YOLO in original implementation of Darknet
        :param frame: The image to process
        :param camera_id: The camera which took the picture
        :return: An image resized to fit darknet & a list of detected objects
        """
        # Prepare image
        height, width, channels = frame.shape
        darknet_image = darknet.make_image(darknet.network_width(self.net), darknet.network_height(self.net), 3)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (darknet.network_width(self.net), darknet.network_height(self.net)), interpolation=cv2.INTER_LINEAR)
        darknet.copy_image_from_bytes(darknet_image, frame_resized.tobytes())

        # Extracting detections
        dees = darknet.detect_image(self.net, self.classes, darknet_image, thresh=0.5, hier_thresh=.5, nms=.45)
        print(dees)
        detected_objects = []
        for d in dees:

            # Extract detection info
            lid = self.classes.index(d[0])
            label = d[0]  # Retrieve the corresponding class name
            confidence = float(d[1])  # Confidence of the detection
            box = d[2]  # Get the coordinates

            # Calculate bounding box coordinates
            center_x = int(box[0])
            center_y = int(box[1])
            h = int(box[3])  # Right hand side?
            w = int(box[2])  # Right hand side?
            x = int(box[0] - box[2] / 2)  # Left hand side?
            y = int(box[1] - box[3] / 2)  # Left hand side?

            detected_object = DetectedObject(lid, label, confidence, camera_id, center_x, center_y, x, y, w, h)
            detected_objects.append(detected_object)

        return frame_resized, detected_objects

    def detect_objects_cv(self, frame, camera_id):
        """
        Extract objects from an image using YOLO in openCV implementation of Darknet.
        :param frame: Picture to process
        :return: A list of objects that were detected in the image
        """

        # Prepare image
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), (0, 0, 0), True, crop=False)
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
                    label = self.classes[int(class_id)]
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
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.1, 0.1)

        # Return a list of objects detected in the image
        detections = []
        for i in range(len(boxes)):
            if i in indexes:
                detections.append(
                    DetectedObject(class_ids[i], self.classes[int(class_ids[i])], confidences[i], camera_id, centers[i][0],
                                   centers[i][1], boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]))

        return detections

    def load_specified_model(self, od_model, model_folder):
        """
        Specify a model on the command line with the correct base directory.
        Makes loading weights and cfgs for yolo easier
        :param od_model:
        :param model_folder:
        :return:
        """

        print("Loading specified model...")
        print("Folder path " + model_folder)
        weights = None
        config = None
        meta_data = None
        names = None

        # Walk the models directory and find one with the model name specified.
        # Then generate the paths for each file inside
        directories = next(os.walk(model_folder))[1]
        for dir in directories:
            if od_model in dir:
                model_files = next(os.walk(os.path.join(model_folder, dir)))[2]
                for f in model_files:
                    if '.cfg' in f:
                        config = os.path.join(model_folder, dir, f)
                    elif '.weights' in f:
                        weights = os.path.join(model_folder, dir, f)
                    elif '.data' in f:
                        meta_data = os.path.join(model_folder, dir, f)
                    elif '.names' in f:
                        names = os.path.join(model_folder, dir, f)

        assert weights, "Couldn't find the .weights file for " + od_model
        assert config, "Couldn't find the .cfg file for " + od_model
        assert meta_data, "Couldn't find the .data file for " + od_model
        assert names, "Couldn't find the .names file for " + od_model

        assert os.path.exists(weights), f"{weights} is not a valid path"
        assert os.path.exists(config), f"{config} is not a valid path"
        #assert os.path.exists(meta_data), f"{meta_data} is not a valid path"
        assert os.path.exists(names), f"{names} is not a valid path"

        print("Weights path: " + weights)
        print("Config path: " + config)
        print("meta_data path: " + meta_data)
        print("names path " + names)

        return weights, config, meta_data, names