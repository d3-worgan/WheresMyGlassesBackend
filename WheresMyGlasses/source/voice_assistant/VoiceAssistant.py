from WheresMyGlasses.source.voice_assistant.Validator import Validator
from WheresMyGlasses.source.voice_assistant.Verbaliser import Verbaliser


class Assistant:
    def __init__(self):
        print("Hello I am the assistant")
        self.database = ["pigeon", "glasses", "dentures"]

    def process_request(self):
        print("Processing request")

    def validate_user_input(self, intent, object_slot, asr_confidence):
        message = ""
        valid_input = True
        validate_input = False
        # Validate the confidence score of the ASR to ensure we don't search for the wrong object
        if valid_input:
            # 80 or above
            if not Validator.input_was_definite(asr_confidence):
                # 70-80, ask for a yes or no
                if not Validator.input_was_certain(asr_confidence):
                    message = Verbaliser.construct_bad_input_message()
                    valid_input = False
                # Less than 70 ask them to ask again
                else:
                    message = Verbaliser.construct_check_input_message(object_slot)
                    validate_input = True

        # Validate the intent received from the user is a valid intent
        if valid_input:
            if not Validator.intent_is_valid(intent):
                message = Verbaliser.construct_bad_intent_message(intent)
                valid_input = False

        # Validate the user has requested a valid object to search for
        if valid_input:
            if not Validator.object_in_database(object_slot, self.database):
                message = Verbaliser.construct_unknown_object_message(object_slot)
                valid_input = False

        # The user passed validation
        if valid_input:
            message = Verbaliser.construct_search_message(object_slot)

        print(message)


    def verbalise_message(self):
        print("Here is my message to you")

    def sendSearchRequest(self):
        print("Asking the object locater to search for your item")


assistant = Assistant()
assistant.validate_user_input("search_for_objects", "glasses", 90)
assistant.validate_user_input("search_for_objects", "pigeon", 90)
assistant.validate_user_input("search_for_objects", "dentures", 90)
assistant.validate_user_input("search_for_objects", "piano", 90)
assistant.validate_user_input("play_music", "glasses", 90)
assistant.validate_user_input("search_for_objects", "glasses", 81)
assistant.validate_user_input("search_for_objects", "glasses", 80)
assistant.validate_user_input("search_for_objects", "glasses", 79)
assistant.validate_user_input("search_for_objects", "glasses", 69)


