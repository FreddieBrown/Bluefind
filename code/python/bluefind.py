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
ADAPTER_IFACE = 'org.bluez.Adapter1'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
em_advertisement = None
agent_manager = None
ad_manager = None
client_ty = None
bus = None
mainloop = None

def get_client_type():
	global client_ty
	return client_ty

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
	if client_ty is "n":
		# Cleans up advert if it was registered
		agent_manager.UnregisterAgent(agent.AGENT_PATH)
		print("Agent Unregistered!")
		ad_manager.UnregisterAdvertisement(em_advertisement)
		print('Advertisement Unregistered')
	raise SystemExit('Exiting...')
	return

def decide_device_type():
	global client_ty
	random.seed()
	if(random.randint(0, 10) < 5):
		print("Server")
		client_ty = "n"
	else:
		print("Client")
		client_ty = "y"


if __name__ == '__main__':

	signal.signal(signal.SIGINT, receiveSignal)

	decide_device_type()

	bus = dbus.SystemBus()

	if client_ty is "y":
		client(bus)
	else:
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


		mainloop = GLib.MainLoop()

		agent_manager = agent.register_agent(bus)

		discovery.disco_start(bus, client_ty)

		# Creates the Advertisement class for emergency advertising
		em_advertisement = advertising.EmergencyAdvertisement(bus, 0)
		ad_manager = server(bus, em_advertisement)

		mainloop.run()

		# Cleans up advert if it was registered
		agent_manager.UnregisterAgent(agent.AGENT_PATH)
		print("Agent Unregistered!")
		ad_manager.UnregisterAdvertisement(em_advertisement)
		print('Advertisement Unregistered')