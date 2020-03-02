import sys
import dbus
import array
import signal
import bluepy
from bluepy.btle import Scanner, UUID, Peripheral, DefaultDelegate
import time
import datetime
import sys

import bluezutils, exceptions
from db import Database

class Client():
	"""
	This class has been created to make it easier to deal 
	with all the clientside functionalith which is needed
	for this project. It holds all the necessary objects 
	and methods which can all be used with the object.
	"""
	SERVICE_UUID =  '0000FFF0-0000-1000-8000-00805f9b34fb'
	NORMAL_UUID = '0000FFF1-0000-1000-8000-00805f9b34fb'
	SECURE_UUID = '0000FFF2-0000-1000-8000-00805f9b34fb'
	EM_UUID = '0000FFF3-0000-1000-8000-00805f9b34fb'

	def __init__(self, location, device_address):
		self.device_address = device_address
		self.location = location
		self.peripheral = None
		self.service = None
		self.characteristic = None
		self.target_address = None
		self.scanner = Scanner()
		self.message = None
		self.db = Database('find.db')
		self.keypair = bluezutils.generate_RSA_keypair()

	def prepare_device(self, target_address):
		"""
		This function will start a connection with a 
		device at `target_address` and will get the 
		handle of the desired characteristic which it 
		has. Its service and characteristics which are 
		relavant are also stored in the object.
		"""
		self.peripheral = Peripheral(target_address)
		self.service = self.peripheral.getServiceByUUID( self.SERVICE_UUID )
		self.target_address = target_address

	def write_value(self, data, response=False):
		"""
		This method is used to write a value to a connected 
		device. 
		"""
		if not self.peripheral:
			print("Cannot write as no device to send to")
		else:
			if response:
				return self.peripheral.writeCharacteristic(self.handle, data, True) 
			self.peripheral.writeCharacteristic(self.handle, data)

	def read_value(self):
		"""
		This function is used to read a value from a connected 
		device.
		"""
		if not self.peripheral:
			print("Cannot write as no device to read from")
			return None
		else:
			return self.characteristic.read()
	
	def disconnect(self):
		"""
		Function used to end connection with connected device
		"""
		if not self.peripheral:
			print("No connected device so cannot disconnect")
		else:
			print("Disconnecting device")
			self.peripheral.disconnect()

	def discover(self, timeout):
		"""
		Function to start the discovery of devices while 
		using over a specific time period.
		"""
		return self.scanner.scan(timeout)

	def reconnect(self, chances):
		"""
		Function to make it easier for device to 
		connect to a device at `target_address`.
		"""
		if self.peripheral is None:
			print("No device to reconnect with")
		else:
			self.peripheral.connect(self.target_address)
	
	def update_location(self, location):
		"""
		Function to change the location data for the 
		client device.
		"""
		self.location = location
	
	def set_characteristic(self, uuid):
		self.characteristic = self.service.getCharacteristics( uuid )[0]
		self.handle = self.characteristic.getHandle()

	def set_message(self, message):
		"""
		Function to set the message which will be sent to other 
		devices.
		"""
		self.message = message
	
	def send_message(self):
		"""
		This function will take the message set in the object and 
		will break it down. It will then convert the message into 
		an array of bytes and write the array to the connected 
		server. If it loses connection, it will try to reconnect 
		and send it again.
		"""
		print("Sending Message")
		if not self.peripheral:
			print("No connected device so cannot write message")
			return None
		elif not self.message:
			print("Need to provide a message to send")
			return None
		else:
			message_buffer = bluezutils.split_message(self.message)
			print("Message Buffer: {}".format(message_buffer))
			seq = 0
			for i in message_buffer:
				# Uses a sequence number to let server know which packet in sequence it is
				# Can do up to a max of 99 packets in sequence
				mess_with_seq = str(seq)+"\x01"+i
				print("Writing: {}".format(mess_with_seq))
				try: 
					ret = self.write_value(bytearray(bluezutils.to_byte_array(mess_with_seq)), True)
					print("Returned Value: {}".format(ret))
				except:
					self.reconnect(5)
					ret = self.write_value(bytearray(bluezutils.to_byte_array(mess_with_seq)), True)
					print("Returned Value: {}".format(ret))
				seq += 1
			print("Written whole message to {}".format(self.target_address))
	
	def send_secure_message(self, key):
		print("Sending Secure Message")
		msg_parts = bluezutils.split_message(self.message, delim=None, size=62)
		print("Message to send: {}".format(self.message))
		for i in range(0, len(msg_parts)):
			print("Encrypt Message")
			enc_seg = bluezutils.encrypt_message(key, msg_parts[i])
			broken_enc_seg = bluezutils.split_message(enc_seg, delim=None, size=15)
			for j in range(0, len(broken_enc_seg)):
				sequence = str(i)+""+str(j)+"\x01"
				message = sequence+broken_enc_seg[j]
				try: 
					ret = self.write_value(bytearray(bluezutils.to_byte_array(message)), True)
					print("Returned Value: {}".format(ret))
				except:
					self.reconnect(5)
					ret = self.write_value(bytearray(bluezutils.to_byte_array(message)), True)
					print("Returned Value: {}".format(ret))
		print("Written whole message to {}".format(self.target_address))
	
	def read_message(self):
		"""
		This function will keep reading from the server 
		until it has messages in an array where their 
		sequence numbers start with 0 and go up until 
		a message is received which contains chr(5). 
		This means it is the final part of the message. 
		The message is then created from the stored 
		message fragments and is stored in the database.
		"""
		if not self.peripheral:
			print("No connected device so cannot read message")
			return None
		message = []
		first_mess = False
		recvd = ''
		while True:
			try:
				recvd = bluezutils.from_byte_array(self.read_value())
			except:
				self.reconnect(5)
				recvd = bluezutils.from_byte_array(self.read_value())
			seq_num, data = bluezutils.get_sequence_number(recvd)
			if not first_mess:
				first_mess = (int(seq_num) == 0)
			if first_mess:
				if str(chr(5)) != data:
					message.append(data)
				else:
					print("End of message")
					message.append(data)
					break
		print("Read whole message from {}".format(self.target_address))	
		# join up whole message
		full_message = ''.join(message)
		print("Read Message: {}".format(full_message))
		# break down whole message
		return full_message
	
	def read_secure_message(self):
		if not self.peripheral:
			print("No connected device so cannot read message")
			return None
		print("Reading Secure Message")
		global_message = []
		local_message = []
		while True:
			try:
				recvd = bluezutils.from_byte_array(self.read_value())
			except:
				self.reconnect(5)
				recvd = bluezutils.from_byte_array(self.read_value())
			seq_num, data = bluezutils.get_sequence_number(recvd)
			global_place = int(seq_num[:len(seq_num)-1])
			local_place = int(seq_num[len(seq_num)-1:len(seq_num)])
			if data == chr(5):
				return "".join(global_message)
			elif local_place == 9:
				local_frag = "".join(local_message)
				print("Decrypt Message")
				decrypted = bluezutils.decrypt_message(self.keypair['private'], local_frag)
				global_message.append(decrypted)
			else:
				local_message.append(data)


