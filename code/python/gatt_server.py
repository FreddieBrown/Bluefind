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

import bluezutils, exceptions

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'
GATT_PATH_BASE = '/org/bluez/example/service'

"""
Implements the org.bluez.GattApplication1 interface. This is 
a class which bundles together different services defined by 
the application. This class provides the base of the object 
path for the services and provides functionality for DBus 
applications to gain further information about services. 
"""
class Application(dbus.service.Object):
	"""
	org.bluez.GattApplication1 interface implementation
	"""
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
	def GetManagedObjects(self):
		response = {}
		print('GetManagedObjects')

		for service in self.services:
			response[service.get_path()] = service.get_properties()
			chrcs = service.get_characteristics()
			for chrc in chrcs:
				response[chrc.get_path()] = chrc.get_properties()
				descs = chrc.get_descriptors()
				for desc in descs:
					response[desc.get_path()] = desc.get_properties()

		return response
	

"""
Implementation of the org.bluez.GattService1 interface. This defines 
how a service works. It contains top-level information about it, such 
as UUID and its path. It has methods to return the properties of the 
service as well as its path and those of its characteristics, which can 
also be added to the service. 
"""
class Service(dbus.service.Object):
	"""
	org.bluez.GattService1 interface implementation
	"""

	def __init__(self, bus, index, uuid, primary):
		self.path = GATT_PATH_BASE + str(index)
		self.bus = bus
		self.uuid = uuid
		self.primary = primary
		self.characteristics = []
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		return {
				GATT_SERVICE_IFACE: {
						'UUID': self.uuid,
						'Primary': self.primary,
						'Characteristics': dbus.Array(
								self.get_characteristic_paths(),
								signature='o')
				}
		}

	def get_path(self):
		return dbus.ObjectPath(self.path)

	def add_characteristic(self, characteristic):
		self.characteristics.append(characteristic)

	def get_characteristic_paths(self):
		result = []
		for chrc in self.characteristics:
			result.append(chrc.get_path())
		return result

	def get_characteristics(self):
		return self.characteristics

	@dbus.service.method(DBUS_PROP_IFACE,
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		if interface != GATT_SERVICE_IFACE:
			raise exceptions.InvalidArgsException()

		return self.get_properties()[GATT_SERVICE_IFACE]
	
"""
Implementation of the org.bluez.GattCharacteristic1 interface. 
This interface contains the required methods to Read/Write properties 
for the service, as well as notify subscribed devices if properties about 
the device change. It contains a UUID for the specific characteristic, 
information about the service it belongs to, and the descriptors which make 
up the service. 
"""
class Characteristic(dbus.service.Object):
	"""
	org.bluez.GattCharacteristic1 interface implementation
	"""
	def __init__(self, bus, index, uuid, flags, service):
		self.path = service.path + '/char' + str(index)
		self.bus = bus
		self.uuid = uuid
		self.service = service
		self.flags = flags
		self.descriptors = []
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		return {
				GATT_CHRC_IFACE: {
						'Service': self.service.get_path(),
						'UUID': self.uuid,
						'Flags': self.flags,
						'Descriptors': dbus.Array(
								self.get_descriptor_paths(),
								signature='o')
				}
		}

	def get_path(self):
		return dbus.ObjectPath(self.path)

	def add_descriptor(self, descriptor):
		self.descriptors.append(descriptor)

	def get_descriptor_paths(self):
		result = []
		for desc in self.descriptors:
			result.append(desc.get_path())
		return result

	def get_descriptors(self):
		return self.descriptors

	@dbus.service.method(DBUS_PROP_IFACE,
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		if interface != GATT_CHRC_IFACE:
			raise exceptions.InvalidArgsException()

		return self.get_properties()[GATT_CHRC_IFACE]

	@dbus.service.method(GATT_CHRC_IFACE,
						in_signature='a{sv}',
						out_signature='ay')
	def ReadValue(self, options):
		print('Default ReadValue called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
	def WriteValue(self, value, options):
		print('Default WriteValue called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE)
	def StartNotify(self):
		print('Default StartNotify called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE)
	def StopNotify(self):
		print('Default StopNotify called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.signal(DBUS_PROP_IFACE,
						 signature='sa{sv}as')
	def PropertiesChanged(self, interface, changed, invalidated):
		pass

"""
Implementation of the org.bluez.GattDescriptor1 interface. Provides 
the required methods for Reading/Writing values to/from the decriptor 
as well as being able to get the properties which belong to the descriptor 
and the object path. 
"""
class Descriptor(dbus.service.Object):
	"""
	org.bluez.GattDescriptor1 interface implementation
	"""
	def __init__(self, bus, index, uuid, flags, chrc):
		self.path = chrc.path + '/desc' + str(index)
		self.bus = bus
		self.uuid = uuid
		self.flags = flags
		self.chrc = chrc
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		return {
				GATT_DESC_IFACE: {
						'Characteristic': self.chrc.get_path(),
						'UUID': self.uuid,
						'Flags': self.flags,
				}
		}

	def get_path(self):
		return dbus.ObjectPath(self.path)

	@dbus.service.method(DBUS_PROP_IFACE,
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		if interface != GATT_DESC_IFACE:
			raise exceptions.InvalidArgsException()

		return self.get_properties()[GATT_DESC_IFACE]

	@dbus.service.method(GATT_DESC_IFACE,
						in_signature='a{sv}',
						out_signature='ay')
	def ReadValue(self, options):
		print ('Default ReadValue called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
	def WriteValue(self, value, options):
		print('Default WriteValue called, returning error')
		raise exceptions.NotSupportedException()


"""
Implementation of the Service class for the purpose of providing 
information in an emergency situation. The service has a UUID which 
indentifies it as unique. It contains characteristics which provide the 
functionality of the service.  
"""
class EmergencyService(Service):
	service_UUID = '0000180d-0000-1000-8000-00805f9b34fb'
	def __init__(self, bus, index):
		Service.__init__(self, bus, index, self.service_UUID, True)
		self.add_characteristic(EmergencyCharacteristic(bus, 0, self))

"""
This characteristic belongs tot eh EmergencyService. It has its own 
unique UUID. It provides both reading and writing functions to send values 
to connected devices and receive them too. 
"""
class EmergencyCharacteristic(Characteristic):
	EM_CHAR_UUID = '00002a37-0000-1000-8000-00805f9b34fb'
	def __init__(self, bus, index, service):
		Characteristic.__init__(
			self, bus, index, 
			self.EM_CHAR_UUID, 
			['read', 'write'],
			service)
		self.value = None
	
	def WriteValue(self, value, options):
		print("Value being Written!")
		readVal = ""
		for char in options.items():
			readVal += str(int(char))+" "
		print("Options: "+readVal)
		print('EmergencyCharacteristic Write: ' + repr(value))
		self.value = value

	def ReadValue(self, options):
		print("Value being Read!")
		readVal = ""
		for char in options.items():
			readVal += str(int(char))+" "
		print("Options: "+readVal)
		print('EmergencyCharacteristic Read: ' + repr(self.value))
		return self.value
	
