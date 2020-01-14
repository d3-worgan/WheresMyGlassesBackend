from WheresMyGlasses.source.ConnectionTests.BackendResponse import BackendResponse

class MessageBuilder:
    """
    Class containing a number of output messages that can be sent to the text to speech engine
    """
    def __init__(self):
        print("Verbalising a message")

    @staticmethod
    def single_location_current_snapshot(br):
        """
        Construct a message describing where the required object is using the info
        from the back end.
        :param located_object: String, the name of object located
        :param location: String, where the object is located or nearby
        :return:
        """
        br = BackendResponse()
        message = f"I just seen a {br.locations_identified[0].object} by the " \
                  f"{br.locations_identified[0].location}"
        return message

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
    def construct_unknown_object_message(br):
        """
        Construct a message explaining the system does not recognise that object
        :param unknown_object:
        :return:
        """
        message = f"I've never heard of {br.original_request} before, but maybe I can help you " \
                  f"find something else"
        return message

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


