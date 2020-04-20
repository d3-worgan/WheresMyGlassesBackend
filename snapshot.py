import cv2
import numpy as np
from matplotlib import pyplot as plt
from backend_response import BackendResponse


class Snapshot:
    """
    Used to manage and track objects. Detection and location data is saved to a snapshot
    for processing later
    """
    def __init__(self):
        self.timestamp = None
        self.id = None
        self.camera_snaps = []

    def to_response(self, code):
        """
        Prepare snapshot for sending to the frontend
        :param code:
        :return:
        """
        br = BackendResponse(code, self.timestamp, self.camera_snaps)
        response = br.pack()
        return response

    def print_details(self):
        """
        Print some details and information about the snapshot to the console.
        :return:
        """
        print("ID " + str(self.id))
        print("Timestamp " + str(self.timestamp))

        for i, camera_snap in enumerate(self.camera_snaps):
            print("Camera " + str(i) + " " + str(camera_snap.camera_id))
            print("Number detections " + str(len(camera_snap.detections)))
            for obj in camera_snap.detections:
                print(obj.label)
            print("Number locations " + str(len(camera_snap.locations)))
            for loc in camera_snap.locations:
                print(f"The {loc.object} is by the {loc.location}")

    def delete_frames(self):
        """
        Delete the image after it has been processed to maintain privacy and save memory
        :return:
        """
        for snap in self.camera_snaps:
            if snap.frame is not None:
                snap.frame = None

    def calculate_brightness(self):
        """
        Needs to implemented, calculate if an image is out of balance, indicating
        whether it might be harder for detections. Use the V in HSV to find brightness.

        https: // opencv - python - tutroals.readthedocs.io / en / latest / py_tutorials / py_imgproc / py_histograms / py_histogram_begins / py_histogram_begins.html  # histograms-getting-started
        https://forum.smithmicro.com/topic/9430/find-average-brightness-of-an-image/4

        :return:
        """
        cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist(self.image, [3], None, [256], [0, 256])
        print(hist)
        av = np.mean(hist)
        print(av)
        plt.hist(self.image.ravel(), 256, [0, 256]);
        plt.show()
