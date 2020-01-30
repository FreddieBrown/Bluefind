from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import re
import sys
import dbus
import os
import random
import signal
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import bluezutils, discovery, advertising, gatt_server, agent


BLUEZ_SERVICE_NAME = 'org.bluez'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
em_advertisement = None
agent_manager = None
ad_manager = None

def get_client_type():
	return client_ty

def disco_start(bus):

	adapter = bluezutils.find_adapter()
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
			discovery.devices[path] = interfaces["org.bluez.Device1"]

	# Builds the filter for the scan filter
	scan_filter = dict()
	
	if client_ty is "y":
		scan_filter.update({ "UUIDs": ['0000FFF0-0000-1000-8000-00805f9b34fb'] })

	# Sets the filter for device discovery
	adapter.SetDiscoveryFilter(scan_filter)
	adapter.StartDiscovery()

def server(bus, ad):
	print("Server mode started")
	gatt_server.GATTStart(bus)
	# Gets the LEAdvertisingManager interface on the adapter in use
	ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, bluezutils.find_adapter_path(bus, LE_ADVERTISING_MANAGER_IFACE)), LE_ADVERTISING_MANAGER_IFACE)

	# Registers the advert using callbacks for the reply for success and when it has an error
	ad_manager.RegisterAdvertisement(ad.get_path(), {},
									reply_handler=advertising.register_ad_cb,
									error_handler=advertising.register_ad_error_cb)
	
	return ad_manager

def client(bus):
	print("Client mode started")


def receiveSignal(signal_number, frame):
	print('Received: '+str(signal_number))
	print("Client: %s" % client_ty)
	agent_manager.UnregisterAgent(agent.AGENT_PATH)
	print("Agent Unregistered!")
	if client_ty is "n":
		# Cleans up advert if it was registered
		ad_manager.UnregisterAdvertisement(em_advertisement)
		print('Advertisement Unregistered')
	raise SystemExit('Exiting...')
	return

def decide_device_type():
	random.seed()
	if(random.randint(0, 10) < 5):
		print("Server")
		return "n"
	else:
		print("Client")
		return "y"


if __name__ == '__main__':

	global client_ty
	global bus
	global mainloop

	signal.signal(signal.SIGINT, receiveSignal)

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()

	mainloop = GLib.MainLoop()

	client_ty = decide_device_type()

	agent_manager = agent.register_agent(bus)

	disco_start(bus)

	if client_ty is "y":
		client(bus)
	else:
		# Creates the Advertisement class for emergency advertising
		em_advertisement = advertising.EmergencyAdvertisement(bus, 0)
		ad_manager = server(bus, em_advertisement)

	mainloop.run()

	if client_ty is "n":
		# Cleans up advert if it was registered
		agent_manager.UnregisterAgent(agent.AGENT_PATH)
		print("Agent Unregistered!")
		ad_manager.UnregisterAdvertisement(em_advertisement)
		print('Advertisement Unregistered')