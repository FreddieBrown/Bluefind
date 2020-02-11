#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals

import sys
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import bluezutils, exceptions, bluefind

"""
This module is used to define an Agent which will control the security aspects of 
connecting to other devices. This will be registered and will be used to deal 
with incoming parining/connection requests for the device. 
"""
BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/test/agent"
capability = "NoInputNoOutput"

def trust_device(path, bus):
	"""
	This function will take the path of a device and a 
	connection to the System bus and will change the 
	`Trusted` property to be True, indicating that the 
	device should trust the device that connects to it.
	"""
	properties = dbus.Interface(bus.get_object(BUS_NAME, path), 
								"org.freedesktop.DBus.Properties")
	properties.Set("org.bluez.Device1", "Trusted", True)

class Agent(dbus.service.Object):
	"""
	This class defines an Agent which will be used to control the security side of 
	external devices connecting the device which it is running on. For this, it has to 
	implement a number of different functions which are part of the org.dbus.Agent1 
	interface. This version focusses on minimal security at this level and just allowing 
	devices to connect to it. This is part of the protocol defined in the project. 
	"""
	def __init__(self, bus, path):
		self.bus = bus
		self.path = path
		self.exit_on_release = True

	def set_eor(self, eor):
		"""
		This function sets the `Exit on Release` flag needed by the spec.
		"""
		self.exit_on_release = eor

	def connect_dev(self, path):
		"""
		This fucnction will be used to connect this device to another device 
		trying to connect to it.
		"""
		device = dbus.Interface(bus.get_object(BUS_NAME, path), "org.bluez.Device1")
		device.Connect()
		return device

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
	def Release(self):
		"""
		This function is called when the agent stops being used. 
		"""
		print("Release Agent")
		if self.exit_on_release:
			bluefind.mainloop.quit()
	
	@dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
	def RequestPinCode(self, device):
		"""
		This function will give a simple, easy pin code. The program doesn't 
		use pin codes and so this function is here to fulfill the spec of the 
		interface.
		"""
		print("RequestPinCode (%s)" % (device))
		trust_device(device, self.bus)
		return "0000"

	@dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
	def DisplayPinCode(self, device, pin):
		"""
		This function will print the pin code given to it by a device it 
		is trying to connect to.
		"""
		print("DisplayPinCode (%s, %s)" % (device, pincode))

	@dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
	def RequestPasskey(self, device):
		"""
		This function is used to take input for a passkey to 
		send back to a connecting device.
		"""
		print("RequestPasskey: (%s)" % (device))
		trust_device(device, self.bus)
		return dbus.UInt32(input("Enter Passkey: "))

	@dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
	def DisplayPasskey(self, device, passkey, entered):
		"""
		This will display the passkey given this method.
		"""
		print("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))

	@dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
	def RequestConfirmation(self, device, passkey):
		"""
		This function will confirm if the connecting device pass key is 
		correct. As we don't care about this, it is always approved and 
		trusted.
		"""
		print("RequestConfirmation (%s, %06d)" %(device, passkey))
		trust_device(device, self.bus)
		return

	@dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
	def RequestAuthorization(self, device):
		"""
		RequestAuthorization
		"""
		print("RequestAuthorization (%s)" %(device))
		return

	@dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
	def AuthorizeService(self, device, uuid):
		"""
		AuthorizeService
		"""
		print("AuthorizeService (%s, %s)" % (device, uuid))
		return

	@dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
	def Cancel(self):
		"""
		Cancel
		"""
		print("Cancel")


def register_agent(bus):
	"""
	This function will instantiate the Agent 
	object and will register it as the defined 
	Agent for the device to use. It will return 
	the interface for AgentManager1 so that it can be 
	used to unregister the Agent when the program ends.
	"""
	em_agent = Agent(bus, AGENT_PATH)
	em_agent.set_eor(False)
	obj = bus.get_object(BUS_NAME, "/org/bluez");
	agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
	agent_manager.RegisterAgent(AGENT_PATH, capability)
	print("Agent Registered")
	return agent_manager