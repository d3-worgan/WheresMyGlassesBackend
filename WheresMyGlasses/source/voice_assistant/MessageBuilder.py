

class MessageBuilder:
    """
    Class containing a number of output messages that can be sent to the text to speech engine
    """
    def __init__(self):
        print("Verbalising a message")

    @staticmethod
    def construct_location_message(located_object, location):
        """
        Construct a message describing where the required object is using the info
        from the back end.
        :param located_object: String, the name of object located
        :param location: String, where the object is located or nearby
        :return:
        """
        # print("The " + located_object + " is by the " + location)
        return "The " + located_object + " is by the " + location

    @staticmethod
    def construct_not_found_message(lost_object):
        """
        Construct a message explaining that the system could not find the specified
        object.
        :param lost_object: A String describing the lost object
        :return:
        """
        # print("The system could not find " + lost_object)
        return "The system could not find " + lost_object

    @staticmethod
    def construct_unknown_object_message(unknown_object):
        """
        Construct a message explaining the system does not recognise that object
        :param unknown_object:
        :return:
        """
        # print("Ive never heard of pizza pie before, but might be able to help you with something else")
        return "Ive never heard of " + unknown_object + " before, but might be able to help you with something else"

    @staticmethod
    def construct_check_input_message(potential_object):
        """
        Construct a message explaining the system wants to confirm the object being searched for
        :param potential_object:
        :return:
        """
        # print("I didnt quite hear that. Did you say you want to look for " + potential_object)
        return "Did you say you want to look for " + potential_object

    @staticmethod
    def construct_bad_input_message():
        """
        Construct a message explaining that the system had a low confidence score in the
        speech recognition.
        :return:
        """
        # print("I did not hear that properly, please ask again a bit louder")
        return "I did not hear that properly, please ask again a bit louder"

    @staticmethod
    def construct_bad_intent_message(intent):
        """
        Construct a message explaining that the system does not understand that particular intent
        and cannot help
        :param intent:
        :return:
        """
        # print("I don't think I can do that, I can help you search for items")
        return "I don't think I can do that, I can help you search for items"

    @staticmethod
    def construct_search_message(object):
        """
        Construct a message confirming we are going to search for the requested object
        :param object: String, describing the object to search for
        :return:
        """
        # print("Okay, lets look for the " + object)
        return "Okay, lets look for the " + object + "..."


# MessageBuilder.construct_location_message("glasses", "head")
# MessageBuilder.construct_check_input_message("glasses")
# MessageBuilder.construct_unknown_object_message("pizza pie")
# MessageBuilder.construct_not_found_message("glasses")
# MessageBuilder.construct_bad_input_message()
# MessageBuilder.construct_bad_intent_message("play_music")