def sig_handler(signal_number, frame):
	"""
	This is the signal handler for the client side 
	to ensure exiting the program happens in an orderly
	way.
	"""
	print('Received: '+str(signal_number))
	raise SystemExit('Exiting...')
	return

def start_client(func):
	"""
	This function will startup client functionality and will perform 
	the actions needed for the client to function. This function could 
	be re-written to perform different functions for the client. For example, 
	an emergency service node wouldn't need to write data to the server. 
	This method will discover nearby devices, find one which offers the 
	correct service and will read and write to the server before disconnecting. 
	This behvaiour will continue until the program is ended.
	"""
	cli = Client("52.281799, -1.532315", bluezutils.get_mac_addr(dbus.SystemBus()))
	print("Starting Client")
	while True:
		devices = cli.discover(5.0)
		for dev in devices:
			print("Scan Data: {}".format(dev.getScanData()))
			have_service = False
			if len(dev.getScanData()) >= 3:
				for uno in dev.scanData.keys():
					print("getValueText ",dev.getValueText(uno))
					if dev.getValueText(uno).lower() == cli.SERVICE_UUID.lower():
						have_service = True
			if have_service:
				func(cli, dev.addr)
				

def normal_client_actions(cli, address):
	"""
	Function to perform normal client behaviour with a 
	server, whose address is passed to the function. This 
	will get relevant information to send, created a message
	and sets it. It then read a messafe from the server and 
	saves that information to the database, before sending 
	its own message.
	"""
	print("Normal Client Action")
	db_data = cli.db.select(50)
	db_data[0].append(cli.location)
	db_data[1].append(cli.device_address)
	message = bluezutils.build_message(db_data[0], db_data[1], [address.upper()])
	cli.set_message(message)
	try:
		cli.prepare_device(address)
		cli.set_characteristic(cli.NORMAL_UUID)
		found_message = bluezutils.break_down_message(cli.read_message())
		bluezutils.add_to_db(cli.db, found_message)
		cli.send_message()
		cli.disconnect()
	except Exception as e:
		print("Connection Error for {}: {}".format(address, e))

