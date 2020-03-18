import paho.mqtt.client as mqtt


class MQTTConnection:
    """
    class to wrap a paho client and create "connections" between system components
    """

    def __init__(self, broker, name, on_message=None):
        print("Creating new MQTT client: " + name)
        print("Broker address: " + broker)
        self.name = name
        self.pClient = mqtt.Client(name)
        self.pClient.on_connect = self.on_connect
        self.pClient.on_log = self.on_log
        self.pClient.on_disconnect = self.on_disconnect
        self.pClient.on_message = on_message  # Main callback (connection)
        self.pClient.connect(broker)
        self.pClient.loop_start()

    def subscribe_topic(self, topic):
        self.pClient.subscribe(topic)
        print(f"{self.name} client Subscribed to " + topic)

    def on_log(client, userdata, level, buf):
        """
        Use for debugging paho client
        """
        print("[ResponseDecoder] log: " + buf)

    def on_connect(client, userdata, flags, rc):
        """
        Use for debugging the paho client
        """
        if rc == 0:
            print("[ResponseDecoder] Connected OK")
        else:
            print("[ResponseDecoder] Bad connection, returned code ", rc)

    def on_disconnect(client, userdata, flags, rc=0):
        """
        Use for debugging the paho client
        """
        print("[ResponseDecoder] Disconnected result code " + str(rc))
