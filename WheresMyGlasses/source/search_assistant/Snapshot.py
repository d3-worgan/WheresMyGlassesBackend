class Snapshot:
    def __init__(self):
        self.objects_detected = []
        self.objects_located = []
        self.time_taken = 0
        self.date_taken = 0
        self.frame_id = 0
        self.light_brightness = 0

    def detect_objects(self):
        print("Searching for object in image...")

    def locate_objects(self):
        print("Locating objects in image...")