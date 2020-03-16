import json
from WheresMyGlasses.ObjectLocator.located_object import LocatedObject
from WheresMyGlasses.ObjectLocator.backend_response import BackendResponse

print(LocatedObject)

print("Request received / locating objects...")
loc1 = LocatedObject('glasses', 'head')
loc2 = LocatedObject('glasses', 'dining_table')
loc3 = LocatedObject('glasses', 'toilet')

print("Objects located, producing response...")
ber = BackendResponse('6', '22:11', None)
ber.locations_identified.append(loc1)
ber.locations_identified.append(loc2)
ber.locations_identified.append(loc3)
print("Final response")
ber.print()

print("Transmitting response...")
transmit = ber.pack()
print(transmit)

print("Response received.")
received = json.loads(transmit)
print("Unpacking response")
fer = BackendResponse(received['code_name'], received['location_time'], received['locations_identified'])
print("Received response")
fer.print()