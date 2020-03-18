"""
Video walk-through using Paho: https://www.youtube.com/watch?v=QAaXNt0oqSI
"""

import paho.mqtt.client as mqtt


class BackCon:
    def __init__(self):
        print("Start")

        # Set up client and broker
        self.broker = "192.168.0.27"
        self.client = mqtt.Client("BackendConnection")

        # Register the callback functions
        self.client.on_connect = self.on_connect
        self.client.on_log = self.on_log
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        # Start listening
        self.listen()

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

    def listen(self):
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker)
        self.client.loop_start()
        self.client.subscribe("topic1/test")
        #client.publish("topic1/test", "Hello danny")
        #time.sleep(4)

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("User quit...")
        finally:
            self.client.loop_stop()
            self.client.disconnect()


bc = BackCon()