

class CameraSnap:

    def __init__(self, frame, camera_id):
        self.frame = frame
        self.camera_id = camera_id
        self.detections = []
        self.locations = []
