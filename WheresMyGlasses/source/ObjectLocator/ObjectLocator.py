from WheresMyGlasses.source.ObjectLocator.Snapshot import Snapshot
from WheresMyGlasses.source.ObjectLocator.LocatedObject import LocatedObject
from WheresMyGlasses.source.ObjectLocator.ObjectDetector import ObjectDetector
import multiprocessing

import cv2
import datetime
import threading
import time


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

        # Load YOLO
        self.object_detector = ObjectDetector()

        # Open the camera stream
        print("Reading camera stream...")
        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            raise Exception("Could not open video device")

        print("Object locator ready.")

        print("Starting threads")

        # self.pBackground = multiprocessing.Process(target=self.run_in_background)
        # self.pRequests = multiprocessing.Process(target=self.process_request)
        #
        # self.pBackground.start()
        # self.pRequests().start()



    def take_snapshot(self, sid):
        """
        Takes a picture and evaluates it for objects and their locations.
        :param sid: The Snapshot ID.
        :return: A Snapshot containing information object detections and locations
                    in an image.
        """

        snapshot = Snapshot()
        snapshot.id = sid
        snapshot.timestamp = datetime.datetime.now()

        # Read an image from the camera
        ret, img = self.video_capture.read()
        snapshot.image = img

        # Extract objects from image
        snapshot.objects_detected = self.object_detector.detect_objects(img)

        # Locate items in the image
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
        for obj in detections:
            for loc in detections:
                if loc.cid != obj.cid:
                    if loc.x < obj.center_x < (loc.x + loc.w) and loc.y < obj.center_y < (loc.y + loc.h):
                        locations.append(LocatedObject(obj.label, loc.label))
        return locations

    def add_snapshot_to_history(self, id):
        """
        Take a snapshot and add save it to the buffer in case we need to search
        backwards later. If the buffer is full then delete the oldest snapshot
        in the list.
        :param id: Give an ID to the Snapshot
        :return:
        """
        snapshot = self.take_snapshot(id)
        if len(self.snapshot_history) > self.snapshot_buffer_size:
            self.snapshot_history.pop(0)
            self.snapshot_history.append(snapshot)
        else:
            self.snapshot_history.append(snapshot)

    def search_snapshot(self, snapshot, object_name):
        for pair in snapshot.objects_located:
            print("Checking if the object was located")
            if pair.object1 == object_name or pair.object2 == object_name:
                return pair
            else:
                return None

    def locate_object(self, object_name):
        """
        Takes a snapshot of the room and checks if the object is there.
        If the object is not there then search in memory to see if it has been seen before.
        :param object_name: String, the name of the object to search for, needs to match a
                            class name in the object detectors names file.
        :return: A pair of object names if it was located or None if it was not found
        """
        print("Searching for items...")
        pair = None

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
            print("The object was not in the snapshot, searching memory...")
            for snapshot in reversed(self.snapshot_history):
                print("Checking snapshot " + str(snapshot.id))
                for obj in snapshot.objects_detected:
                    if obj.label == object_name:
                        print("Detected the object at " + str(snapshot.timestamp))
                        for pair in snapshot.objects_located:
                            if pair.object1 == object_name or pair.object2 == object_name:
                                print("Object was located at " + str(snapshot.timestamp))
                                return pair
                        print("But it was not located...")

        return pair


    def run_locator(self):
        """
        Use this to test the ObjectDetector. Will run continuously taking snapshots,
        maintaining a history, and displaying results to the screen.
        :return:
        """
        try:
            i = 0
            while True:
                self.take_snapshot(i)
                self.add_snapshot_to_history(i)
                self.snapshot_history[-1].print_snapshot()
                self.snapshot_history[-1].print_details()
                i += 1
        finally:
            cv2.destroyAllWindows()
            print("Done.")








