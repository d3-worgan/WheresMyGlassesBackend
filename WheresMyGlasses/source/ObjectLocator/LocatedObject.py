class LocatedObject:
    def __init__(self, snapshot_id, timestamp, object1, object2):
        print("Located an object")
        self.snapshot_id = snapshot_id
        self.timestamp = timestamp
        self.object1 = object1
        self.object2 = object2