def emergency_service_actions(cli, address):
	"""
	Function to perform emergency services client behaviour with a 
	server, whose address is passed to the function. This will connect 
	to a device and inform it of its status. After this, it will read 
	special extra information from the server, as well as a normal 
	message read. It will giet all of this information and will store 
	it in its database.
	"""
	print("Emergency Service Action")
	request_message = bluezutils.build_generic_message({5:[chr(6)]})
	cli.set_message(request_message)
	try:
		cli.prepare_device(address)
		cli.set_characteristic(cli.EM_UUID)
		cli.send_message()
		found_message = bluezutils.break_down_message(cli.read_message())
		bluezutils.add_to_db_em(cli.db, found_message)
		found_message = bluezutils.break_down_message(cli.read_message())
		bluezutils.add_to_db(cli.db, found_message)
		cli.disconnect()
	except Exception as e:
		print("Connection Error for {}: {}".format(address, e))

def encrypted_client_actions(cli, address):
	"""
		- Key Exchange

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
	print("Encrypted Client Action")
	db_data = cli.db.select(3)
	db_data[0].append(cli.location)
	db_data[1].append(cli.device_address)
	message = bluezutils.build_message(db_data[0], db_data[1], [address.upper()])
	try:
		# Key exchange
		cli.prepare_device(address)
		cli.set_characteristic(cli.SECURE_UUID)
		key_message = bluezutils.build_generic_message({3:[cli.keypair['public']]})
		cli.set_message(key_message)
		cli.send_message()
		print("Get Server Key")
		server_key = bluezutils.break_down_message(cli.read_message())
		if "3" in server_key.keys():
			print("Received public key")
			print("Key Size: {}".format(len(self.keypair["public"])))
			cli.set_message(message)
			print("Get message")
			msg = cli.read_secure_message()
			print("Message recevied: {}".format(msg))
			print("Send Message")
			# cli.send_secure_message(server_key["3"][0])
			# message_parts = bluezutils.break_down_message(msg)
			# bluezutils.add_to_db(cli.db, message_parts)
		print("Disconnect")
		cli.disconnect()
	except Exception as e:
		print("Connection Error for {}: {}".format(address, e))

if __name__ == '__main__':
	if len(sys.argv) == 1:
		action = "normal"
	else:
		action = sys.argv[1]

	client_actions = {
		"emergency": emergency_service_actions,
		"normal": normal_client_actions,
		"secure": encrypted_client_actions
	}
	signal.signal(signal.SIGINT, sig_handler)
	start_client(client_actions[action])