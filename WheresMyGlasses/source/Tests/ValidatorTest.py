from WheresMyGlasses.source.voice_assistant.Validator import Validator

print("Validator.input_was_definite(81) " + str(Validator.input_was_definite(81)))
print("Validator.input_was_definite(79) " + str(Validator.input_was_definite(79)))
print("Validator.input_was_certain(71) " + str(Validator.input_was_certain(71)))
print("Validator.input_was_certain(69) " + str(Validator.input_was_certain(69)))
print("Validator.intent_is_valid(""search_for_objects"") " + str(Validator.intent_is_valid("search_for_objects")))
print("Validator.intent_is_valid(""peanuts"")" + str(Validator.intent_is_valid("peanuts")))