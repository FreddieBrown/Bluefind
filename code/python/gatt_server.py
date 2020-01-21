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
	

"""
Implementation of the org.bluez.GattService1 interface. This defines 
how a service works. It contains top-level information about it, such 
as UUID and its path. It has methods to return the properties of the 
service as well as its path and those of its characteristics, which can 
also be added to the service. 
"""
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
			raise exceptions.InvalidArgsException()

		return self.get_properties[GATT_CHRC_IFACE]

	@dbus.service.method(GATT_CHRC_IFACE, in_signature='a{sv}', out_signature='ay')
	def ReadValue(self, options):
		print("ReadValue: Reading value...")
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
	def WriteValue(self, value, options):
		print("WriteValue: Writing value...")
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE)
	def StartNotify(self):
		print("StartNotify: Starting to Notify...")
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE)
	def StopNotify(self):
		print("StopNotify: Stopping Notifying...")
		raise exceptions.NotSupportedException()

	@dbus.service.signal(DBUS_PROP_IFACE, signature='sa{sv}as')
	def PropertiesChanges(self):
		print("PropertiesChanged: Propety Changed...")

"""
Implementation of the org.bluez.GattDescriptor1 interface. Provides 
the required methods for Reading/Writing values to/from the decriptor 
as well as being able to get the properties which belong to the descriptor 
and the object path. 
"""
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
			raise exceptions.InvalidArgsException()
		return self.get_properties()[GATT_DESC_IFACE]

	@dbus.service.method(GATT_DESC_IFACE, in_signature='a{sv}', out_signature='ay')
	def ReadValue(self, options):
		print("ReadValue: Read called...")
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
	def WriteValue(self, value, options):
		print("WriteValue: Writing value...")
		raise exceptions.NotSupportedException()


"""
Implementation of the Service class for the purpose of providing 
information in an emergency situation. The service has a UUID which 
indentifies it as unique. It contains characteristics which provide the 
functionality of the service.  
"""
class EmergencyService(Service):
	service_UUID = "b0d4d4bf-c032-4875-97d2-e7a67b5aa35b"
	def __init__(self, bus, index):
		Service.__init__(self, bus, index, self.service_UUID, True)
		self.add_characteristic(EmergencyCharacteristic(bus, 0, self))

"""
This characteristic belongs tot eh EmergencyService. It has its own 
unique UUID. It provides both reading and writing functions to send values 
to connected devices and receive them too. 
"""
class EmergencyCharacteristic(Characteristic):
	EM_CHAR_UUID = "f473d81b-acb1-4801-9cb7-92495f8ddea8"
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
	

	
