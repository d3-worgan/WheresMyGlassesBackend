"""
Video walk-through using Paho: https://www.youtube.com/watch?v=QAaXNt0oqSI
"""
from WheresMyGlasses.source.ObjectLocator.ObjectLocator import ObjectLocator
from WheresMyGlasses.source.ObjectLocator.BackendResponse import BackendResponse
from WheresMyGlasses.source.ObjectLocator.stream_manager import StreamManager
from WheresMyGlasses.source.ObjectLocator.realsense_device_manager import DeviceManager
from WheresMyGlasses.source.ObjectLocator.connection import MQTTConnection
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

        if use_mqtt:
            self.connection = MQTTConnection(broker, name, self.process_requests)
            self.connection.pClient.subscribe("frontend/request")

        # Initialise the snapshot history, calculate the number of snapshots required to store a days worth of data
        # using the specified intervals
        seconds_in_a_day = 86400
        self.history_size = seconds_in_a_day / snapshot_interval
        self.snapshot_history = []
        print("Snapshot interval " + str(snapshot_interval))
        print("Snapshot history size " + str(self.history_size))
        assert self.history_size > 0, "The history size should be greater than zero?"

        # Avoid conflict between take_snapshots and process requests on the snapshot history
        self.lock = threading.Lock()

        # Start taking regular snapshots and listening for incoming requests on MQTT
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
            response = BackendResponse(message_code, m_decode, current_snapshot.timestamp, locator.search_snapshot(current_snapshot, m_decode), stream_manager)
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

    def take_snapshots(self):
        """
        Background loop taking regular snapshots to keep track of objects and state of the room. Display output.
        :return:
        """

        try:
            # Give each snapshot an id
            snapshot_id = 0
            while True:
                # Take a snapshot on specified intervals
                t = datetime.now()
                #if t.second % snapshot_interval == 0:

                # Use the lock to avoid competing with the "process_requests" thread for the snapshot_history
                self.lock.acquire()

                # Take the snapshot
                snapshot = self.locator.take_snapshot(snapshot_id)

                # Display snapshot
                if display_output:
                    self.stream_manager.display_bboxes(snapshot, flip_cameras)

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

    # Specify model (yolov3, yolo9000, yoloSuper, open_images, oi_custom)
    od_model = "yolov3"
    assert od_model is "yolov3" or od_model is "yolo9000" or od_model is "yoloSuper" or od_model is "open_images" \
           or od_model is "oi_custom", "Invalid model specified"

    # Specify the location of the detection models, configs & data files
    model_folder = r"E:\DetectionModels"
    assert os.path.exists(model_folder), "Couldn't find the detection models folder..."

    # Specify Darknet implementation (e.g. True = Darknet implementation, False = openCV implementation)
    use_darknet = False

    # Specify an interval to take regular snapshots
    snapshot_interval = 1  # (seconds)

    # Turn on MQTT listener (brokers address = raspberry pi IP)
    use_mqtt = True
    broker = "192.168.0.159"

    # Specify camera stream parameters
    # resolution_width = 1920  # frame width px
    # resolution_height = 1080  # frame height px
    resolution_width = 1280  # frame width px
    resolution_height = 720  # frame height px
    frame_rate = 30  # fps
    flip_cameras = False  # True to flip view
    display_output = True  # True to display camera streams with bounding box info

    backend_manager = BackendManager(od_model, model_folder, resolution_width, resolution_height, frame_rate, broker,
                                     "BackendManager", snapshot_interval, use_darknet, use_mqtt, display_output)

    try:
        backend_manager.take_snapshots()
    except KeyboardInterrupt:
        print("User quit.")
    finally:
        print("done")
