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

def server(bus, ad):
    """
    This function is used to start up the server. It will define and register 
    GATT functionality and advertisement, including any callbacks. This is 
    functionality specific to a server device, so this function is only called 
    when the device runs as one. 
    """
	print("Server mode started")
	gatt_server.GATTStart(bus)
	# Gets the LEAdvertisingManager interface on the adapter in use
	ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, bluezutils.find_adapter_path(bus, LE_ADVERTISING_MANAGER_IFACE)), LE_ADVERTISING_MANAGER_IFACE)

	# Registers the advert using callbacks for the reply for success and when it has an error
	ad_manager.RegisterAdvertisement(ad.get_path(), {},
									reply_handler=advertising.register_ad_cb,
									error_handler=advertising.register_ad_error_cb)
	
	return ad_manager

def client():
    """
    Function starts up the clientside functionalty of the project.
    """
	print("Client mode started")

def receiveSignal(signal_number, frame):
    """
    Signal handler for the project. This is to clean up the 
    serverside functionality and to ensure the program will 
    exit safely in the event of an untimely exit.
    """
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
    """
    Function to randomly decide if device should be a 
    device or if it should be a server. 
    """
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



	if client_ty is "y":
		client()
	else:
        # Set parameters about Dbus main loop
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        # new instance of dbus system bus
		bus = dbus.SystemBus()

        # Startup main GLib loop which will allow program to run 
        # indefinetly with dbus
		mainloop = GLib.MainLoop()

        # Register agent
		agent_manager = agent.register_agent(bus)

        # Start device discovery
		discovery.disco_start(bus)

		# Creates the Advertisement class for emergency advertising
		em_advertisement = advertising.EmergencyAdvertisement(bus, 0)
		ad_manager = server(bus, em_advertisement)

        # run mainloop
		mainloop.run()

		# Cleans up advert if it was registered
		agent_manager.UnregisterAgent(agent.AGENT_PATH)
		print("Agent Unregistered!")
		ad_manager.UnregisterAdvertisement(em_advertisement)
		print('Advertisement Unregistered')