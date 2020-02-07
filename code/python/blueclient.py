import sys
import dbus
import array
import signal
import bluepy
from bluepy.btle import Scanner, UUID, Peripheral, DefaultDelegate
import time

import bluezutils, exceptions




class Client():
	SERVICE_UUID =  '0000FFF0-0000-1000-8000-00805f9b34fb'
	RW_UUID = '0000FFF1-0000-1000-8000-00805f9b34fb'

	def __init__(self, location, device_address):
		self.device_address = device_address
		self.location = location
		self.peripheral = None
		self.service = None
		self.characteristic = None
		self.target_address = None
		self.scanner = Scanner()
		self.message = None

	def prepare_device(self, target_address):
		self.peripheral = Peripheral(target_address)
		self.service = self.peripheral.getServiceByUUID( self.SERVICE_UUID )
		self.characteristic = self.service.getCharacteristics( self.RW_UUID )[0]
		self.handle = self.characteristic.getHandle()
		self.target_address = target_address

	def write_value(self, data):
		if not self.peripheral:
			print("Cannot write as no device to send to")
		else:
			print("Writing data")
			self.peripheral.writeCharacteristic(self.handle, data)

	def read_value(self):
		if not self.peripheral:
			print("Cannot write as no device to read from")
			return None
		else:
			print("Reading data")
			return self.characteristic.read()
	
	def disconnect(self):
		if not self.peripheral:
			print("No connected device so cannot disconnect")
		else:
			print("Disconnecting device")
			self.peripheral.disconnect()

	def discover(self, timeout):
		return devices = self.scanner.scan(timeout)

	def reconnect(self, chances):
		if self.peripheral is None:
			print("No device to reconnect with")
		else:
			self.peripheral.connect(self.target_address)

	def device_characteristics(self):
		# This function should return a dict with information about the device
		pass
	
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
				cli.write_value(bytearray(bluezutils.to_byte_array(mess_with_seq)))
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



if __name__ == '__main__':
	signal.signal(signal.SIGINT, sig_handler)
	print("Starting")
	address = 'DC:A6:32:26:CE:70'
	cli.prepare_device(address)
	devices = cli.discover(5.0)
	for dev in devices:
		print("Scan Data: {}".format(dev.getScanData()))
	cli.write_value(bytearray(bluezutils.to_byte_array("Hello")))
	print("Read Message: {}".format(cli.read_message()))
	# while True:
	#     print("READ: {}".format(bluezutils.from_byte_array(ch.read())))
