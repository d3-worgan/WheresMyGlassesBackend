from WheresMyGlasses.source.search_assistant.ObjectLocator import ObjectLocator
from WheresMyGlasses.source.voice_assistant.MessageBuilder import MessageBuilder


# TEST/DEMO
# Capture some samples
# Choose an item to request
# Search the room or the history to see if the object was located

# System running
ol = ObjectLocator(100)
i = 0
while i < 100:
    ol.add_snapshot_to_history(i)
    i += 1

# 'Received request'
requested_object = "bottle"

# Process request
pair = ol.locate_object(requested_object)

# Output
if pair is None:
    message = MessageBuilder.construct_not_found_message(requested_object)
else:
    message = MessageBuilder.construct_location_message(pair.object1, pair.object2)

print(message)