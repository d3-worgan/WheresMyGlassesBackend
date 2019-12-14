from WheresMyGlasses.source.search_assistant.Snapshot import Snapshot
import cv2
import numpy as np

class SearchAssistant:
    def __init__(self):
        self.snapshot_frequency = 10
        self.snapshot_buffer_size = 1440
        self.snapshot_history = []

    def take_snapshot(self):
        """
        Takes a snapshot and saves it to the snapshot history, maintains a specified
        number of snapshots
        :return:
        """
        print("Taking a snapshot")
        if len(self.snapshot_history) > self.snapshot_buffer_size:
            self.snapshot_history.pop(0)

        self.snapshot_history.append(Snapshot())

    def find_snapshot(self):
        print("Searching for items...")
