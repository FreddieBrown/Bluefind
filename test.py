def get_sequence_number(message):
    message_parts = message.split("\x01")
    print("Sequence Number: {}".format(message_parts[0]))
    return message_parts[0], message_parts[1]
	
	
print(get_sequence_number('0\x011=(52.281807, -1'))
