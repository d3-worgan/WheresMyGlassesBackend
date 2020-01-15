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
        self.objects_detected = []
        self.objects_located = []
        self.timestamp = None
        self.id = None
        self.light_brightness = 0
        self.image = None

    def to_response(self, code):
        br = BackendResponse(code, self.timestamp, self.objects_located)
        response = br.pack()
        return response

    def print_details(self):
        """
        Print some details and information about the snapshot to the console.
        :return:
        """
        print("ID " + str(self.id))
        print("Timestamp " + str(self.timestamp))
        print("Objects detected " + str(len(self.objects_detected)))
        # for obj in self.objects_detected:
        #     print(obj.label)
        print("Objects located  " + str(len(self.objects_located)))
        for pair in self.objects_located:
            print(f"The {pair.object} is by the {pair.location}")

    def print_snapshot(self):
        """
        Display the image taken of the snapshot with bounding boxes around the
        detected objects.
        :return:
        """
        # Draw bounding boxes on detected objects
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (255, 100, 100)

        for obj in self.objects_detected:
            cv2.rectangle(self.image, (obj.x, obj.y), (obj.x + obj.w, obj.y + obj.h), color, 1)
            cv2.putText(self.image, obj.label + " " + str(round(obj.confidence, 2)), (obj.x, obj.y + 30), font, 1, color, 1)

        # Display results
        cv2.imshow("Image", self.image)

        # Finish up
        cv2.waitKey(1)
        #cv2.destroyAllWindows()
        #print("Done.")

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
