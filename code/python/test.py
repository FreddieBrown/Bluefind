from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import struct

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

def split_message(message):
	"""
	Method splits message into 16byte chunks so they can be transmitted 
	using Bluetooth. 
	"""
	print("Splitting message")
	mess_size = 16
	byte_arr = []
	message_len = len(message)
	if int(message_len/mess_size) == 0:
		byte_arr.append(message)
	else:
		for i in range(0, int(message_len/mess_size)):
			j = (i+1)*mess_size
			byte_arr.append(message[i*mess_size:j])
		if message_len%mess_size is not 0:
			byte_arr.append(message[(i+1)*mess_size:(i+1)*mess_size+message_len%mess_size])
	byte_arr.append(chr(5))
	return byte_arr

def remove_bytes(buffer, blacklist):
    b = list()
    for i in list(buffer):
        if i == 194 or i == 195:
            # print('FOUND: {}'.format(i)) # 3 way split
            continue
        else:
            b.append(i)
    print("Recon Len: {}".format(len(bytes(b))))
    return bytes(b)

def test_to_string(buffer):
    list_of_vals = list(buffer)
    empty_str = ""
    for i in list_of_vals:
        empty_str += chr(i)
    return empty_str

keypair = generate_RSA_keypair()
print("{}".format(from_byte_array(keypair['public'])))
print(build_generic_message({
	3 : [keypair['public'], "hello"]
}))

fun_message = b'You can attack now!'
other_message = "Hey there, I'm a string"
cipher = encrypt_message(keypair['public'], other_message)
print("Before: {}".format(list(cipher)))
print("Cipher Length: {}".format(len(cipher)))
cipherstr = test_to_string(cipher)
# print("str value: {}".format(cipherstr))
# print("Ciphertext: {}".format(str.encode(cipherstr)))
print("Cipherstr: {}".format(list(str.encode(cipherstr))))
recon = remove_bytes(str.encode(cipherstr), [194, 195])
print("Same?: {}".format(recon == cipher))
print("Reconstruction: {}".format(list(recon)))
print("Decrypted Message: {}".format(decrypt_message(keypair['private'], recon)))
# print("Decrypted Message: {}".format(decrypt_message(keypair['private'], cipher)))

small_message = "4="+chr(6)
print(split_message(small_message))
print(split_message(other_message))
