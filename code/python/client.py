from __future__ import absolute_import, print_function, unicode_literals

import sys
import dbus
import array
import signal
from gattlib import GATTRequester, GATTResponse, DiscoveryService
import time

import bluezutils, exceptions



class Client():
	SERVICE_UUID =  '0000FFF0-0000-1000-8000-00805f9b34fb'
	RW_UUID = '0000FFF1-0000-1000-8000-00805f9b34fb'

	def __init__(self, location, device_address):
		self.device_address = device_address
		self.location = location
		self.requester = None
		self.target_address = None
		self.discovery = DiscoveryService("hci0")
		self.message = None

	def prepare_device(self, target_address, connect=True):
		self.requester = GATTRequester(target_address, connect)
		self.target_address = target_address

	def write_value(self, handle, data):
		if not self.requester:
			print("Cannot write as no device to send to")
		else:
			print("Writing data")
			self.requester.write_cmd(handle, data)



	def read_value(self):
		if not self.requester:
			print("Cannot write as no device to read from")
			return None
		else:
			response = GATTResponse()
			print("Reading data")
			self.requester.read_by_uuid_async(self.RW_UUID, response)
			while not response.received():
				time.sleep(0.1)	

			print("Response: {}".format(response.received()))
			if len(response.received()) is 0:
				return '' 
			return response.received()[0]
	
	def disconnect(self):
		if not self.requester:
			print("No connected device so cannot disconnect")
		else:
			print("Disconnecting device")
			self.requester.disconnect()
	
	def is_connected(self):
		if not self.requester:
			return False
		else:
			return self.requester.is_connected()
	def discover(self, timeout):
		return self.discovery.discover(timeout)
	def reconnect(self, chances):
		if self.requester is None:
			print("No device to reconnect with")
		else:
			for i in range(chances):
				self.requester.connect()
				if self.is_connected():
					break

	def device_characteristics(self):
		while not self.is_connected():
			time.sleep(0.1)
		response = GATTResponse()
		self.requester.discover_characteristics_async(response)
		while not response.received():
			time.sleep(0.1)
			
		print("Characteristics for {}: {}".format(self.target_address, response.received()))
		return response.received()
	
	def update_location(self, location):
		self.location = location

	def set_message(self, message):
		self.message = message
	
	def send_message(self, handle):
		if not self.requester:
			print("No connected device so cannot write message")
			return None
		elif not self.message:
			print("Need to provide a message to send")
			return None
		else:
			message_buffer = bluezutils.split_message(self.message)
			seq = 0
			for i in message_buffer:
				# Uses a sequence number to let server know which packet in sequence it is
				# Can do up to a max of 99 packets in sequence
				mess_with_seq = str(seq)+"\x01"+i
				print("Writing: {}".format(mess_with_seq))
				cli.write_value(handle, mess_with_seq)
				seq += 1
			print("Written whole message to {}".format(self.target_address))
	
	def read_message(self):
		if not self.requester:
			print("No connected device so cannot read message")
			return None
		message = []
		first_mess = False
		while True:
			recvd = bluezutils.from_byte_array(self.read_value())
			seq_num, data = bluezutils.get_sequence_number(recvd)
			if not first_mess:
				first_mess = (int(seq_num) == 0)
			if first_mess:
				if str(chr(5)) not in data:
					message.append(data)
				else:
					message.append(data.strip(str(chr(5))))
					break
		print("Read whole message from {}".format(self.target_address))	
		return ''.join(message)
		

cli = Client("52.281799, -1.532315", bluezutils.get_mac_addr(dbus.SystemBus()))

def sig_handler(signal_number, frame):
	print('Received: '+str(signal_number))
	try:
		cli.disconnect()
	except:
		print("Error disconnecting")
	raise SystemExit('Exiting...')
	return

"""

1. Start to Discover devices and information about them DONE
2. Get the devices which utilise the EmergencyService DONE
3. Connect to that device (if it wasn't the last seen device (only ok if 1 device visible) ) DONE
4. Read data from the connected device
5. Write data to connected device DONE
6. Split up and save message
7. Disconnect device DONE
8. Go back to step 2 DONE

"""

if __name__ == '__main__':
	signal.signal(signal.SIGINT, sig_handler)
	print("Starting")

	while True:
		# Build message at start of each iteration
		message = bluezutils.build_message([cli.location], [cli.device_address])
		cli.set_message(message)
		# Search for devices
		devices = cli.discover(5)
		# Go through discovered devices and print them
		for address, name in list(devices.items()):
			print("Device: {} {}".format(address, name))
			# If one has an EmergencyAdvertisement name, investigate it
			if "EmergencyAdvertisement" in name:
				# Connect to the device
				cli.prepare_device(address)
				# Get characteristics of the device (its attributes)
				chrcs = cli.device_characteristics()
				for dev in chrcs:
					# Go through the dict and inspect the UUIDs
						# If one of them is the same as the emergency UUID, allow it to talk to it
					if dev['uuid'].lower() == cli.RW_UUID.lower():
						# Get the handle of the service
						print("Handle: {}, Properties: {}, Value Handle {}".format(dev['handle'], dev['properties'], dev['value_handle']))
						handle = int(dev['value_handle'])
						# Read a value from the server
						data = cli.read_message()
						print("Data from device: {}".format(data))
						# Write the whole planned message to the server
						cli.send_message(handle)
				# Otherwise, disconnect from device
				cli.disconnect()
	print("Done")
	