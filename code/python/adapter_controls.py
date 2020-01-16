# This file will be for functions which will mutate properties of the adapter
# e.g things like enabling discoverability

from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser, make_option
import re
import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

import bluezutils

def properties(adapter_p, prop, onoff):
    if onoff == "on":
        status = dbus.Boolean(1)
    elif onoff == "off": 
        status = dbus.Boolean(0)
    else: 
        status = onoff
    print("\t%s = %s", prop, onoff)
    adapter_p.Set("org.bluez.Adapter1", prop, status)