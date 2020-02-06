def split_message(message):
	"""
	Method splits message into 19byte chunks 
	"""
	byte_arr = []
	message_len = len(message)
	for i in range(0, int(message_len/19)):
		j = (i+1)*19
		byte_arr.append(message[i*19:j])
	if message_len%19 is not 0:
		byte_arr.append(message[(i+1)*19:(i+1)*19+message_len%19])
	byte_arr.append(chr(5))
	return byte_arr

print(split_message("Hey there how are you doing? I am doing well"))
