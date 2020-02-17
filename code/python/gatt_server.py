from __future__ import absolute_import, print_function, unicode_literals

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
import datetime
import bluezutils, exceptions
from db import Database

BLUEZ_SERVICE_NAME = 'org.bluez'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
DBUS_OM_IFACE =      'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE =    'org.freedesktop.DBus.Properties'

GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE =    'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE =    'org.bluez.GattDescriptor1'
GATT_PATH_BASE = '/org/bluez/example/service'
current_client = ''



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
		"""
		Function to return the path of the object for DBUS
		"""
		return dbus.ObjectPath(self.path)

	def add_service(self, service):
		"""
		Function to add a service to the application. 
		Adds an association between the services and application. 
		Means they are contained within the application.
		"""
		self.services.append(service)

	@dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
	def GetManagedObjects(self):
		"""
		Function to return a dictionary of the properties of the 
		services that an application offers and the characteristics and 
		descriptors withtin them.
		"""
		response = {}
		print('Getting Objects')

		for service in self.services:
			response[service.get_path()] = service.get_properties()
			chrcs = service.get_characteristics()
			for char in chrcs:
				response[char.get_path()] = char.get_properties()
				descs = char.get_descriptors()
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
		"""
		Returns an object containing information 
		about the service.
		"""
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
		"""
		Function to return the path of the object for DBUS
		"""
		return dbus.ObjectPath(self.path)

	def add_characteristic(self, characteristic):
		"""
		Function to add a characteristic to a service. This makes
		the characteristic part of the service.
		"""
		self.characteristics.append(characteristic)

	def get_characteristic_paths(self):
		"""
		Function gets the object paths of each characteristic 
		which belongs to it and returns them as a list.
		"""
		result = []
		for chrc in self.characteristics:
			result.append(chrc.get_path())
		return result

	def get_characteristics(self):
		"""
		Function to return list of characteristics
		"""
		return self.characteristics

	@dbus.service.method(DBUS_PROP_IFACE,
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		"""
		Function to return the properties about the 
		service associated with the GATT service interface.
		"""
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
		"""
		Function to return information about the 
		characteristic.
		"""
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
		"""
		Function to return the path of the object for DBUS
		"""
		return dbus.ObjectPath(self.path)

	def add_descriptor(self, descriptor):
		"""
		Function to add a descriptor to the characteristic
		"""
		self.descriptors.append(descriptor)

	def get_descriptor_paths(self):
		"""
		Function to return a list of the object paths 
		of descriptors associated with the characteristic
		"""
		result = []
		for desc in self.descriptors:
			result.append(desc.get_path())
		return result

	def get_descriptors(self):
		"""
		Function that returns the descriptors associated 
		with the characteristic
		"""
		return self.descriptors

	@dbus.service.method(DBUS_PROP_IFACE,
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		"""
		Function to return the properties about the characteristic 
		associated with the GATT characteristic interface.
		"""
		if interface != GATT_CHRC_IFACE:
			raise exceptions.InvalidArgsException()

		return self.get_properties()[GATT_CHRC_IFACE]

	@dbus.service.method(GATT_CHRC_IFACE,
						in_signature='a{sv}',
						out_signature='ay')
	def ReadValue(self, options):
		"""
		Function which can be called by external connected 
		devices to read a certain value from the device.
		"""
		print('Default ReadValue called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE, in_signature='aya{sv}')
	def WriteValue(self, value, options):
		"""
		Function which can be used by external connected devices 
		to send data to the server.
		"""
		print('Default WriteValue called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE)
	def StartNotify(self):
		"""
		Function to tell the server that a client wants to 
		be notified of any changes to the value of the 
		characteristic.
		"""
		print('Default StartNotify called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_CHRC_IFACE)
	def StopNotify(self):
		"""
		Function to tell the server that a client wants to 
		be not notified of any changes to the value of the 
		characteristic any more.
		"""
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
		"""
		Function to return information about the 
		descriptor and the characteristic it belongs to.
		"""
		return {
				GATT_DESC_IFACE: {
						'Characteristic': self.chrc.get_path(),
						'UUID': self.uuid,
						'Flags': self.flags,
				}
		}

	def get_path(self):
		"""
		Function to return the path of the object for DBUS
		"""
		return dbus.ObjectPath(self.path)

	@dbus.service.method(DBUS_PROP_IFACE,
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		"""
		Function to return the properties about the descriptor 
		associated with the GATT descriptor interface.
		"""
		if interface != GATT_DESC_IFACE:
			raise exceptions.InvalidArgsException()

		return self.get_properties()[GATT_DESC_IFACE]

	@dbus.service.method(GATT_DESC_IFACE,
						in_signature='a{sv}',
						out_signature='ay')
	def ReadValue(self, options):
		"""
		Function which can be called by external connected 
		devices to read a certain value from the device.
		"""
		print ('Default ReadValue called, returning error')
		raise exceptions.NotSupportedException()

	@dbus.service.method(GATT_DESC_IFACE, in_signature='aya{sv}')
	def WriteValue(self, value, options):
		"""
		Function which can be used by external connected devices 
		to send data to the server.
		"""
		print('Default WriteValue called, returning error')
		raise exceptions.NotSupportedException()


"""
Implementation of the Service class for the purpose of providing 
information in an emergency situation. The service has a UUID which 
indentifies it as unique. It contains characteristics which provide the 
functionality of the service.  
"""
class EmergencyService(Service):
	# FFF0
	service_UUID = '0000FFF0-0000-1000-8000-00805f9b34fb'
	def __init__(self, bus, index):
		Service.__init__(self, bus, index, self.service_UUID, True)
		self.add_characteristic(EmergencyCharacteristic(bus, 0, self))

"""
This characteristic belongs to the EmergencyService. It has its own 
unique UUID. It provides both reading and writing functions to send values 
to connected devices and receive them too. 
"""
class EmergencyCharacteristic(Characteristic):
	EM_CHAR_UUID = '0000FFF1-0000-1000-8000-00805f9b34fb'
	def __init__(self, bus, index, service):
		Characteristic.__init__(
			self, bus, index, 
			self.EM_CHAR_UUID, 
			['read', 'write'],
			service)
		self.value = None
		self.address = bluezutils.get_mac_addr(bus)
		self.location = '52.281807, -1.532221'
		self.read_states = {}
		self.write_states = {}
		self.db = Database('find.db')
		self.keypair = bluezutils.generate_RSA_keypair()
		self.send_key = False
		self.encrypt = False
		self.client_key = None
		self.emer_services = False
	
	def WriteValue(self, value, options):
		"""
		Function to send data to the server. This is an implementation of 
		the standard WriteValue function. In this, the MAC address of the 
		connecting device is found and the received message is broken down 
		into its sequence number and message. If that device has already 
		written messages to the server and the message is the next expected 
		message, then it is added to the message buffer associated with that 
		connected device. If that is the last part of the message, connect the 
		message parts and save it to the database. If it is the first fragment of 
		the message, create a message buffer for the device. Otherwise, do nothing.
		"""
		dev = bluezutils.dbus_to_MAC(options['device'])
		sequence_num, message = bluezutils.get_sequence_number(bluezutils.from_byte_array(value))
		print("Value being Written!: "+message)
		print("Sequence Number: "+sequence_num)
		if (dev in self.write_states.keys()) and  int(sequence_num) is len(self.write_states[dev]):
			self.write_states[dev].append(message)
			if str(chr(5)) == message:
				# If it is in message, join up message
				print("End of message")
				full_message = ''.join(self.write_states[dev])
				print("Message Written To Server: {}".format(full_message))
				# break down message
				if self.encrypt:
					print("Decrypting message")
					try:
						full_message = bluezutils.decrypt_message(self.keypair['private'], bluezutils.utf_to_byte_string(full_message))
					except Exception as e:
						print("Exception: {}".format(e))
				message_parts = bluezutils.break_down_message(full_message)
				print("Keys in Message: {}".format(message_parts.keys()))
				if "3" in message_parts.keys():
					self.client_key = message_parts["3"][0]
					print("Recevied Key: {}".format(self.client_key))
					self.send_key = True
				elif "4" in message_parts.keys():
					print("Recevied ACK")
					self.encrypt = True
				elif "5" in message_parts.keys():
					# This part should set a flag to say it is talking to emergency node
					self.emer_services = True
				else:
					# Go through message, build tuples with datetime and commit to db
					bluezutils.add_to_db(self.db, message_parts)
					self.encrypt = False
				del self.write_states[dev] 
			return sequence_num
		elif int(sequence_num) is 0:
			if str(chr(5)) == message:
				print(message)
			else:
				self.write_states[dev] = [message]
			return sequence_num
		# Take value are pass into method to split and store data
		else:
			return len(self.write_states[dev])-1
		


	def ReadValue(self, options):
		"""
		This function allows a connected device to read information 
		from the server. If the connected device is the same as the 
		last one, the server will check for the next message fragement
		to send and will send it. Otherwise, the device is treated as a 
		new device and the message is generated and the first fragment is 
		sent to the connected device. If it reaches the end of the message 
		to send, it will forget about the connected device and will treat it 
		as a new device the next time it reads from the server.
		"""
		# Create method to get device address from options['device']
		global current_client
		dev = bluezutils.dbus_to_MAC(options['device'])
		if (current_client == dev) and (dev in self.read_states.keys()):
			# Same device connected
			dev_state = self.read_states[dev]
			position = dev_state['position']
			message_packets = dev_state['message']
			packet = str(position)+"\x01"+message_packets[position]
			dev_state['position']+=1
			self.read_states[dev] = dev_state
		else: 
			# New device or device which has already received whole packet
			current_client = dev
			print("New client: {}".format(current_client))
			if self.send_key:
				# Need to send public key
				print("Sending public key")
				message = bluezutils.build_generic_message({3:[self.keypair['public']]})
				self.send_key = False
			elif self.emer_services:
				print("Doing emergency services stuff")
				db_data = self.db.select_em(50)
				db_data[0].append(self.location)
				db_data[1].append(self.address)
				db_data[2].append(datetime.datetime.now())
				message = bluezutils.build_generic_message({
					1: db_data[0],
					2: db_data[1],
					6: db_data[2],
				})
				self.emer_services = False
			else:
				if self.encrypt:
					select_amount = 3
				else:
					select_amount = 50
				db_data = self.db.select(select_amount)
				db_data[0].append(self.location)
				db_data[1].append(self.address)
				message = bluezutils.build_message(db_data[0], db_data[1], [current_client.upper()])
				if self.encrypt:
					print("Encrypting message")
					message = bluezutils.bytestring_to_uf8(bluezutils.encrypt_message(self.client_key, message))
					print("Message: {}".format(bluezutils.utf_to_value_list(message)))
					print("Size of enc message: {}".format(len(bluezutils.utf_to_value_list(message))))
			message_packets = bluezutils.split_message(message)
			print("Split message: {}".format(message_packets))
			dev_state = dict()
			dev_state['message'] = message_packets
			dev_state['position'] = 1
			self.read_states[dev] = dev_state
			# Gets to this point then just stops working when working with 
			# encrypted message
			packet = str(0)+"\x01"+message_packets[0]
			print("Packet: {}".format(packet))
		
		if self.read_states[dev]['position'] == len(self.read_states[dev]['message']):
			print("Sent whole message to {}".format(dev))
			del self.read_states[dev]
		print("Packet being sent: {}".format(packet))
		return bluezutils.to_byte_array(packet)

def app_register_cb():
	"""
	Callback for when GATT application is registered
	"""
	print("GATT Application registered!")

def app_register_error_cb(error):
	"""
	Callback for when GATT application fails to be registered
	"""
	print('GATT Application not registered: ' + str(error))

def GATTStart(bus):
	"""
	Function to register the GATT application with the GATT 
	manager. Called when the program wants to utilise this 
	functionality.
	"""
	adapter = bluezutils.find_adapter_path(bus, GATT_MANAGER_IFACE)
	if not adapter:
		print("No adapter with interface: "+GATT_MANAGER_IFACE)
	
	service_manager = dbus.Interface(
			bus.get_object(BLUEZ_SERVICE_NAME, adapter),
			GATT_MANAGER_IFACE)
	
	app = Application(bus)

	print('Registering GATT application...')
	print("Debugging: "+app.get_path())
	service_manager.RegisterApplication(app.get_path(), {},
									reply_handler=app_register_cb,
									error_handler=app_register_error_cb)