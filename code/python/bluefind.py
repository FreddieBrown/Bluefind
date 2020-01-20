from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import re
import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import bluezutils, discovery, advertising, gatt_server

BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'

def discoStart(bus):
	option_list = [
			make_option("-i", "--device", action="store",
					type="string", dest="dev_id"),
			make_option("-u", "--uuids", action="store",
					type="string", dest="uuids",
					help="Filtered service UUIDs [uuid1,uuid2,...]"),
			make_option("-r", "--rssi", action="store",
					type="int", dest="rssi",
					help="RSSI threshold value"),
			make_option("-p", "--pathloss", action="store",
					type="int", dest="pathloss",
					help="Pathloss threshold value"),
			make_option("-t", "--transport", action="store",
					type="string", dest="transport",
					help="Type of scan to run (le/bredr/auto)"),
			]
	parser = OptionParser(option_list=option_list)

	(options, args) = parser.parse_args()

	adapter = bluezutils.find_adapter(options.dev_id)
	adapter_props = dbus.Interface(bus.get_object("org.bluez", adapter.object_path),
					"org.freedesktop.DBus.Properties")

	# Adds a callback to listen for signals from InterfacesAdded.
	# This will be activated when a new device is found
	bus.add_signal_receiver(discovery.interfaces_added,
			dbus_interface = "org.freedesktop.DBus.ObjectManager",
			signal_name = "InterfacesAdded")

	# This creates a callback when something changes about a 
	# device. This is usually the UUIDs or if it is connected.
	bus.add_signal_receiver(discovery.properties_changed,
			dbus_interface = "org.freedesktop.DBus.Properties",
			signal_name = "PropertiesChanged",
			arg0 = "org.bluez.Device1",
			path_keyword = "path")

	# Sets the Discoverable option to on, meaning devices can discover it
	bluezutils.properties(adapter_props, "Discoverable", "on")    

	# Gets all objects for Bluez on Dbus. This looks for the 
	# Device1 interface so that it can be used later on
	om = dbus.Interface(bus.get_object("org.bluez", "/"),
				"org.freedesktop.DBus.ObjectManager")
	objects = om.GetManagedObjects()
	for path, interfaces in objects.items():
		if "org.bluez.Device1" in interfaces:
			discovery.devices[path] = interfaces["org.bluez.Device1"]

	# Builds the filter for the scan filter
	scan_filter = dict()

	if options.uuids:
		uuids = []
		uuid_list = options.uuids.split(',')
		for uuid in uuid_list:
			uuids.append(uuid)

		scan_filter.update({ "UUIDs": uuids })

	if options.rssi:
		scan_filter.update({ "RSSI": dbus.Int16(options.rssi) })

	if options.pathloss:
		scan_filter.update({ "Pathloss": dbus.UInt16(options.pathloss) })

	if options.transport:
		scan_filter.update({ "Transport": options.transport })

	# Sets the filter for device discovery
	adapter.SetDiscoveryFilter(scan_filter)
	adapter.StartDiscovery()

def server(bus):
	# Gets the LEAdvertisingManager interface on the adapter in use
	ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, bluezutils.find_adapter_path(bus)), LE_ADVERTISING_MANAGER_IFACE)

	# Creates the Advertisement class for emergency advertising
	em_advertisement = advertising.EmergencyAdvertisement(bus, 0)

	# Registers the advert using callbacks for the reply for success and when it has an error
	ad_manager.RegisterAdvertisement(em_advertisement.get_path(), {},
									reply_handler=advertising.register_ad_cb,
									error_handler=advertising.register_ad_error_cb)




# if __name__ == '__main__':
def main():
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()

	discoStart(bus)
	
	server(bus)
	


	mainloop = GLib.MainLoop()
	mainloop.run()
