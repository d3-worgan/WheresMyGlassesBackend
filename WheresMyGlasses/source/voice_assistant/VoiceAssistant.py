from WheresMyGlasses.source.voice_assistant.Validator import Validator
from WheresMyGlasses.source.voice_assistant.MessageBuilder import MessageBuilder


class Assistant:
    def __init__(self):
        print("Hello I am the assistant")
        self.database = ["pigeon", "glasses", "dentures"]

    def process_request(self):
        print("Processing request")

    def validate_user_input(self, intent, object_slot, asr_confidence):

        message = ""

        valid_intent = False
        valid_input = False
        validate_input = False
        poor_input = False
        object_recognised = False

        if Validator.input_was_definite(asr_confidence):
            valid_input = True
        elif Validator.input_was_certain(asr_confidence):
            validate_input = True
        else:
            poor_input = True

        if valid_input:
            if Validator.object_in_database(object_slot, self.database):
                object_recognised = True
        elif validate_input:
            message = MessageBuilder.construct_check_input_message(object_slot)
        elif poor_input:
            message = MessageBuilder.construct_bad_input_message()

        if valid_input and object_recognised:
            message = MessageBuilder.construct_search_message(object_slot)

        if valid_input and not object_recognised:
            message = MessageBuilder.construct_unknown_object_message(object_slot)

        print(message)


    def verbalise_message(self):
        print("Here is my message to you")

    def sendSearchRequest(self):
        print("Asking the object locater to search for your item")


assistant = Assistant()


print("assistant.validate_user_input(""search_for_objects"", ""glasses"", 90)")
assistant.validate_user_input("search_for_objects", "glasses", 90)

print("assistant.validate_user_input(""search_for_objects"", ""pigeon"", 90)")
assistant.validate_user_input("search_for_objects", "pigeon", 90)

print("assistant.validate_user_input(""search_for_objects"", ""dentures"", 90)")
assistant.validate_user_input("search_for_objects", "dentures", 90)

print("assistant.validate_user_input(""search_for_objects"", ""piano"", 90)")
assistant.validate_user_input("search_for_objects", "piano", 90)

print("assistant.validate_user_input(""play_music"", ""glasses"", 90)")
assistant.validate_user_input("play_music", "glasses", 90)

print("assistant.validate_user_input(""search_for_objects"", ""glasses"", 81)")
assistant.validate_user_input("search_for_objects", "glasses", 81)

print("assistant.validate_user_input(""search_for_objects"", ""glasses"", 80)")
assistant.validate_user_input("search_for_objects", "glasses", 80)

print("assistant.validate_user_input(""search_for_objects"", ""glasses"", 79)")
assistant.validate_user_input("search_for_objects", "glasses", 79)

print("assistant.validate_user_input(""search_for_objects"", ""glasses"", 69)")
assistant.validate_user_input("search_for_objects", "glasses", 69)

# assistant.validate_user_input("search_for_objects", "pigeon", 90)
# assistant.validate_user_input("search_for_objects", "dentures", 90)
# assistant.validate_user_input("search_for_objects", "piano", 90)
# assistant.validate_user_input("play_music", "glasses", 90)
# assistant.validate_user_input("search_for_objects", "glasses", 81)
# assistant.validate_user_input("search_for_objects", "glasses", 80)
# assistant.validate_user_input("search_for_objects", "glasses", 79)
# assistant.validate_user_input("search_for_objects", "glasses", 69)


