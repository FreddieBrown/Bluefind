#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser
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
device_obj = None
dev_path = None

class Agent(dbus.service.Object):
	def __init__(self, bus, path):
		self.bus = bus
		self.path = path
		self.exit_on_release = True

	def set_eor(self, eor):
		self.exit_on_release = eor
	
	def trust_device(self, path):
	properties = dbus.Interface(bus.get_object(BUS_NAME, path), 
								"org.freedesktop.DBus.Properties")
	properties.Set("org.bluez.Device1", "Trusted", True)

	def connect_dev(self, path):
		device = dbus.Interface(bus.get_object(BUS_NAME, path), "org.bluez.Device1")
		device.Connect()
		return device

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
	def Release(self):
		print("Release Agent")
		if self.exit_on_release:
			bluefind.mainloop.quit()
	
	@dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
	def RequestPinCode(self, device):
		print("RequestPinCode (%s)" % (device))
		self.trust_device(device)
		return input("Enter Pin Code: ")

	@dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
	def DisplayPinCode(self, device, pin):
		print("DisplayPinCode (%s, %s)" % (device, pincode))

	@dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
	def RequestPasskey(self, device):
		print("RequestPasskey: (%s)", % (device))
		self.trust_device(device)
		return dbus.UInt32(input("Enter Passkey: "))

	@dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
	def DisplayPasskey(self, device, passkey, entered):
		print("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))

	@dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
	def RequestConfirmation(self, device, passkey):
		print("RequestConfirmation (%s, %06d)", %(device, passkey))
		if input("Confirm Passkey? (yes/no): ") is "yes":
			self.trust_device(device)
			return
		print("Rejected")
		raise exceptions.RejectedException("Passkey doesn't match")

	@dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
	def RequestAuthorization(self, device):
		print("RequestAuthorization (%s)", %(device))
		if input("Authorize? (yes/no): ") is "yes":
			return
		raise exceptions.RejectedException("Device not authorized, pairing rejected")

	@dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
	def AuthorizeService(self, device, uuid):
		print("AuthorizeService (%s, %s)", % (device, uuid))
		if input("Authorize Connection? (yes/no): ") is "yes":
			return
		raise exceptions.RejectedException("Connection not authorized")

	@dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
	def Cancel(self):
		print("Cancel")