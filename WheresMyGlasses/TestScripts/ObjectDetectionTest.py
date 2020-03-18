from object_detector import ObjectDetector
import cv2


desk = cv2.imread("desktop_objects.jpg")

od = ObjectDetector()
od.detect_objects(desk)