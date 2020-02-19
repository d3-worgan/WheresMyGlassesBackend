from WheresMyGlasses.source.ObjectLocator.DetectedObject import DetectedObject

import cv2
import numpy as np
import sys, os


class ObjectDetector:
    """
    Darknet and YOLO object detector
    """
    def __init__(self, od_model, model_folder, use_darknet):
        print("Initialising detector")
        weights, config, meta_data, names = self.load_specified_model(od_model, model_folder)
        self.classes = []
        with open(names, "r") as f:
            self.classes = [line.strip() for line in f.readlines()]
        if use_darknet:
            print("Loading Darknet original")
            self.net = darknet.load_net_custom(config.encode("ascii"), weights.encode("ascii"), 0, 1)  # batch size = 1
            self.meta = darknet.load_meta(meta_data.encode("ascii"))
        else:
            print("Loading Darknet openCV")
            self.net = cv2.dnn.readNet(config, weights)
            self.layer_names = self.net.getLayerNames()
            self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
            self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        print("Detector initialised.")

    def detect_objects_dn(self, frame, camera_id):
        """
        Extract object from an image using YOLO in original implementation of Darknet
        :param frame:
        :param camera_id:
        :return:
        """
        # Prepare image
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (640, 640), (0, 0, 0), True, crop=False)

        dees = darknet.detect(self.net, self.meta, blob, thresh=0.5, hier_thresh=.5, nms=.45)

        print(dees)
        detected_objects = []
        for d in dees:

            # Extract detection info
            dindex = d[0]  # Class ID
            label = self.classes[dindex]  # Retrieve the corresponding class name
            confidence = d[1]  # Confidence of the detection
            box = d[2]  # Get the coordinates

            # Calculate bounding box coordinates
            center_x = int(box[0])
            center_y = int(box[1])
            h = int(box[3])  # Right hand side?
            w = int(box[2])  # Right hand side?
            x = int(box[0] - box[2] / 2)  # Left hand side?
            y = int(box[1] - box[3] / 2)  # Left hand side?

            detected_object = DetectedObject(dindex, label, confidence, center_x, center_y, x, y, w, h)
            detected_objects.append(detected_object)

        return detected_objects

    def detect_objects_cv(self, frame, camera_id):
        """
        Extract objects from an image using YOLO in openCV implementation of Darknet.
        :param frame: Picture to process
        :return: A list of objects that were detected in the image
        """

        #print(f"Analysing {camera_id} for objects")

        # Prepare image
        height, width, channels = frame.shape
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (640, 640), (0, 0, 0), True, crop=False)
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
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.1, 0.1)

        # Return a list of objects detected in the image
        detections = []
        for i in range(len(boxes)):
            if i in indexes:
                detections.append(
                    DetectedObject(class_ids[i], self.classes[class_ids[i]], confidences[i], camera_id, centers[i][0],
                                   centers[i][1], boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]))

        #print(f"Detected {len(detections)} objects")
        return detections

    def load_specified_model(self, od_model, model_folder):
        """
        Return the corresponding paths for the chosen model
        :param od_model:
        :param model_folder:
        :return:
        """

        weights = None
        config = None
        meta_data = None
        names = None
        if od_model == "yolov3":
            weights = os.path.join(model_folder, "yolov3.weights")
            config = os.path.join(model_folder, "yolov3.cfg")
            meta_data = os.path.join(model_folder, "coco.data")
            names = os.path.join(model_folder, "coco.names")
        elif od_model == "yolo9000":
            weights = os.path.join(model_folder, "yolo9000.weights")
            config = os.path.join(model_folder, "yolo9000.cfg")
            meta_data = os.path.join(model_folder, "combine9k.data")
            names = os.path.join(model_folder, "9k.names")
        elif od_model == "yoloSuper":
            weights = os.path.join(model_folder, "yoloSuper.weights")
            config = os.path.join(model_folder, "yoloSuper.cfg")
            meta_data = os.path.join(model_folder, "coco.data")
            names = os.path.join(model_folder, "coco.names")
        elif od_model == "open_images":
            weights = os.path.join(model_folder, "openimages.weights")
            config = os.path.join(model_folder, "openimages.cfg")
            meta_data = os.path.join(model_folder, "openimages.data")
            names = os.path.join(model_folder, "openimages.names")
        elif od_model == "oi_custom":
            weights = os.path.join(model_folder, "oi_custom.weights")
            config = os.path.join(model_folder, "oi_custom.cfg")
            meta_data = os.path.join(model_folder, "oi_custom.data")
            names = os.path.join(model_folder, "oi_custom.names")
        else:
            print("Specified model is not available, default yoloSuper")

        assert weights, "Couldn't find the .weights file for" + od_model
        assert config, "Couldn't find the .cfg file for " + od_model
        assert meta_data, "Couldn't find the .data file for " + od_model
        assert names, "Couldn't find the .names file for " + od_model

        return weights, config, meta_data, names