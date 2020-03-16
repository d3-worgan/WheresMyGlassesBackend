"""
Video walk-through using Paho: https://www.youtube.com/watch?v=QAaXNt0oqSI
"""
import argparse

from WheresMyGlasses.ObjectLocator.object_locator import ObjectLocator
from WheresMyGlasses.ObjectLocator.backend_response import BackendResponse
from WheresMyGlasses.ObjectLocator.stream_manager import StreamManager
from WheresMyGlasses.ObjectLocator.realsense_device_manager import DeviceManager
from WheresMyGlasses.ObjectLocator.connection import MQTTConnection
import threading
import time
import pyrealsense2 as rs
from datetime import datetime
import os


class BackendManager:
    """
    Maintains the state of the room by saving regular snapshots to the snapshot history.
    Waits and processes requests from the frontend.
    """

    def __init__(self, od_model, model_folder, res_width, res_hight, fps, broker, name, snapshot_interval, use_darknet, use_mqtt, display):
        print("Loading backend manager...")

        # Open and configure connected realsense devices
        print("Camera config %s x %s @ %s fps" % (res_width, res_hight, fps))
        rs_config = rs.config()
        rs_config.enable_stream(rs.stream.color, res_width, res_hight, rs.format.bgr8, fps)
        self.device_manager = DeviceManager(rs.context(), rs_config)
        self.device_manager.enable_all_devices()
        assert len(self.device_manager._enabled_devices) > 0, "No realsense devices were found"

        # Open and configure output streams (so we can view the snapshots)
        print("Loading camera streams...")
        self.stream_manager = StreamManager(resolution_width, resolution_height, frame_rate)
        self.stream_manager.load_display_windows(self.device_manager._enabled_devices)
        assert len(self.stream_manager.display_windows) > 0, "No display windows"

        # Load the object detection and location system
        print("Loading the object locator...")
        self.locator = ObjectLocator(od_model, model_folder, use_darknet, self.device_manager)
        assert self.locator is not None, "Problem loading the locator..."

        # Connect to the MQTT
        if use_mqtt:
            self.connection = MQTTConnection(broker, name, self.process_requests)
            self.connection.pClient.subscribe("frontend/request")

        # Initialise the snapshot history, calculate the number of snapshots required to store a days worth of data
        # using the specified intervals
        seconds_in_a_day = 86400
        self.snapshot_interval = snapshot_interval
        self.history_size = seconds_in_a_day / self.snapshot_interval
        self.snapshot_history = []
        print("Snapshot interval " + str(self.snapshot_interval))
        print("Snapshot history size " + str(self.history_size))
        assert self.history_size > 0, "The history size should be greater than zero?"

        # Avoid conflict between "self.update" and "self.process_requests" accessing the snapshot history
        self.lock = threading.Lock()

        print("BackendManager loaded, waiting for requests.")

    def process_requests(self, client, userdata, msg):
        """
        Main callback from the MQTT client which processes the frontend requests and produces a backend response.
        :return: No return, but publish a BackendResponse on the MQTT
        """

        # Decode the incoming message
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print(f"Message {m_decode} received on {topic}")

        # Avoid conflict with take_snapshots()
        self.lock.acquire()

        # Start building information for the backend response
        response = None
        current_snapshot = None
        object_located = False
        message_code = ''

        # Check the object has been trained on the detector
        if self.validate_object(m_decode, self.locator):

            # Check if the locator can locate the object in the current snapshot
            current_snapshot = self.locator.take_snapshot('x')
            print("Searching snapshot...")
            locations_identified = self.locator.search_snapshot(current_snapshot, m_decode)

            # The locator located an object
            if len(locations_identified) == 1:
                print("Message code 1")
                object_located = True
                message_code = '1'

            # The locator located multiple objects
            elif len(locations_identified) > 1:
                print("Message code 2")
                object_located = True
                message_code = '2'

            # The locator did not find the object in the current snapshot and starts looking through the snapshot history
            else:
                print(f"The {m_decode} was not in the snapshot, searching the snapshot history...")
                for i, snap in enumerate(self.snapshot_history):
                    print(f"Searching snapshot {i}")
                    locations_identified = self.locator.search_snapshot(snap, m_decode)

                    # The locator found a snapshot with the object located
                    if len(locations_identified) == 1:
                        object_located = True
                        current_snapshot = snap

                        # Use the correct message code to describe how long ago the location was
                        if self.minutes_passed(current_snapshot.timestamp) < 2:
                            message_code = '1'
                        else:
                            message_code = '3'

                    # The locator found a snapshot with multiple object locations
                    elif len(locations_identified) > 1:
                        object_located = True
                        current_snapshot = snap

                        # Use the correct message code to describe the location information
                        if self.minutes_passed(current_snapshot.timestamp) < 2:
                            message_code = '2'
                        else:
                            message_code = '4'

            # The object was not found in the current snapshot of any of the historical snapshots
            if not object_located:
                print("The object was not found, message code 5")
                message_code = '5'
        else:
            # Inform the user the detector does not recognise that object
            print("The object has not been trained on the network, returning bad item")
            object_located = False
            message_code = '6'

        # Build the response object using the information gathered
        if object_located:
            response = BackendResponse(message_code, m_decode, current_snapshot.timestamp, self.locator.search_snapshot(current_snapshot, m_decode), self.stream_manager)
        else:
            response = BackendResponse(message_code, m_decode, None, [], self.stream_manager)

        # Pack the response object into json and publish to the backend handler
        if response:
            response = response.pack()
            print(response)
            self.connection.pClient.publish("backend/response", response)
        else:
            self.connection.pClient.publish("backend/response", "*backend error*")

        # Release the lock so can continue taking snapshots while waiting for requests
        self.lock.release()

    def add_snapshot_to_history(self):

        # Use the lock to avoid competing with the "process_requests" thread for the snapshot_history
        self.lock.acquire()

        # Take the snapshot
        snapshot = self.locator.take_snapshot(snapshot_id)

        # Maintain a fixed size queue
        if len(self.snapshot_history) < self.history_size:
            self.snapshot_history.append(self.locator.take_snapshot(snapshot_id))
            snapshot_id += 1
        else:
            self.snapshot_history.pop(0)
            self.snapshot_history.append(self.locator.take_snapshot(snapshot_id))
            snapshot_id += 1

        # Release the lock so the request handler can access the snapshot_history
        self.lock.release()

    def idle(self):
        """
        Background loop taking regular snapshots to keep track of objects and state of the room. Display output.
        :return:
        """

        try:
            # Give each snapshot an id
            snapshot_id = 0
            while True:

                # Take a snapshot on specified intervals
                if self.snapshot_interval > 0:
                    t = datetime.now()
                    if t.second % snapshot_interval == 0:
                        self.add_snapshot_to_history()
                else:
                    self.add_snapshot_to_history()

                # Display snapshot
                if display_output:
                    self.stream_manager.display_bboxes(self.snapshot_history[-1], flip_cameras)

                # Need to sleep otherwise will keep blocking the request handler
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("User quit.")
        finally:
            print("done")
            self.lock.release()
            if use_mqtt:
                self.connection.pClient.loop_stop()
                self.connection.pClient.disconnect()
            print("done")

    def validate_object(self, m_decode, locator):
        """
        Check the requested object is in the training data
        :param m_decode:
        :param locator:
        :return:
        """
        print("Searching names file for requested object ", m_decode)
        for name in locator.object_detector.classes:
            if name == m_decode:
                print("Object is in training data")
                return True

    def minutes_passed(self, timestamp):
        if timestamp:
            current_time = datetime.now()
            print("Current time ", current_time)
            print("Location time ", timestamp)
            passed = current_time - timestamp
            minutes_passed = passed.seconds / 60
            return round(minutes_passed, 2)


