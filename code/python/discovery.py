from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import re
import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import bluezutils
import bluefind
import agent

devices = {}
dev_path = None
device_obj = None

def pair_reply():
	print("PAIRING SUCCESS")
	agent.trust_device(dev_path, bluefind.bus)
	dev = dbus.Interface(bus.get_object("org.bluez", dev_path),
						"org.bluez.Device1")
	dev.Connect()


def pair_error():
	print("PAIRING ERROR")
	err_name = error.get_dbus_name()
	if err_name == "org.freedesktop.DBus.Error.NoReply" and device_obj:
		print("Timed out. Cancelling pairing")
		device_obj.CancelPairing()
	else:
		print("Creating device failed: %s" % (error))

def print_info(address, properties):
	"""
	Passed a device address and the properties of the 
	device. Contains information about connecting to 
	devices and UUIDs
	"""
	print("[ " + address + " ]")

	for key in properties.keys():
		value = properties[key]
		if type(value) == dbus.String:
			value = str(value)
		if key == "Class":
			print("    %s = 0x%06x" % (key, value))
		elif key == "UUIDs":
			for uuid_string in value:
				print("    %s = %s" % ("UUID", str(uuid_string)))
		elif key == "ManufacturerData":
			for key, arr in value.items():
				print("    %s = %s" % ("ManufacturerData Key", str(key)))
				ManuData = "    ManufacturerData Value = "
				for mandata in arr:
					ManuData += str(int(mandata))+" "
				print(ManuData)
		else:
			print("    %s = %s" % (key, value))

	print()

	properties["Logged"] = True

def interfaces_added(path, interfaces):
	"""
	This function will be called when a new interface is added 
	to the org.bluez object on DBus. It will extract the relevant 
	information and will try and connect to devices if it is a client.
	It will also print any information about the interfaces it encounters.
	"""
	print("New Device!")
	print(list(interfaces))
	if "org.bluez.Device1" not in list(interfaces):
		return
		
	properties = interfaces["org.bluez.Device1"]
	if not properties:
		return

	if path in devices:
		dev = devices[path]
		devices[path].update(properties.items())
	else:
		devices[path] = properties

	if "Address" in devices[path]:
		address = properties["Address"]
	else:
		address = "<unknown>"

	print("Thinking about pairing, is device Client?: "+bluefind.client_ty)
	if bluefind.client_ty is "y": 
		print("Trying to pair with %s"%(str(address)))
		device = bluezutils.find_device(address)
		dev_path = device.object_path
		device.Pair(reply_handler=pair_reply, error_handler=pair_error,
										timeout=60000)
		device_obj = device

	print_info(address, devices[path])

def properties_changed(interface, changed, invalidated, path):
	if interface != "org.bluez.Device1":
		return

	if path in devices:
		dev = devices[path]
		devices[path].update(changed.items())
	else:
		devices[path] = changed

	if "Address" in devices[path]:
		address = devices[path]["Address"]
	else:
		address = "<unknown>"
		print_info(address, devices[path])
