class ObjectDetected:
    """
    Load information from the object detector
    """
    def __init__(self, cid, label, confidence, camera_id, center_x, center_y, x, y, w, h):
        self.cid = cid  # Class id
        self.label = label
        self.confidence = confidence
        self.camera_id = camera_id
        self.center_x = center_x
        self.center_y = center_y
        self.x = x  # top left of box
        self.y = y  # top left of box
        self.w = w  # width of box
        self.h = h  # height of box
