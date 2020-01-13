class LocatedObject:
    """
    A pair of objects which were located near each other
    """
    def __init__(self, object, location):
        #self.camera_id
        self.object = object
        self.location = location
