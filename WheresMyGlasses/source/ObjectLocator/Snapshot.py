import cv2
import numpy as np
from matplotlib import pyplot as plt
from WheresMyGlasses.source.ObjectLocator.LocatedObject import LocatedObject

class Snapshot:
    def __init__(self):
        self.objects_detected = []
        self.objects_located = []
        self.timestamp = None
        self.id = None
        self.light_brightness = 0
        self.image = None

    def print_details(self):
        print("ID " + str(self.id))
        print("Timestamp " + str(self.timestamp))
        print("Objects detected " + str(len(self.objects_detected)))
        for obj in self.objects_detected:
            print(obj.label)
        print("Objects located  " + str(len(self.objects_located)))
        for pair in self.objects_located:
            print(pair.object1 + " " + pair.object2)

    def print_snapshot(self):
        """
        Display the image taken of the snapshot with bounding boxes around the
        detected objects.
        :return:
        """

        # Draw bounding boxes on detected objects
        font = cv2.FONT_HERSHEY_PLAIN
        color = (0, 255, 0)

        for obj in self.objects_detected:
            cv2.rectangle(self.image, (obj.x, obj.y), (obj.x + obj.w, obj.y + obj.h), color, 2)
            cv2.putText(self.image, obj.label, (obj.x, obj.y + 30), font, 3, color, 3)

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
