from WheresMyGlasses.source.ObjectLocator.Snapshot import Snapshot
from WheresMyGlasses.source.ObjectLocator.LocatedObject import LocatedObject
from WheresMyGlasses.source.ObjectLocator.ObjectDetector import ObjectDetector

import cv2
from datetime import datetime


class ObjectLocator:
    """
    The object locator uses the object detection module and a camera stream to analyse
    pictures for objects. It can take a "Snapshot" using the camera and extract the
    location information from the frame.
    """
    def __init__(self):
        """
        Initialise the object locator by loading the neural network and object detector.
        Then start reading from the camera stream.
        """
        print("Preparing object locator...")

        # Load detector (YOLO)
        self.object_detector = ObjectDetector()

        # Open the camera stream
        print("Reading camera stream...")
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Could not open video device")

        print("Object locator ready.")

    def take_snapshot(self, sid='x'):
        """
        Takes a picture and evaluates it for objects and their locations.
        :param sid: Give the Snapshot an ID for reference.
        :return: A Snapshot containing the detected objects and location information
                 from an image.
        """
        snapshot = Snapshot()
        snapshot.id = sid
        now = datetime.now()
        snapshot.timestamp = now.strftime("%H:%M")

        # Read an image from the camera
        ret, img = self.video_capture.read()
        snapshot.image = img

        # Detect objects in the image
        snapshot.objects_detected = self.object_detector.detect_objects(img)

        # Try to locate the detected objects
        snapshot.objects_located = self.locate_objects(snapshot.objects_detected)

        return snapshot

    def locate_objects(self, detections):
        """
        Computes if objects are close to each other to produce information describing
        the location of an object. If the center of an object is within the same space
        as another object it is considered near to it. I.e. if the center xy of object
        is within the bounding box of another, then pair them together as a location.
        :param detections: A list of detected objects found in an image
        :return: A list describing pairs of objects that were 'near' each other in the image.
        """
        locations = []

        # Put together pairs of objects
        for obj in detections:
            for loc in detections:
                if loc.cid != obj.cid:
                    if loc.x < obj.center_x < (loc.x + loc.w) and loc.y < obj.center_y < (loc.y + loc.h):
                        locations.append(LocatedObject(obj.label, loc.label))

        # Delete pairs where they are in the same location i.e. no new information
        for location1 in locations:
            for location2 in locations:
                if location2 is not location1:
                    if location1.object == location2.object and location1.location == location2.location:
                        locations.remove(location2)
                    elif location1.object == location2.location and location1.location == location2.object:
                        locations.remove(location2)

        return locations

    def search_snapshot(self, snapshot, object_name):
        """
        Checks to see if a requested object has been located in a particular snapshot. If
        the object is in there then make sure the requested object is in the object and not
        in the location. This avoids saying e.g. "the table is by the glasses" instead of
        "the glasses are by the table"
        :param snapshot: The Snapshot to investigate
        :param object_name: The name of the object to search for
        :return: Return a list of locations identified with the specified object
        """
        # Return
        locations = []
        print(f"Checking if the object was located in snapshot {snapshot.id}")
        for pair in snapshot.objects_located:
            if pair.object == object_name:
                locations.append(pair)
            elif pair.location == object_name:
                # Swap the names around so it makes better sense
                temp = pair.location
                pair.location = pair.object
                pair.object = temp
                locations.append(pair)
        return locations








