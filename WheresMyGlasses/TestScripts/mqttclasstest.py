import paho.mqtt.client as mqtt
import time


class BackendClient:

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected OK")
        else:
            print("Bad connection, returned code ", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print("Disconnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8","ignore"))
        print("Message recieved: ", m_decode)

print("Start")
broker = "192.168.0.27"
client = mqtt.Client("python1")

bec = BackendClient()

client.on_connect = bec.on_connect
client.on_log = bec.on_log
client.on_disconnect = bec.on_disconnect
client.on_message = bec.on_message

print("Connecting to broker ", broker)
client.connect(broker)

client.loop_start()

client.subscribe("topic1/test")
client.publish("topic1/test", "Hello danny")
time.sleep(4)

# while True:
#     pass

client.loop_stop()
client.disconnect()