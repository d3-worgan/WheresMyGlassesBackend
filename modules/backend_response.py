import json
from datetime import datetime
import time


class BackendResponse:
    """
    Used to structure the location data to satisfy the request. Object can be flattened into a json string for transmition
    over mqtt to the location decoder
    """
    def __init__(self, code_name, original_request, location_time, locations_identified, stream_manager):
        print("Creating a backend response")
        self.code_name = code_name
        self.original_request = original_request
        self.location_time = location_time
        self.location_time_passed = self.minutes_passed()
        self.locations_identified = locations_identified
        self.stream_manager = stream_manager

    def minutes_passed(self):
        if self.location_time:
            current_time = datetime.now()
            print("Current time ", current_time)
            print("Location time ", self.location_time)
            passed = current_time - self.location_time
            minutes_passed = passed.seconds / 60
            return round(minutes_passed, 2)

    def pack(self):
        """
        Pack the objects information into a json object so that it can be transmitted over
        MQTT.
        :return: A json object containing the BackendResponse
        """
        package = {}
        package['code_name'] = self.code_name
        package['original_request'] = self.original_request
        package['location_time'] = str(self.location_time)
        package['minutes_passed'] = str(self.location_time_passed)
        locations_identified = []
        for location in self.locations_identified:
            print("Pre-ID " + location.camera_id)
            location.camera_id = self.stream_manager.camNames[location.camera_id]
            print("Post ID " + location.camera_id)
            locations_identified.append(location.to_json())
        package['locations_identified'] = locations_identified
        return json.dumps(package)

    def print(self):
        print("Code name: ", self.code_name)
        print("Original Request: ", self.original_request)
        print("Location_time: ", self.location_time)
        print("Locations: ")
        for loc in self.locations_identified:
            print(loc.object + " " + loc.location)
