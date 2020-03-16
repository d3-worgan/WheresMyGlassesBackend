import cv2


devices = {'Camera 0': cv2.VideoCapture(0), 'Camera1': cv2.VideoCapture(1)}

while True:
    ret, img = devices['Camera 0'].read()
    cv2.imshow("Image", img)
    cv2.waitKey(1)
