from __future__ import absolute_import, print_function, unicode_literals

import re
import sys
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import time
import threading
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import bluezutils, exceptions

"""
Module which deals with advertising services which the application offers.
"""

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'
AD_PATH_BASE = '/org/bluez/bluefind/advertisement'

"""
This class defines the basics for advertising services to 
other BLE devices. It holds all the properties of the device 
and services which are provided by the device. From this, it 
implements a number of standard methods for the Advertising class. 
This implements the org.bluez.LEAdvertisement1 interface.
"""
class Advertisement(dbus.service.Object):

	def __init__(self, bus, index, adtype):
		self.path = AD_PATH_BASE + str(index)
		self.bus = bus
		self.adtype = adtype
		self.service_uuids = None
		self.manufacturer_data = None
		self.solicit_uuids = None
		self.service_data = None
		self.local_name = None
		self.include_tx_power = None
		self.data = None
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		"""
		This method will collect the properties of the advert that are set, 
		such as the type of advert, manufucturer data and local name, and will
		return this as a dictionary of items which are set.
		"""
		properties = {}
		properties["Type"] = self.adtype
		if self.service_uuids is not None:
			properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature='s')

		if self.manufacturer_data is not None:
			properties["ManufacturerData"] = dbus.Dictionary(self.manufacturer_data, signature='qv')

		if self.solicit_uuids is not None:
			properties["SolicitUUIDs"] = dbus.Array(self.solicit_uuids, signature='s')

		if self.service_data is not None:
			properties["ServiceData"] = dbus.Dictionary(self.service_data, signature='sv')

		if self.local_name is not None:
			properties["LocalName"] = dbus.String(self.local_name)

		if self.include_tx_power is not None:
			properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)

		if self.data is not None:
			properties['Data'] = dbus.Dictionary(self.data, signature='yv')

		return {LE_ADVERTISEMENT_IFACE: properties}

	def get_path(self):
		"""
		This function will return the path to the advert object.
		"""
		return dbus.ObjectPath(self.path)

	def add_service_uuid(self, uuid):
		"""
		Function to add a service UUID to the list of service UUIDs
		"""
		if self.service_uuids is None:
			self.service_uuids = []
		self.service_uuids.append(uuid)

	def add_solicit_uuid(self, uuid):
		"""
		Function to add a solicit UUID to the list of solicit UUIDs
		"""
		if self.solicit_uuids is None:
			self.solicit_uuids = []
		self.solicit_uuids.append(uuid)

	def add_local_name(self, local_name):
		"""
		Function to give a local name to the advert
		"""
		self.local_name = dbus.String(local_name)

	def tx_power(self, include):
		"""
		Function to set whether the advertisement should include the 
		transmission power of the device.
		"""
		self.include_tx_power = dbus.Boolean(include)

	def add_manufacturer_data(self, mancode, data):
		"""
		Function to set the manufucturer data, part of the advertisement
		"""
		if self.manufacturer_data is None:
			self.manufacturer_data = dbus.Dictionary({}, signature='qv')
		self.manufacturer_data[mancode] = dbus.Array(data, signature='y')

	def add_service_data(self, uuid, data):
		"""
		Function to set the service data, part of the advertisement
		"""
		if self.service_data is None:
			self.service_data = dbus.Dictionary({}, signature='sv')
		self.service_data[uuid] = dbus.Array(data, signature='y')

	def add_data(self, adtype, data):
		"""
		Function to set other data, part of the advertisement
		"""
		if self.data is None:
			self.data = dbus.Dictionary({}, signature='yv')
		self.data[adtype] = dbus.Array(data, signature='y')

	@dbus.service.method(DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
	def GetAll(self, interface):
		"""
		Function to return the properties of the Advertisement. This is mainly 
		used by DBUS so that it knows what the interface of the process is.
		"""
		print('GetAll')
		if interface != LE_ADVERTISEMENT_IFACE:
			raise exceptions.InvalidArgsException()
		print('Returning Properties of Advertisement')
		return self.get_properties()[LE_ADVERTISEMENT_IFACE]

	@dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature='', out_signature='')
	def Release(self):
		"""
		Function that is called when the advertisement is unregistered.
		"""
		print("Advertisement Unregistered: %s" % (self.path))

"""
This class takes the base advertising class and implements 
more specific behaviours. These include specifying services 
offered by the server, as well as service and manufacturer data. 
This is an implementation of the Advertisement class that is defined 
above.
"""
class EmergencyAdvertisement(Advertisement):
	def __init__(self, bus, index):
		Advertisement.__init__(self, bus, index, 'peripheral')
		# Change this when UUID is finalised
		self.add_service_uuid('FFF0')
		self.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03, 0x04])
		self.add_service_data('9999', [0x00, 0x01, 0x02, 0x03, 0x04])
		self.add_local_name('EmergencyAdvertisement')
		self.include_tx_power = True
		self.add_data(0x26, [0x01, 0x01, 0x00])

def register_ad_cb():
	"""
	Callback to be called whent the advertisement is registered.
	"""
	print('Advertisement registered')

def register_ad_error_cb(error):
	"""
	Callback to be called when there is an error in registering 
	advertisements.
	"""
	print('Failed to register advertisement: ' + str(error))






