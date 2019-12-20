from WheresMyGlasses.source.VoiceAssistant.MessageBuilder import MessageBuilder


print(MessageBuilder.construct_location_message("glasses", "head"))
print(MessageBuilder.construct_check_input_message("glasses"))
print(MessageBuilder.construct_unknown_object_message("pizza pie"))
print(MessageBuilder.construct_not_found_message("glasses"))
print(MessageBuilder.construct_bad_input_message())
print(MessageBuilder.construct_bad_intent_message("play_music"))
