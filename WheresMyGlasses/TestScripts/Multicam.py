import cv2
from object_detector import ObjectDetector

cameras = []
cameras.append(cv2.VideoCapture(0))
cameras.append(cv2.VideoCapture(1))

# cap1 = cv2.VideoCapture(0)
# cap2 = cv2.VideoCapture(1)

od = ObjectDetector()


while True:

    images = []

    for camera in cameras:
        ret, frame = camera.read()
        if ret:
            images.append(frame)
        else:
            print("Poopy pants")


    # ret1, frame1 = cap1.read()
    # ret2, frame2 = cap2.read()

    detections = []

    for image in images:
        detections.append(od.detect_objects(image))

    # detections1 = od.detect_objects(frame1)
    # detections2 = od.detect_objects(frame2)

    # Draw bounding boxes on detected objects
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (255, 100, 100)

    for detection in detections:

    for obj in detections1:
        cv2.rectangle(frame1, (obj.x, obj.y), (obj.x + obj.w, obj.y + obj.h), color, 1)
        cv2.putText(frame1, obj.label + " " + str(round(obj.confidence, 2)), (obj.x, obj.y + 30), font, 1, color, 1)

    for obj in detections2:
        cv2.rectangle(frame2, (obj.x, obj.y), (obj.x + obj.w, obj.y + obj.h), color, 1)
        cv2.putText(frame2, obj.label + " " + str(round(obj.confidence, 2)), (obj.x, obj.y + 30), font, 1, color, 1)

    if ret1 and ret2:
        cv2.imshow("cap1", frame1)
        cv2.imshow("cap2", frame2)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    else:
        break

cap1.release()
cap2.release()
cv2.destroyAllWindows()