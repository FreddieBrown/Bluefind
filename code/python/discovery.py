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
client_ty = None

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

def disco_start(bus, client_type):
	global client_ty
	client_ty = client_type

	adapter = bluezutils.find_adapter()
	adapter_props = dbus.Interface(bus.get_object("org.bluez", adapter.object_path),
					"org.freedesktop.DBus.Properties")
	bluezutils.get_mac_addr(bus)
	

	# Adds a callback to listen for signals from InterfacesAdded.
	# This will be activated when a new device is found
	bus.add_signal_receiver(interfaces_added,
			dbus_interface = "org.freedesktop.DBus.ObjectManager",
			signal_name = "InterfacesAdded")

	# This creates a callback when something changes about a 
	# device. This is usually the UUIDs or if it is connected.
	bus.add_signal_receiver(properties_changed,
			dbus_interface = "org.freedesktop.DBus.Properties",
			signal_name = "PropertiesChanged",
			arg0 = "org.bluez.Device1",
			path_keyword = "path")

	# Sets the Discoverable option to on, meaning devices can discover it
	if client_ty is "n":
		bluezutils.properties(adapter_props, "Discoverable", "on")
	else:
		bluezutils.properties(adapter_props, "Discoverable", "off")		    

	# Gets all objects for Bluez on Dbus. This looks for the 
	# Device1 interface so that it can be used later on
	om = dbus.Interface(bus.get_object("org.bluez", "/"),
				"org.freedesktop.DBus.ObjectManager")
	objects = om.GetManagedObjects()
	for path, interfaces in objects.items():
		if "org.bluez.Device1" in interfaces:
			devices[path] = interfaces["org.bluez.Device1"]

	# Builds the filter for the scan filter
	scan_filter = dict()
	
	if client_ty is "y":
		scan_filter.update({ "UUIDs": ['0000FFF0-0000-1000-8000-00805f9b34fb'] })

	# Sets the filter for device discovery
	adapter.SetDiscoveryFilter(scan_filter)
	adapter.StartDiscovery()