if __name__ == "__main__":
    """
    Entry point for the backend system. Initialise parameters etc here....
    """

    parser = argparse.ArgumentParser(description='Run the object location system')
    parser.add_argument("--model", help="Specify the name of the detection model e.g. yolov3, yolo9000, yoloCSP, open_images, wmg_v3"  , required=False, type=str, default="yoloCSP")
    parser.add_argument("--location", help="Specify the path to base location of the detection models", required=False, type=str, default=r"E:\DetectionModels")
    parser.add_argument("--interval", help="Specify an interval to take snapshots in seconds (else fast as possible)", required=False, type=float, default=0)
    parser.add_argument("--darknet", help="True to use darknet implementation or False for openCV", required=False, type=boolean, default=True)
    parser.add_argument("--mqtt", help="False to switch off connection to MQTT", required=False, type=boolean, default=True)
    parser.add_argument("--broker", help="Specify the IP address of the MQTT broker", required=False, type=str, default="192.168.0.159")
    parser.add_argument("--display", help="True to display the output of the detection streams", required=False, type=boolean, default=True)
    parser.add_argument("--resolution", help="Specify input res e.g. 1080, 720", required=False, type=int, default=1080)
    parser.add_argument("--flip", help="True to vertically flip the camera image", required=False, type=boolean, default=True)

    args = parser.parse_args()

    od_model = args.model
    model_folder = args.location
    snapshot_interval = args.interval
    use_darknet = args.darknet
    use_mqtt = args.mqtt
    broker = args.broker
    display_output = args.display
    res = args.resolution
    flip_cameras = args.flip

    assert os.path.exists(model_folder), "Couldn't find the detection models folder..."
    assert od_model is "yolov3" or od_model is "yolo9000" or od_model is "yoloCSP" or od_model is "open_images" \
           or od_model is "wmg_v3" or od_model is "wmg_anchors" or od_model is "wmg_spp", "Invalid model specified"
    assert snapshot_interval > 0, "interval must be float greater than 0"
    assert res == 720 or res == 1080, "Resolution must be 720 or 1080"

    if res == 720:
        resolution_width = 1280
        resolution_height = 720
        frame_rate = 30
    elif res == 1080:
        resolution_width = 1920
        resolution_height = 1080
        frame_rate = 30
    else:
        print("WARNING: Not a valid resolution")

    backend_manager = BackendManager(od_model, model_folder, resolution_width, resolution_height, frame_rate, broker,
                                     "BackendManager", snapshot_interval, use_darknet, use_mqtt, display_output)

    try:
        backend_manager.idle()
    except KeyboardInterrupt:
        print("User quit.")
    finally:
        print("done")