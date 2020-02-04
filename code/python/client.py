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
from gattlib import GATTRequester, GATTResponse

import bluezutils, exceptions


class Client():
	SERVICE_UUID =  '0000FFF0-0000-1000-8000-00805f9b34fb'
	RW_UUID = '0000FFF1-0000-1000-8000-00805f9b34fb'

	def __init__(self):
		self.requester = None
		self.address = None

	def connect_to_device(self, address):
		self.requester = GATTRequester(address)
		# self.requester.connect(True)
		self.address = address
		
		data = self.read_value()

		return data

	def write_value(self, data):
		if not self.requester:
			print("Cannot write as no device to send to")
		else:
			for i in range(0, 256):
				self.requester.write_cmd(i, data)

	def read_value(self):
		if not self.requester:
			print("Cannot write as no device to read from")
			return None
		else:
			response = GATTResponse()

			requester.read_by_uuid_async(self.RW_UUID, response)
			while not response.received():
				time.sleep(0.1)
			
			return response.received()[0]
	
	def disconnect(self):
		if not self.requester:
			print("No connected device so cannot disconnect")
		else:
			print("Disconnecting device")
			self.requester.disconnect()



