import cv2
import numpy as np
from matplotlib import pyplot as plt
from WheresMyGlasses.source.ObjectLocator.BackendResponse import BackendResponse

class Snapshot:
    """
    The Snapshot is used to hold all the information extracted from a given image. A
    picture is taken and then analysed by the object detector and locator, the extractions
    are then stored in a Snapshot for use later.
    """
    def __init__(self):
        self.timestamp = None
        self.id = None
        self.camera_snaps = []

    def to_response(self, code):
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

    # def display_snapshot(self):
    #     """
    #     Display the image taken of the snapshot with bounding boxes around the
    #     detected objects.
    #     :return:
    #     """
    #     # # Draw bounding boxes on detected objects
    #     # font = cv2.FONT_HERSHEY_SIMPLEX
    #     # color = (255, 100, 100)
    #     #
    #     # windows = {}
    #     # for i, camera_snap in enumerate(self.camera_snaps):
    #     #     winName = "Camera " + str(i)
    #     #     windows[camera_snap] = winName
    #     #     cv2.namedWindow(winName)
    #     #
    #     # for i, camera_snap in enumerate(self.camera_snaps):
    #     #     window = windows[camera_snap]
    #     #     for obj in camera_snap.detections:
    #     #         cv2.rectangle(camera_snap.frame, (obj.x, obj.y), (obj.x + obj.w, obj.y + obj.h), color, 1)
    #     #         cv2.putText(camera_snap.frame, obj.label + " " + str(round(obj.confidence, 2)), (obj.x, obj.y + 30), font, 1, color, 1)
    #     #         cv2.imshow(window, camera_snap.frame)
    #     #
    #     # # Finish up
    #     # cv2.waitKey(1)
    #     # #cv2.destroyAllWindows()
    #     # #print("Done.")

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
