from WheresMyGlasses.ObjectLocator.snapshot import Snapshot
from WheresMyGlasses.ObjectLocator.located_object import LocatedObject
from WheresMyGlasses.ObjectLocator.object_detector import ObjectDetector
from WheresMyGlasses.ObjectLocator.camera_snap import CameraSnap
import numpy as np
import pyrealsense2 as rs
from datetime import datetime
import cv2


class ObjectLocator:
    """
    Pulls together the camera streams and object detector to produce or investigate snapshots.
    """

    def __init__(self, od_model, model_folder, use_darknet, device_manager):

        # CV or Darknet?
        self.use_darknet = use_darknet

        # Use the device manager to grab images from the cameras
        self.device_manager = device_manager

        # Use the object detector to analyse images and extract detection info.
        self.object_detector = ObjectDetector(od_model, model_folder, use_darknet)

        print("Object locator ready.")

    def take_snapshot(self, sid='x'):
        """
        Takes a picture and evaluates it for objects and their locations.
        :param sid: Give the Snapshot an ID for reference.
        :return: A Snapshot containing the detected objects and location information from an image.
        """
        # print("Taking a snapshot")
        snapshot = Snapshot()
        snapshot.id = sid
        snapshot.timestamp = datetime.now()

        # Take images from each camera
        # print("Reading camera stream")

        frames_devices = self.device_manager.poll_frames()
        for i, (device, frame) in enumerate(frames_devices.items()):
            image = np.asarray(frame[rs.stream.color].get_data())
            image = cv2.flip(image, 0)
            snapshot.camera_snaps.append(CameraSnap(image, device))

        # Detect objects in the images
        for camera_snap in snapshot.camera_snaps:
            if self.use_darknet:
                image_resized, camera_snap.detections = self.object_detector.detect_objects_dn(camera_snap.frame, camera_snap.camera_id)
                camera_snap.frame = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
            else:
                camera_snap.detections = self.object_detector.detect_objects_cv(camera_snap.frame, camera_snap.camera_id)

        # Try to locate the detected objects

        for camera_snap in snapshot.camera_snaps:
            camera_snap.locations = self.locate_objects(camera_snap.detections)

        return snapshot

    def locate_objects(self, detections):
        """
        Computes if objects are close to each other to produce information describing the location of an object. If the
        center of an object is within the same space as another object it is considered near to it. I.e. if the center
        xy of object a is within the bounding box of object b, then a is located next to b.
        :param detections: A list of detected objects found in an image
        :return: A list describing pairs of objects that were 'near' each other in the image.
        """
        locations = []

        # Put together pairs of objects
        for obj in detections:
            for loc in detections:
                if loc.cid != obj.cid:
                    if loc.x < obj.center_x < (loc.x + loc.w) and loc.y < obj.center_y < (loc.y + loc.h):
                        locations.append(LocatedObject(obj.label, loc.label, obj.camera_id))

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
        Checks to see if a requested object has been located in a particular snapshot. If the object is in there then
        make sure the requested object is in the object and not in the location. This avoids saying e.g. "the table is
        by the glasses" instead of "the glasses are by the table"
        :param snapshot: The Snapshot to investigate
        :param object_name: The name of the object to search for
        :return: Return a list of locations identified with the specified object
        """
        # Return
        locations = []
        print(f"Checking if the object was located in snapshot {snapshot.id}")
        for camera_snap in snapshot.camera_snaps:
            for pair in camera_snap.locations:
                if pair.object == object_name:
                    locations.append(pair)
                elif pair.location == object_name:
                    # Swap the names around so it makes better sense
                    temp = pair.location
                    pair.location = pair.object
                    pair.object = temp
                    locations.append(pair)
        return locations








