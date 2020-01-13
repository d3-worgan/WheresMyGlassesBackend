import json

class LocatedObject:
    """
    A pair of objects which were located near each other
    """
    def __init__(self, object, location):
        self.object = object
        self.location = location

    def to_json(self):
        data = {}
        data['object'] = self.object
        data['location'] = self.location
        json_data = json.dumps(data)
        return json_data


class BackendResponse:
    def __init__(self, code_name, location_time, locations_identified):
        self.code_name = code_name
        self.location_time = location_time
        self.locations_identified = []
        for loc in locations_identified:
            lo = LocatedObject(loc['object'], loc['location'])
            self.locations_identified.append(lo)

    def print(self):
        print("Code name: ", self.code_name)
        print("Location_time: ", self.location_time)
        for loc in self.locations_identified:
            print(loc.location + " " + loc.location)

def to_json():

    loc1 = LocatedObject('glasses', 'head')
    loc2 = LocatedObject('glasses', 'dining_table')

    data = {}
    data['code_name'] = 'code_1'
    data['camera_name'] = 'kitchen_camera'
    data['location_time'] = '12:00'
    data['locations_identified'] = [loc1.to_json(), loc2.to_json()]
    json_data = json.dumps(data)
    return json_data

response = to_json()

process = json.loads(response)

print(process)

br = BackendResponse(process['code_name'], process['location_time'], process['locations_identified'])

br.print()