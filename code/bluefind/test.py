from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import array

def generate_RSA_keypair():
	key = RSA.generate(1024)
	private = key.export_key()
	public = key.publickey().export_key()
	return {
		"private" : private,
		"public" : public,
	}

def build_generic_message(message_struct):
	"""
	Takes a dict where keys are tags, and each has a list with
	values for that tag, e.g 
	{
		1 : [...],
		2 : [...],
		3 : [...],
	}
	"""
	message = ""
	for key, value in message_struct.items():
		for item in value:
			message+="{}={}|".format(key, item)
	return message


def from_byte_array(val_arr):
	"""
	When provided with a list of bytes, the function will convert 
	it into an ASCII string and will return it.
	"""
	med_arr = []
	# Take byte array and work out character of each value
	for value in val_arr:
		med_arr.append(chr(value)) 
	# With each character, add it to a string
	ret_string = ''.join(med_arr)
	# return string
	return ret_string

def to_byte_array(value):
	"""
	This function will take a string and will split it 
	down into an array of bytes. This will then be returned.
	"""
	# Convert string into some sort of char array
	char_arr = list(value)
	ret_list = []
	# For each member of the char array, get the ASCII code for each character
	for char in char_arr:
		ascii_v = ord(char)
		# Take each ASCII code and create a dbus.Byte object with it and add it to another array
		ret_list.append(bytes(ascii_v))
	# Once byte array built, return
	return ret_list

def from_byte_array(val_arr):
	"""
	When provided with a list of bytes, the function will convert 
	it into an ASCII string and will return it.
	"""
	med_arr = []
	# Take byte array and work out character of each value
	for value in val_arr:
		med_arr.append(chr(value)) 
	# With each character, add it to a string
	ret_string = ''.join(med_arr)
	# return string
	return ret_string

def encrypt_message(public_key, message):
	key = RSA.importKey(public_key)
	cipher_rsa = PKCS1_OAEP.new(key)
	return cipher_rsa.encrypt(str.encode(message))

def decrypt_message(private_key, ciphertext):
	key = RSA.importKey(private_key)
	cipher = PKCS1_OAEP.new(key)
	return cipher.decrypt(ciphertext).decode()

def split_message(message, delim=chr(5), size=15, frags=None):
	"""
	Method splits message into 16byte chunks so they can be transmitted 
	using Bluetooth. 
	"""
	print("Splitting message")
	byte_arr = []
	message_len = len(message)
	if int(message_len/size) == 0:
		byte_arr.append(message)
	elif frags:
		size = round(message_len/frags)
		print(size)
		for i in range(0, int(message_len/size)):
			j = (i+1)*size
			byte_arr.append(message[i*size:j])
		if message_len%size is not 0:
			byte_arr.append(message[(i+1)*size:(i+1)*size+message_len%size])
	else:
		for i in range(0, int(message_len/size)):
			j = (i+1)*size
			byte_arr.append(message[i*size:j])
		if message_len%size is not 0:
			byte_arr.append(message[(i+1)*size:(i+1)*size+message_len%size])
	if delim:
		byte_arr.append(delim)
	return byte_arr

def bytestring_to_uf8(buffer):
	"""
	Converts a bytestring string.
	"""
	list_of_vals = list(buffer)
	utf_str = ""
	for i in list_of_vals:
		utf_str += chr(i)
	return utf_str

def utf_to_value_list(buffer):
	"""
	Converts a string to a list of ASCII character 
	values.
	"""
	list_of_vals = list(buffer)
	value_list = []
	for i in list_of_vals:
		value_list.append(ord(i))
	return value_list

def utf_to_byte_string(buffer):
	value_list = utf_to_value_list(buffer)
	return array.array('B', value_list).tobytes()

keypair = generate_RSA_keypair()

fun_message = b'You can attack now!'
other_message = "Hey there, I'm a string blah blah blah blahfdskbdsfbkjfdbfdbhsdsfhjrebuycjkasdb  xhfhhjdfshbfdjkhnfbsdhfgdnbhfgyehuijnsfbdhdgyehuijdskncvbhgdfuisjknxcbvhfgduisokmlcnvbgfhjuiodsklmcxnvbjhfg"
splitup = split_message(other_message, delim=None, size=62)
print(splitup)
global_list = []
for mess in splitup:
	cipher = encrypt_message(keypair['public'], mess)
	cipherstr = bytestring_to_uf8(cipher)
	print("Cipher: {}, Len: {}".format(cipherstr, len(cipherstr)))
	print("Broken Cipher: {}".format(len(split_message(cipherstr, delim=None, size=15))))
	message_parts = split_message(cipherstr)
	second_part = "".join(message_parts).strip(chr(5))
	recon = utf_to_byte_string(second_part)
	global_list.append(decrypt_message(keypair['private'], recon))
	print("Decrypted Message: {}".format(decrypt_message(keypair['private'], recon)))

print("Final Message: {}".format("".join(global_list)))