from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import re
import sys
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import time
import threading
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import bluezutils

LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

class InvalidArgsException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class NotSupportedException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.bluez.Error.NotSupported'


class NotPermittedException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.bluez.Error.NotPermitted'


class InvalidValueLengthException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.bluez.Error.InvalidValueLength'


class FailedException(dbus.exceptions.DBusException):
	_dbus_error_name = 'org.bluez.Error.Failed'

class Advertisment(dbus.service.Object):
    PATH_BASE = "org/bluez/bluefind/advertisement"

    def __init__(self, bus, index, adtype):
        self.path = PATH_BASE + str(index)
        self.bus = bus
        self.adtype = adtype
        self.service_uuids = None
		self.manufacturer_data = None
		self.solicit_uuids = None
		self.service_data = None
		self.local_name = None
		self.include_tx_power = None
		self.data = None
		dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = {}
        properties["Type"] = self.adtype
        if self.service_uuids is not None:
            properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature='s')
        
        if self.manufacturer_data is not None:
            properties["ManufacturerData"] = dbus.Dictionary(self.manufacturer_data, signature='qv')
        
        if self.solicit_uuids is not None:
            properties["SolicitUUIDs"] = dbus.Array(self.solicit_uuids, signature='s')
        
        if self.service_data is not None:
            properties["ServiceData"] = dbus.Dictionary(self.service_data, signature='sv')
        
        if self.local_name is not None:
            properties["LocalName"] = dbus.String(self.local_name)

        if self.include_tx_power is not None:
            properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
        
        if self.data is not None:
            properties['Data'] = dbus.Dictionary(self.data, signature='yv')
        
        return {LE_ADVERTISEMENT_IFACE: properties}


