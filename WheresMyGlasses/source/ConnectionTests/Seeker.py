"""
Video walk-through using Paho: https://www.youtube.com/watch?v=QAaXNt0oqSI
"""
from WheresMyGlasses.source.ObjectLocator.ObjectLocator import ObjectLocator
from WheresMyGlasses.source.ConnectionTests.BackendResponse import BackendResponse

import paho.mqtt.client as mqtt
import threading
import time


def on_log(client, userdata, level, buf):
    print("log: " + buf)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection, returned code ", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code " + str(rc))


def on_message(client, userdata, msg):
    """
    Main callback function for when a request is received from the front end. First validate
    the detector can recognise the specified object, then take a snapshot. If the
    object is not the snapshot check in the snapshot history. Produce a message code and
    build a response object to send to the front end.
    :return: Publish a BackendResponse on the MQTT
    """
    # Decode the incoming message
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    print(f"Message {m_decode} received on {topic}")

    global ol
    global snapshot_history
    global lock

    lock.acquire()
    response = None
    current_snapshot = None
    object_located = False
    message_code = ''

    if validate_object(m_decode, ol):
        # Use the object detector to see if the object is in the room
        current_snapshot = ol.take_snapshot('x')
        print("Searching snapshot...")
        locations_identified = ol.search_snapshot(current_snapshot, m_decode)
        if len(locations_identified) == 1:
            print("Message code 1")
            object_located = True
            message_code = '1'
        elif len(locations_identified) > 1:
            print("Message code 2")
            object_located = True
            message_code = '2'
        else:
            print(f"The {m_decode} was not in the snapshot, searching the snapshot history...")
            for snap in snapshot_history:
                print(f"Searching snapshot {snap.id}")
                locations_identified = ol.search_snapshot(snap, m_decode)
                if len(locations_identified) == 1:
                    object_located = True
                    message_code = '3'
                    current_snapshot = snap
                elif len(locations_identified) > 1:
                    object_located = True
                    message_code = '4'
                    current_snapshot = snap

        if not object_located:
            print("The object was not found, message code 5")
            message_code = '5'
    else:
        # Inform the user the detector does not recognise that object
        print("The object has not been trained on the network, returning bad item")
        object_located = False
        message_code = '6'

    if object_located:
        response = BackendResponse(message_code, m_decode, current_snapshot.timestamp, ol.search_snapshot(current_snapshot, m_decode))
    else:
        response = BackendResponse(message_code, m_decode, None, [])

    if response:
        response = response.pack()
        print(response)
        client.publish("seeker/processed_requests", response)
    else:
        client.publish("seeker/processed_requests", "*backend error*")

    lock.release()


def take_snapshots():
    """
    Background loop taking regular snapshots to keep track of objects and state of the room.
    :return:
    """
    i = 0
    while True:
        lock.acquire()
        if len(snapshot_history) < history_size:
            snapshot_history.append(ol.take_snapshot(i))
            snapshot_history[-1].print_snapshot()
            # snapshot_history[-1].print_details()
            i += 1
        else:
            snapshot_history.pop(0)
            snapshot_history.append(ol.take_snapshot(i))
            snapshot_history[-1].print_snapshot()
            # snapshot_history[-1].print_details()
            i += 1

        lock.release()
        time.sleep(0.1)


def validate_object(m_decode, ol):
    for name in ol.object_detector.classes:
        print("Searching names file for requested object ", m_decode)
        if name == m_decode:
            print("Object is in training data")
            return True


if __name__ == "__main__":
    print("Start")
    broker = "192.168.0.27"
    client = mqtt.Client("Backend")

    history_size = 1000
    snapshot_history = []
    ol = ObjectLocator()
    lock = threading.Lock()

    client.on_connect = on_connect
    client.on_log = on_log
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    print("Connecting to broker ", broker)
    client.connect(broker)
    client.loop_start()
    client.subscribe("voice_assistant/user_requests")


    print("Saving snapshots to history...")

    try:
        take_snapshots()
    except KeyboardInterrupt:
        print("User quit.")
    finally:
        print("done")
        lock.release()
        client.loop_stop()
        client.disconnect()

