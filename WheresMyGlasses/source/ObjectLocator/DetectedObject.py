class ObjectDetected:
    """
    A structure to easily handle information extracted from the object detection.
    """
    def __init__(self, cid, label, confidence, center_x, center_y, x, y, w, h):
        self.cid = cid  # Class id
        self.label = label
        self.confidence = confidence
#        self.camera_id
        self.center_x = center_x
        self.center_y = center_y
        self.x = x  # top left of box
        self.y = y  # top left of box
        self.w = w  # width of box
        self.h = h  # height of box
