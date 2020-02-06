from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import re
import sys
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import array
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from gattlib import GATTRequester, GATTResponse, DiscoveryService
import time

import bluezutils, exceptions


class Client():
	SERVICE_UUID =  '0000FFF0-0000-1000-8000-00805f9b34fb'
	RW_UUID = '0000FFF1-0000-1000-8000-00805f9b34fb'

	def __init__(self):
		self.requester = None
		self.address = None
		self.discovery = DiscoveryService("hci0")

	def prepare_device(self, address, connect=True):
		self.requester = GATTRequester(address)
		# self.requester.connect(True)
		self.address = address
		
		data = self.read_value()

		return data

	def write_value(self, handle, data):
		if not self.requester:
			print("Cannot write as no device to send to")
		else:
				self.requester.write_cmd(i, data)

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
				if not self.is_connected():
					print("Lost connection, reconnecting")
					self.reconnect()

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
		response = GATTResponse()
		self.requester.discover_characteristics_async(response)
		while not response.received():
			time.sleep(0.1)
		print("Characteristics for {}: {}".format(self.address, response.received()))
		return response.received()


"""

1. Start to Discover devices and information about them
2. Get the devices which utilise the EmergencyService
3. Connect to that device (if it wasn't the last seen device (only ok if 1 device visible) )
4. Read data from the connected device
5. Write data to connected device
6. Split up and save message
7. Set device to last seen device
8. Disconnect device
9. Go back to step 2

"""

if __name__ == '__main__':
	print("Starting")
	cli = Client()
	bus = dbus.SystemBus()
	dev_addr = bluezutils.get_mac_addr(bus)
	coord = "52.281799, -1.532315"
	message = bluezutils.build_message([coord], [dev_addr])

	devices = cli.discover(5)
	print("Devices: {}".format(devices))
	for address, name in list(devices.items()):
		print("name: {}, address: {}".format(name, address))
		if name.strip(' ') is not '':
			cli.prepare_device(address)
			chrcs = cli.device_characteristics()
			cli.write_value(35, str(message))
			while cli.is_connected():
				# Do stuff with other device e.g write to it and read from it
				data = cli.read_value()
				print("Data from device: {}".format(bluezutils.from_byte_array(data)))
				time.sleep(0.1)
			cli.disconnect()


	# print("Connecting to device")
	# data = cli.prepare_device("DC:A6:32:26:CE:70")
	# print("Data from device: {}".format(data))
	

	
	cli.disconnect()

	print("Done")
	