#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hermes_python.hermes import Hermes
import paho.mqtt.client as mqtt

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
broker = "192.168.0.27"


def on_log(client, userdata, level, buf):
    """
    Use for debugging paho client
    """
    print("log: " + buf)


def on_connect(client, userdata, flags, rc):
    """
    Use for debugging the paho client
    """
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection, returned code ", rc)


def on_disconnect(client, userdata, flags, rc=0):
    """
    Use for debugging the paho client
    """
    print("Disconnected result code " + str(rc))


def on_message(client, userdata, msg):
    """
    Paho client (pClient) main callback function, Handles messages from the backend
    using the paho mqtt client. Listen for messages on the seeker/processed_requests topics
    and use the information to provide an output to the user
    :param client:
    :param userdata:
    :param msg:
    :return:
    """
    global pClient
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    print("Topics recieved ", topic)
    print("Message recieved: ", m_decode)

    if topic == "hermes/nlu/intentNotRecognized":
        print("Handle intent not recognised")
        tts = "{\"siteId\": \"default\", \"text\": \"i dont understand that. please ask again\", \"lang\": \"en_GB\"}"
    else:
        data = m_decode.split()
        for d in data:
            print(d)

        tts = ""
        if data[0] == 'Bad':
            print("the requested object is not recognised")
            tts = "{\"siteId\": \"default\", \"text\": \"i do not recognise %s. maybe i can help with something else\", \"lang\": \"en_GB\"}" % (
                "that object")
        if data[0] == 'snapshot':
            print("i can see a {} by the {}".format(data[2], data[4]))
            tts = "{\"siteId\": \"default\", \"text\": \"i can see a %s by a %s\", \"lang\": \"en_GB\"}" % (
            data[4], data[2])
        if data[0] == 'history':
            print("i last seen a {} by the {}".format(data[2], data[4]))
            tts = "{\"siteId\": \"default\", \"text\": \"i last seen a %s by a %s\", \"lang\": \"en_GB\"}" % (
            data[4], data[2])
        if data[0] == 'Not':
            print("Locator could not find the object")
            tts = "{\"siteId\": \"default\", \"text\": \"i have not seen %s recently\", \"lang\": \"en_GB\"}" % ("that")

    pClient.publish('hermes/tts/say', tts)


def intent_received(hermes, intent_message):
    # Extract intent information
    session_id = intent_message.session_id
    intent_name = intent_message.intent.intent_name
    intent_confidence = intent_message.intent.confidence_score
    slot_value = None
    slot_score = None

    print("Session ID " + str(session_id))
    print("Intent name " + intent_name)
    print("intent confidence " + str(intent_confidence))

    search_object = True
    sentence = ''

    # Validate intent confidence
    if search_object:
        if intent_confidence < 0.80:
            sentence += "Im not certain what you asked for, please ask again"
            search_object = False

    # Validate correct intent
    if search_object:
        if intent_name != 'code-pig:LocateObject':
            sentence += "I do not understand that intent. please ask again"

    # Validate an object was given
    if search_object:
        if not intent_message.slots.home_object:
            sentence += "you did not specify an object to search for. please ask again"
            search_object = False

    # Extract the object name and confidence
    if search_object:
        if intent_message.slots.home_object.first().value is not None:
            slot_value = intent_message.slots.home_object.first().value
            slot_score = 0
            print("Slot value " + slot_value)
            for slot in intent_message.slots.home_object:
                slot_score = slot.confidence_score
            print("Slot score ", str(slot_score))

    # Validate heard the object correctly
    if search_object:
        if slot_score < 0.80:
            sentence += 'did you say you want to look for ' + str(slot_value) + '... please ask again'
            search_object = False

    # Handle unknown objects
    if search_object:
        if slot_value == "unknownword":
            sentence += "i do not know that object. please ask again"

    # Respond to user
    if search_object:
        sentence += 'you want to look for ' + slot_value
        global pClient
        pClient.publish("voice_assistant/user_requests", slot_value)
        hermes.publish_end_session(session_id, sentence)
    else:
        hermes.publish_end_session(session_id, sentence)


print("Loading pClient")
pClient = mqtt.Client("python2")
pClient.on_connect = on_connect
pClient.on_log = on_log
pClient.on_disconnect = on_disconnect
pClient.on_message = on_message
pClient.connect(broker)
pClient.loop_start()
pClient.subscribe("seeker/processed_requests")
pClient.subscribe("hermes/nlu/intentNotRecognized")

print("Subscribed to backend")

print("Loading hermes")
with Hermes(MQTT_ADDR) as h:
    h.subscribe_intents(intent_received).start()
    print("subscribed to intents")