#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser
import sys
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import bluezutils

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

def trust_device(path):
    # TODO: Change bluefind.py so bus can be accessed here
    properties = dbus.Interface(bus.get_object(BUS_NAME, path), 
                                "org.freedesktop.DBus.Properties")
    properties.Set("org.bluez.Device1", "Trusted", True)

def connect_dev(path):
    # TODO: Change bluefind.py so bus can be accessed here
    device = dbus.Interface(bus.get_object(BUS_NAME, path), "org.bluez.Device1")
    device.Connect()
    return device

class Agent(dbus.service.Object):
    exit_on_release = True

    def set_eor(self, eor):
        self.exit_on_release = eor

	@dbus.service.method(AGENT_INTERFACE,
					in_signature="", out_signature="")
    def Release(self):
        print("Release Agent")
        if self.exit_on_release:
            # TODO: Change bluefind.py so mainloop can be accessed here
            mainloop.quit()
    
    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode (%s)" % (device))
        trust_device(device)
        return "placeholder string"

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pin):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        pass  

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        pass
