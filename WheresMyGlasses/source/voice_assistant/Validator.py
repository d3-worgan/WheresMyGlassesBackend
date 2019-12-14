class Validator:
    """
    Methods to help validate user input
    """

    @staticmethod
    def input_was_definite(confidence_score):
        """
        Validate that the speech recognition was confident in what the users input was
        :param confidence_score: The speech engines confidence score
        :return: True if the score was above 80% or False otherwise
        """
        if confidence_score >= 80:
            return True
        else:
            return False

    @staticmethod
    def input_was_certain(confidence_score):
        """
        Validate that the speech recognition heard what the user said
        :param confidence_score: The speech engines confidence score
        :return: True if the score was above 70% or False otherwise
        """
        if 80 > confidence_score >= 70:
            return True
        else:
            return False

    @staticmethod
    def object_in_database(object_name, database):
        """
        Validate the requested object is in the object detectors list of classes
        :param object_name: String, name of the object to investigate
        :param database: A list of class names from the detectors trained set
        :return: True of the object can be detected or false if it is not in the list of classes
        """
        for object_class in database:
            if object_name == object_class:
                return True
        return False

    @staticmethod
    def intent_is_valid(intent_name):
        """
        Validate the user has not spoken an invalid intent
        :param intent_name: The intent name the user has spoken
        :return: True if the intent is to search or False otherwise
        """
        if intent_name == "search_for_objects":
            return True
        else:
            return False


# print("Validator.input_was_definite(81) " + str(Validator.input_was_definite(81)))
# print("Validator.input_was_definite(79) " + str(Validator.input_was_definite(79)))
# print("Validator.input_was_certain(71) " + str(Validator.input_was_certain(71)))
# print("Validator.input_was_certain(69) " + str(Validator.input_was_certain(69)))
# print("Validator.intent_is_valid(""search_for_objects"") " + str(Validator.intent_is_valid("search_for_objects")))
# print("Validator.intent_is_valid(""peanuts"")" + str(Validator.intent_is_valid("peanuts")))
