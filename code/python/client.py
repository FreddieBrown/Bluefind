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

	def __init__(self, location, device_address):
		self.device_address = device_address
		self.location = location
		self.requester = None
		self.target_address = None
		self.discovery = DiscoveryService("hci0")

	def prepare_device(self, target_address, connect=True):
		self.requester = GATTRequester(target_address, connect)
		self.target_address = target_address
		data = self.read_value()
		return data

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
				if not self.is_connected():
					print("Lost connection, reconnecting")
					self.reconnect(3)

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
			if not self.is_connected():
				print("Lost connection, reconnecting")
				self.reconnect(3)
		print("Characteristics for {}: {}".format(self.target_address, response.received()))
		return response.received()
	def update_location(self, location):
		self.location = location


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
	cli = Client("52.281799, -1.532315", bluezutils.get_mac_addr(dbus.SystemBus()))
	message = bluezutils.build_message([cli.location], [cli.device_address])

	devices = cli.discover(5)
	print("Devices: {}".format(devices))
	for address, name in list(devices.items()):
		print("name: {}, address: {}".format(name, address))
		if "EmergencyAdvertisement" in name:
			cli.prepare_device(address)
			chrcs = cli.device_characteristics()
			for dev in chrcs:
				# Go through the dict and inspect the UUIDs
				print("CHRC_UUID: {}, DEV_UUID: {}, MATCH: {}".format(dev['uuid'].lower(), cli.RW_UUID.lower(), dev['uuid'].lower() == cli.RW_UUID.lower()))
				if dev['uuid'].lower() == cli.RW_UUID.lower():
					# If one of them is the same as the emergency UUID, allow it to talk to it
					handle = int(dev['handle'])
					cli.write_value(handle, str(bytearray([2])))
					while cli.is_connected():
						# Do stuff with other device e.g write to it and read from it
						data = cli.read_value()
						print("Data from device: {}".format(bluezutils.from_byte_array(data)))
						time.sleep(0.1)
			# Otherwise, disconnect from device
			cli.disconnect()
	print("Done")
	