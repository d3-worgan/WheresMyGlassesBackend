"""
Video walk-through using Paho: https://www.youtube.com/watch?v=QAaXNt0oqSI
"""
from WheresMyGlasses.source.ObjectLocator.ObjectLocator import ObjectLocator
from WheresMyGlasses.source.ConnectionTests.BackendResponse import BackendResponse

import paho.mqtt.client as mqtt
import threading
import time

def validate_object(m_decode, ol):
    for name in ol.object_detector.classes:
        print("Searching names file for requested object ", m_decode)
        if name == m_decode:
            print("Object is in training data")
            return True


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

    if validate_object(m_decode, ol):
        # Use the object detector to see if the object is in the room
        snapshot = ol.take_snapshot('x')
        print("Searching snapshot...")
        locations_identified = ol.search_snapshot(snapshot, m_decode)
        if len(locations_identified) == 1:
            print("Message code 1")
            response = BackendResponse('1', m_decode, snapshot.timestamp, locations_identified)
            print(response)
        elif len(locations_identified) > 1:
                print("Message code 2")
                response = BackendResponse('2', m_decode, snapshot.timestamp, locations_identified)
                print(response)
        else:
            print(f"The {m_decode} was not in the snapshot, searching the snapshot history...")
            for snap in snapshot_history:
                print(f"Searching snapshot {snap.id}")
                locations_identified = ol.search_snapshot(snap, m_decode)
                if len(locations_identified) == 1:
                    response = BackendResponse('3', m_decode, snap.timestamp, locations_identified)
                elif len(locations_identified) > 1:
                    response = BackendResponse('4', m_decode, snapshot.timestamp, locations_identified)
                else:
                    print(f"The {m_decode} was not in the snapshots, returning not found...")
                    response = BackendResponse('5', m_decode, None, [])
    else:
        # Inform the user the detector does not recognise that object
        print("The object has not been trained on the network, returning bad item")
        response = BackendResponse('6', m_decode, None, [])

    if response:
        response = response.pack()
        print(response)
        client.publish("seeker/processed_requests", response)
    else:
        client.publish("seeker/processed_requests", "*backend error*")

    lock.release()


def take_snapshots():
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

print("Start")
broker = "192.168.0.27"
client = mqtt.Client("seeker")

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

