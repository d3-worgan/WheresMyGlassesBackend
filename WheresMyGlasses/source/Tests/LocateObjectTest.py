from WheresMyGlasses.source.search_assistant.ObjectLocator import ObjectLocator
from WheresMyGlasses.source.voice_assistant.MessageBuilder import MessageBuilder

ol = ObjectLocator(100)

requested_object = "bottle"

pair = ol.locate_object(requested_object)
message = None

if pair is not None:
    print(pair.object1)
    print(pair.object2)

if pair is None:
    message = MessageBuilder.construct_not_found_message(requested_object)
else:
    message = MessageBuilder.construct_location_message(pair.object1, pair.object2)

print(message)