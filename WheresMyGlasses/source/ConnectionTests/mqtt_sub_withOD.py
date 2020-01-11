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
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8","ignore"))
    print("Message recieved: ", m_decode)
    # check object is in names list
    global ol
    global snapshot_history
    global lock
    bad_object = True

    lock.acquire()
    for name in ol.object_detector.classes:
        print("Searching names file for requested object ", m_decode)
        if name == m_decode:
            print("Object is in training data")
            bad_object = False

    if not bad_object:
        snapshot = ol.take_snapshot('x')
        print("Searching snapshot...")
        location = ol.search_snapshot(snapshot, m_decode)
        if location is not None:
            print(f"The {m_decode} was in the snapshot, returning location.")
            client.publish("seeker/processed_requests", "snapshot = {} @ {}".format(location.object1, location.object2))
        else:
            print(f"The {m_decode} was not in the snapshot, searching the snapshot history...")
            for snap in snapshot_history:
                print(f"Searching snapshot {snap.id}")
                location = ol.search_snapshot(snap, m_decode)
                if location is not None:
                    print(f"The {m_decode} was in the snapshot, returning location.")
                    client.publish("seeker/processed_requests", "history = {} @ {}".format(location.object1, location.object2))
                    break
            if location is None:
                print(f"The {m_decode} was not in the snapshots, returning not found...")
                client.publish("seeker/processed_requests", "Not Found")
    else:
        print("The object has not been trained on the network, returning bad item")
        client.publish("seeker/processed_requests", "Bad Object")

    lock.release()


print("Start")
broker = "192.168.0.27"
client = mqtt.Client("seeker")

client.on_connect = on_connect
client.on_log = on_log
client.on_disconnect = on_disconnect
client.on_message = on_message

print("Connecting to broker ", broker)
client.connect(broker)

client.loop_start()

client.subscribe("voice_assistant/user_requests")


snapshot_history = []
ol = ObjectLocator(100)
lock = threading.Lock()

print("Saving snapshots to history...")
i = 0
while True:
    lock.acquire()
    snapshot_history.append(ol.take_snapshot(i))
    snapshot_history[-1].print_snapshot()
    #snapshot_history[-1].print_details()
    i += 1
    lock.release()
    time.sleep(0.5)

client.loop_stop()
client.disconnect()
