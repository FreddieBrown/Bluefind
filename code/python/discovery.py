from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import re
import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import bluezutils

devices = {}

def print_info(address, properties):
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
        elif key = "ManufacturerData":
            for key, arr in value.items():
                print("    %s = %s" % ("ManufacturerData Key", str(key)))
                ManuData = "    ManufacturerData Value = "
                for mandata in arr:
                    ManuData += str(mandata+" ")
                print(ManuData)

		else:
			print("    %s = %s" % (key, value))

	print()

	properties["Logged"] = True

def interfaces_added(path, interfaces):
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
