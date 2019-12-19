from WheresMyGlasses.source.search_assistant.ObjectLocator import ObjectLocator
from WheresMyGlasses.source.voice_assistant.MessageBuilder import MessageBuilder
import keyboard


ol = ObjectLocator(100)
requested_object = "bottle"

pair = None
message = None

# while not found
# maintain a list of 100 snapshots
# Show an object to locate e.g. bottle on the dining table
# When the 100 snapshots are done it will search back through and find it

found = False
pair = None
i = 0

while i < 100:
    ol.add_snapshot_to_history(i)
    i += 1

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