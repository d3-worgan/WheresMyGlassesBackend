# import pyrealsense2 as rs
import numpy as np
import cv2
import time
# from pylsl import StreamInfo, StreamOutlet

class StreamManager:

    def __init__(self, frame_width, frame_height, frames_second):
        """
        Class to manage the streams coming from the RealSense cameras
        E.g. Output the streams to screen, video files, or the LSL
        -----------------------------------------------------------
        :param frame_width: Desired frame width in pixels
        :param frame_height: Desired frame height in pixels
        :param frames_second: Desired frames per second
        """

        # Allow window to be smaller than frame:
        self.defaultWinSize = (int(1920/3), int(1080/3)) # Good for 1920x1080 display, e.g. monitor in control room
        # self.defaultWinSize = (int(1920/5), int(1080/5))  # Good for Living Lab TV when using low resolution.

        # Set window positions for known cameras based on integer tiling in a 3x3 grid, roughly reflecting their
        # positions in the lab:
        self.defaultWinPos = {
            '2':(2,2), # Right, bottom
            '3':(2,1), # Middle, bottom
            '4':(2,0), # Right, top
            '5':(1,2), # Middle, bottom
            '6':(1,1), # Middle, middle
            '7':(0,2), # Left, bottom
            '8':(0,0), # Left, top
        }
        # Convert window positions to pixels
        for key in self.defaultWinPos:
            self.defaultWinPos[key] = tuple([x*self.defaultWinSize[i] for i,x in enumerate(self.defaultWinPos[key])])

        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames_second = frames_second
        self.display_windows = {}
        print("Loaded lab manager " + str(self.frame_width) + " " + str(self.frame_height) + " " + str(self.frames_second))

    def load_display_windows(self, enabled_devices):
        """
        Creates a window for each enabled device,
        saves the window into the 'self.display_windows = {}'
        -------
        :param enabled_devices: The devices passed from the device manager
        :return: None
        """
        for i, device in enumerate(enabled_devices):
            winName = 'Camera ' + i
            self.display_windows[device] = winName
            cv2.namedWindow(winName, cv2.WINDOW_NORMAL) # cv2.WINDOW_NORMAL enables explicit sizing, as opposed to cv2.WINDOW_AUTOSIZE.
            cv2.resizeWindow(winName, self.defaultWinSize)

    def display(self, snapshot, flip):
        """
        Displays the latest polled frames to their windows
        :param frames_devices: Dictionary from device manager (with latest polled frames)
        :param flip: Select true for right way up
        :return: None
        """

        for i, camera_snap in enumerate(snapshot.camera_snaps):
            window = self.display_windows[i]
            cv2.imshow(window, camera_snap.frame)
            ret = cv2.waitKey(1)
