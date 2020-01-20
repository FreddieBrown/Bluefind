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
from random import randint

import bluezutils

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'
GATT_PATH_BASE = '/org/bluez/example/service'

class InvalidArgsException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.bluez.Error.NotSupported'

class NotPermittedException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.bluez.Error.NotPermitted'

class InvalidValueLengthException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.bluez.Error.InvalidValueLength'

class FailedException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.bluez.Error.Failed'

class Application(dbus.service.Object):
	def __init__(self, bus):
		self.path = '/'
		self.services = []
		dbus.service.Object.__init__(self, bus, self.path)
		self.add_service(EmergencyService(bus, 0))
	
	def get_path(self):
		return dbus.ObjectPath(self.path)
	
	def add_service(self, service):
		self.services.append(service)
	
	@dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
	def getManagedObjects(self):
		objs = {}
		for service in self.services:
			objs[service.get_path()] = service.get_properties()
			chars = service.get_characteristics()
			for char in chars:
				objs[char.get_path()] = char.get_properties()
				descs = char.get_descriptions()
				for desc in descs:
					objs[desc.get_path()] = desc.get_properties()
		
		return objs
	

class Service(dbus.service.Object):
	def __init__(self, bus, index, uuid, primary):
		self.bus = bus
		# Maybe change this to give a better name to the service on DBus
		self.path = GATT_PATH_BASE + str(index)
		self.uuid = uuid
		self.primary = primary
		self.characteristics = []
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		return {
			GATT_SERVICE_IFACE : {
				'UUID' : self.uuid,
				'Primary' : self.primary
				'Characteristics' : dbus.Array(self.get_characteristic_paths(), signature='o')
			}
		}

	def get_path(self):
		return dbus.ObjectPath(self.path)
	
	def add_characteristic(self, char):
		self.characteristics.append(char)
	
	def get_characteristic_paths(self):
		result = []
		for char in self.characteristics:
			result.append(char.get_path())
		return result
	
	def get_characteristics(self):
		return self.characteristics

	@dbus.service.method(DBUS_PROP_IFACE,
						in_signature = 's',
						out_signature = 'a{sv}')
	def GetAll(self, interface):
		if interface != GATT_SERVICE_IFACE:
			raise InvalidArgsException()

		return self.get_properties()[GATT_SERVICE_IFACE]
	

class Characteristic(dbus.service.Object):
	def __init__(self, bus, index, uuid, flag, service):
		self.bus = bus
		self.path = service.path + '/char'+str(index)
		self.descriptors = []
		self.flag = flag
		self.service = service
		self.uuid = uuid
		dbus.service.Object.__uuid__(self, bus, self.path)
	
	def get_properties(self):
		return {
			GATT_CHRC_IFACE : {
				'Service': self.service.get_path(),
				'UUID' : self.uuid,
				'Flags' : self.flag,
				'Descriptors' : dbus.Array(self.descriptor_paths(), signature='o')
			}
		}
	
	def get_path(self):
		return dbus.ObjectPath(self.path)
	
	def add_descriptor(self, desc):
		self.descriptors.append(desc)
	
	def get_descriptor_paths(self):
		response = []
		for desc in self.descriptors:
			response.append(desc.get_path())
		return response

	def get_descriptors(self):
		return self.descriptors
	
	@dbus.service.method(DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
	def GetAll(self, interface):
		if interface != GATT_CHRC_IFACE:
			raise InvalidArgsException()

		return self.get_properties[GATT_CHRC_IFACE]

	@dbus.service.method(GATT_CHRC_IFACE, in_signature='a{sv}', out_signature='ay')
	def ReadValue(self, options):
		print("ReadValue: Reading value...")
		raise NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
	def WriteValue(self, options):
		print("WriteValue: Writing value...")
		raise NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE)
	def StartNotify(self):
		print("StartNotify: Starting to Notify...")
		raise NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE)
	def StopNotify(self):
		print("StopNotify: Stopping Notifying...")
		raise NotSupportedException()

	@dbus.service.signal(DBUS_PROP_IFACE, signature='sa{sv}as')
	def PropertiesChanges(self):
		print("PropertiesChanged: Propety Changed...")
	
class Descriptor(dbus.service.Object):
	def __init__(self, bus, index, uuid, flag, characteristic):
		self.bus = bus
		self.uuid = uuid
		self.characteristic = characteristic
		self.flag = flag
		self.path = self.characteristic.get_path()+'/desc'+str(index)
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		return {
			GATT_DESC_IFACE : {
				'Characteristic' : self.characteristic.get_path(),
				'UUID' : self.uuid,
				'Flags' : self.flag
			}
		}
		
	def get_path(self):
		return dbus.ObjectPath(self.path)
	
	@dbus.service.method(DBUS_PROP_IFACE, in_signature='s', out_signature='a{sv}')
	def GetAll(self, interface):
		if interface != GATT_DESC_IFACE:
			raise InvalidArgsException()
		return self.get_properties()[GATT_DESC_IFACE]

	@dbus.service.method(GATT_DESC_IFACE, in_signature='a{sv}', out_signature='ay')
	def ReadValue(self, options):
		print("ReadValue: Read called...")
		raise NotSupportedException()

	@dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
	def WriteValue(self, value, options):
		print("WriteValue: Writing value...")
		raise NotSupportedException()

# Use the above classes to implement functionality for EmergencyService


