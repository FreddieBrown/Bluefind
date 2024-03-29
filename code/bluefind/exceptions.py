import re
import sys
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

"""
File which holds exceptions needed through the program. 
Each of these exceptions is needed for different things 
within BlueZ. They are all kept in this module as they 
all have very similar behaviour.
"""
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

class RejectedException(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"