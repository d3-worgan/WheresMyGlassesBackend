"""
Video walk-through using Paho: https://www.youtube.com/watch?v=QAaXNt0oqSI
"""
from WheresMyGlasses.source.ObjectLocator.ObjectLocator import ObjectLocator

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
    object is not the snapshot check in the snapshot history. Publish a message to the
    front end describing the results i.e. code located, code not found, code bad object.
    :param client:
    :param userdata:
    :param msg:
    :return:
    """
    global ol
    global snapshot_history
    global lock
    bad_object = True

    # Decode the incoming message
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    print("Message received: ", m_decode)

    # Use the object detector to see if the object is in the room
    # Validate that the detector can detect the required object
    lock.acquire()
    for name in ol.object_detector.classes:
        print("Searching names file for requested object ", m_decode)
        if name == m_decode:
            print("Object is in training data")
            bad_object = False

    if not bad_object:
        # Use the object detector to see if the object is in the room
        snapshot = ol.take_snapshot('x')
        print("Searching snapshot...")
        location = ol.search_snapshot(snapshot, m_decode)
        if location is not None:
            print(f"The {m_decode} was in the snapshot, returning location.")
            client.publish("seeker/processed_requests", "snapshot = {} @ {}".format(location.object1, location.object2))
        else:
            # Check the Snapshot history to see if we have seen the object before
            print(f"The {m_decode} was not in the snapshot, searching the snapshot history...")
            for snap in snapshot_history:
                print(f"Searching snapshot {snap.id}")
                location = ol.search_snapshot(snap, m_decode)
                if location is not None:
                    print(f"The {m_decode} was in the snapshot, returning location.")
                    client.publish("seeker/processed_requests", "history = {} @ {}".format(location.object1, location.object2))
                    break

            # Inform the front end the object could not be found
            if location is None:
                print(f"The {m_decode} was not in the snapshots, returning not found...")
                client.publish("seeker/processed_requests", "Not Found")
    else:
        # Inform the user the detector does not recognise that object
        print("The object has not been trained on the network, returning bad item")
        client.publish("seeker/processed_requests", "Bad Object")

    lock.release()


print("Start")
broker = "192.168.0.27"
client = mqtt.Client("seeker")

history_size = 20
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
i = 0
while True:
    lock.acquire()
    if len(snapshot_history) < history_size:
        snapshot_history.append(ol.take_snapshot(i))
        snapshot_history[-1].print_snapshot()
        #snapshot_history[-1].print_details()
        i += 1
    else:
        snapshot_history.pop(0)
        snapshot_history.append(ol.take_snapshot(i))
        snapshot_history[-1].print_snapshot()
        # snapshot_history[-1].print_details()
        i += 1

    lock.release()
    time.sleep(0.1)

client.loop_stop()
client.disconnect()
