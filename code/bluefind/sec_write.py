def WriteValue(self, value, options):
		"""
		Function to send data to the server. This is an implementation of 
		the standard WriteValue function. In this, the MAC address of the 
		connecting device is found and the received message is broken down 
		into its sequence number and message. If that device has already 
		written messages to the server and the message is the next expected 
		message, then it is added to the message buffer associated with that 
		connected device. If that is the last part of the message, connect the 
		message parts and save it to the database. If it is the first fragment of 
		the message, create a message buffer for the device. Otherwise, do nothing.
		"""
	print("Secure Write")
	dev = bluezutils.dbus_to_MAC(options['device'])
	sequence_num, message = bluezutils.get_sequence_number(bluezutils.from_byte_array(value))
	print("Value being Written!: "+message)
	print("Sequence Number: "+sequence_num)
	global_place = sequence_num[:len(sequence_num)-1]
	local_place = sequence_num[len(sequence_num)-1:len(sequence_num)]
	if (dev in self.write_states.keys()) and  int(sequence_num) is len(self.write_states[dev]):
		"""
		- Get message and split into message and sequence number
		- Check if in encryption mode
		- Build local list for messages 
		- Add each local segment to list
		- When the global segment ends, concat local segment pieces and decrypt and add to global message list
		- When chr(5) has been received, get global list and concat it to get full message then move on
		"""
		if self.encrypt:
			if int(local_place) == 0 and int(global_place) == 0:
				"""
				create place in lists for this device
				"""
				pass
			elif int(local_place) == 0:
				"""
				Create entry in local list
				"""
				pass
			elif int(local_place) == 9:
				"""
				This should take the local_list, concat it, decrypt it and add it to global list
				and then empty the local list
				"""
				pass
			else:
				"""
				Add message to local list
				"""
				pass
		elif message == chr(5):
			"""
			This is the end of the whole message
			This should concat the global_list, get the keys of the message and add to db, 
			then del from global_list 
			"""

def ReadValue(self, options):
	"""
		- Build message
		- Check length
		- Break down into segments which can be encrypted and give each one a seq number
		- Encrypt each segment of the message
		- Try and send each segment. For each one, break down into 15 byte segments and 
		send each one with large segment seq number + local seq and denim plus the message segment
	"""
	pass
		

def encrypted_client_actions(cli, address):
	"""
			WRITE:

			- Build message
			- Check length
			- Break down into segments which can be encrypted and give each one a seq number
			- Encrypt each segment of the message
			- Try and send each segment. For each one, break down into 15 byte segments and send 
			each one with large segment seq number + local seq and denim plus the message segment

			READ:

			- Get message and split into message and sequence number
			- Check if in encryption mode
			- Build local list for messages 
			- Add each local segment to list
			- When the global segment ends, concat local segment pieces and decrypt and add to global message list
			- When chr(5) has been received, get global list and concat it to get full message then move on


	"""
	pass