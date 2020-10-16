import pyrealsense2 as rs
import numpy as np
import cv2
import time


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
        #self.defaultWinSize = (int(1920/3), int(1080/3)) # Good for 1920x1080 display, e.g. monitor in control room
        self.defaultWinSize = (int(1920/5), int(1080/5))  # Good for Living Lab TV when using low resolution.
        #self.defaultWinSize = (int(frame_width/2), int(frame_height/2))

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

        # Dict of camera numbers
        # This allows simplified window naming and consistent window positioning between runs.
        # If cameras are moved around in the lab, these should be changed.
        self.camNames = {
            "830112071467":'Living Room',
            "830112071329":'4',
            "831612070394":'2',
            "831612071422":'Dining Area',
            "831612071440":'Kitchen',
        }

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
        for device in enabled_devices:
            # If we don't know the name of this device, use its serial number.
            if device not in self.camNames:
                self.camNames[device] = device
            winName = self.camNames[device]
            self.display_windows[device] = winName
            cv2.namedWindow(winName,cv2.WINDOW_NORMAL) # cv2.WINDOW_NORMAL enables explicit sizing, as opposed to cv2.WINDOW_AUTOSIZE.
            cv2.resizeWindow(winName, self.defaultWinSize)
            if self.camNames[device] in self.defaultWinPos:
                cv2.moveWindow(winName,self.defaultWinPos[self.camNames[device]][0],
                               self.defaultWinPos[self.camNames[device]][1])

    def display(self, frames_devices, flip):
        """
        Displays the latest camera snaps to their windows
        :param frames_devices: Dictionary from device manager (with latest polled frames)
        :param flip: Select true for right way up
        :return: None
        """

        for i, (device, frame) in enumerate(frames_devices.items()):
            window = self.display_windows[device]
            if flip:
                final_frame = self.flip_frame(frame)
            else:
                final_frame = np.asarray(frame[rs.stream.color].get_data())
            print(str(self.camNames[device]) + " " + str(frame[rs.stream.color].frame_number) + " " + str(frame[rs.stream.color].timestamp))
            cv2.imshow(window, final_frame)
            ret = cv2.waitKey(1)


    def display_bboxes(self, snapshot, flip):

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_size = 1
        color = (0, 255, 0)
        line_px = 2

        #snapshot.print_details()

        for i, camera_snap in enumerate(snapshot.camera_snaps):

            # Select the corresponding camera window
            window = self.display_windows[camera_snap.camera_id]

            boxed_image = camera_snap.frame

            # Draw bounding boxes and display to windows
            for obj in camera_snap.detections:
                cv2.rectangle(boxed_image, (obj.x, obj.y), (obj.x + obj.w, obj.y + obj.h), color, line_px)
                cv2.putText(boxed_image, obj.label + " " + str(round(obj.confidence, 2)), (obj.x, obj.y + 30), font, font_size, color, 2)

            cv2.imshow(window, boxed_image)

        # Finish up
        cv2.waitKey(1)

    @staticmethod
    def flip_frame(frame):
        """
        Takes a frame and flips horizontally & vertically.
        :param frame: Given frame data, a 3d array from the device stream
        :return:
        """
        array = np.asarray(frame[rs.stream.color].get_data())
        flip_h = np.fliplr(array)
        flip_v = np.flipud(flip_h)
        return flip_v
0