"""
Video walk-through using Paho: https://www.youtube.com/watch?v=QAaXNt0oqSI
"""
from WheresMyGlasses.source.ObjectLocator.ObjectLocator import ObjectLocator
from WheresMyGlasses.source.ObjectLocator.BackendResponse import BackendResponse
from WheresMyGlasses.source.ObjectLocator.stream_manager import StreamManager
from WheresMyGlasses.source.ObjectLocator.realsense_device_manager import DeviceManager

import paho.mqtt.client as mqtt
import threading
import time
import pyrealsense2 as rs
from datetime import datetime
import sys, os

def on_log(client, userdata, level, buf):
    print("log: " + buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection, returned code ", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))


def minutes_passed(timestamp):
    if timestamp:
        current_time = datetime.now()
        print("Current time ", current_time)
        print("Location time ", timestamp)
        passed = current_time - timestamp
        minutes_passed = passed.seconds / 60
        return round(minutes_passed, 2)


def process_requests(client, userdata, msg):
    """
    Main callback from the MQTT client which processes the frontend requests and produces a backend response.
    :return: No return, but publish a BackendResponse on the MQTT
    """

    # Decode the incoming message
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    print(f"Message {m_decode} received on {topic}")

    # Grab the lock and restrict access to the snapshot history
    lock.acquire()

    # Start building information for the backend response
    response = None
    current_snapshot = None
    object_located = False
    message_code = ''

    # Check the object has been trained on the detector
    if validate_object(m_decode, locator):

        # Check if the locator can locate the object in the current snapshot
        current_snapshot = locator.take_snapshot('x')
        print("Searching snapshot...")
        locations_identified = locator.search_snapshot(current_snapshot, m_decode)

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
            for i, snap in enumerate(snapshot_history):
                print(f"Searching snapshot {i}")
                locations_identified = locator.search_snapshot(snap, m_decode)

                # The locator found a snapshot with the object located
                if len(locations_identified) == 1:
                    object_located = True
                    current_snapshot = snap

                    # Use the correct message code to describe how long ago the location was
                    if minutes_passed(current_snapshot.timestamp) < 2:
                        message_code = '1'
                    else:
                        message_code = '3'

                # The locator found a snapshot with multiple object locations
                elif len(locations_identified) > 1:
                    object_located = True
                    current_snapshot = snap

                    # Use the correct message code to describe the location information
                    if minutes_passed(current_snapshot.timestamp) < 2:
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
        response = BackendResponse(message_code, m_decode, None, [], stream_manager)

    # Pack the response object into json and publish to the backend handler
    if response:
        response = response.pack()
        print(response)
        client.publish("backend/response", response)
    else:
        client.publish("backend/response", "*backend error*")

    # Release the lock so can continue taking snapshots while waiting for requests
    lock.release()


def take_snapshots():
    """
    Background loop taking regular snapshots to keep track of objects and state of the room. Display output.
    :return:
    """

    # Give each snapshot an id
    snapshot_id = 0
    while True:
        # Take a snapshot on specified intervals
        t = datetime.now()
        #if t.second % snapshot_interval == 0:

        # Use the lock to avoid competing with the "process_requests" thread for the snapshot_history
        lock.acquire()

        # Take the snapshot
        snapshot = locator.take_snapshot(snapshot_id)

        # Display snapshot
        if display_output:
            stream_manager.display_bboxes(snapshot, flip_cameras)

        # Maintain a fixed size queue
        if len(snapshot_history) < history_size:
            snapshot_history.append(locator.take_snapshot(snapshot_id))
            snapshot_id += 1
        else:
            snapshot_history.pop(0)
            snapshot_history.append(locator.take_snapshot(snapshot_id))
            snapshot_id += 1

        # Release the lock so the request handler can access the snapshot_history
        lock.release()

        # Need to sleep otherwise will keep blocking the request handler
        time.sleep(0.1)


def validate_object(m_decode, locator):
    """
    Searches the object detectors list of trained classes to check the request is valid
    :param m_decode:
    :param locator:
    :return:
    """
    print("Searching names file for requested object ", m_decode)
    for name in locator.object_detector.classes:
        if name == m_decode:
            print("Object is in training data")
            return True


if __name__ == "__main__":

    """
    Entry point for the backend system. Intialise paramters etc here....
    """

    # Specify model (yolov3, yolo9000, yoloSuper, open_images, oi_custom)
    od_model = "yolov3"

    # Specify the location of the detection models, configs & data files
    model_folder = r"G:\DetectionModels"
    assert os.path.exists(model_folder), "Couldn't find the detection models folder..."

    # Specify Darknet implementation (e.g. True = Darknet implementation, False = openCV implementation)
    use_darknet = False

    # Specify an interval to take regular snapshots
    snapshot_interval = 1  # (seconds)

    # Turn on MQTT listener (brokers address = raspberry pi IP)
    use_mqtt = False
    broker = "192.168.0.159"

    # Specify camera stream parameters
    resolution_width = 1920  # frame width px
    resolution_height = 1080  # frame height px
    # resolution_width = 1280  # frame width px
    # resolution_height = 720  # frame height px
    frame_rate = 30  # fps
    flip_cameras = False  # True to flip view
    display_output = True  # True to display camera streams with bounding box info

    print("Loading the backend manager...")

    # Open and configure devices
    print("Loading camera devices...")
    print("Camera config %s x %s @ %s fps" % (resolution_width, resolution_height, frame_rate))
    rs_config = rs.config()
    rs_config.enable_stream(rs.stream.color, resolution_width, resolution_height, rs.format.bgr8, frame_rate)
    device_manager = DeviceManager(rs.context(), rs_config)
    device_manager.enable_all_devices()
    assert len(device_manager._enabled_devices) > 0, "No realsense devices were found"

    # Open and configure output streams (so we can view the snapshots)
    print("Loading camera streams...")
    stream_manager = StreamManager(resolution_width, resolution_height, frame_rate)
    stream_manager.load_display_windows(device_manager._enabled_devices)

    # Load the object detection and location system
    print("Loading the object locator...")
    locator = ObjectLocator(od_model, model_folder, use_darknet, device_manager)

    if use_mqtt:
        # Load the MQTT client and register callback functions
        print("Loading MQTT client")
        client = mqtt.Client("Backend")
        client.on_connect = on_connect
        client.on_log = on_log
        client.on_disconnect = on_disconnect
        client.on_message = process_requests  # Main callback for processing frontend requests

        # Connect MQTT and start listening for frontend requests
        print("Connecting to MQTT broker ", broker)
        client.connect(broker)
        client.loop_start()
        client.subscribe("backend_handler/frontend_request")

    # Initialise the snapshot history, calculate the number of snapshots required to store a days worth of data
    # using the specified intervals
    seconds_in_a_day = 86400
    history_size = seconds_in_a_day / snapshot_interval
    snapshot_history = []
    print("Snapshot interval " + str(snapshot_interval))
    print("Snapshot history size " + str(history_size))

    assert history_size > 0, "The history size should be greater than zero?"

    # Use a lock to manage access to the snapshot_history
    lock = threading.Lock()

    # Start taking regular snapshots and listening for incoming requests on MQTT
    print("BackendManager loaded, waiting for requests.")

    try:
        take_snapshots()
    except KeyboardInterrupt:
        print("User quit.")
    finally:
        print("done")
        lock.release()
        if use_mqtt:
            client.loop_stop()
            client.disconnect()

