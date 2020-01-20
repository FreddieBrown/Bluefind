import dbus

SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"

def get_managed_objects():
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("org.bluez", "/"),
				"org.freedesktop.DBus.ObjectManager")
	return manager.GetManagedObjects()

def find_adapter(pattern=None):
	return find_adapter_in_objects(get_managed_objects(), pattern)

def find_adapter_path(bus):
	remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
							   DBUS_OM_IFACE)
	objects = remote_om.GetManagedObjects()

	for o, props in objects.items():
		if LE_ADVERTISING_MANAGER_IFACE in props:
			return o

	return None

def find_adapter_in_objects(objects, pattern=None):
	bus = dbus.SystemBus()
	for path, ifaces in objects.items():
		adapter = ifaces.get(ADAPTER_INTERFACE)
		if adapter is None:
			continue
		if not pattern or pattern == adapter["Address"] or \
							path.endswith(pattern):
			obj = bus.get_object(SERVICE_NAME, path)
			return dbus.Interface(obj, ADAPTER_INTERFACE)
	raise Exception("Bluetooth adapter not found")

def find_device(device_address, adapter_pattern=None):
	return find_device_in_objects(get_managed_objects(), device_address,
								adapter_pattern)

def find_device_in_objects(objects, device_address, adapter_pattern=None):
	bus = dbus.SystemBus()
	path_prefix = ""
	if adapter_pattern:
		adapter = find_adapter_in_objects(objects, adapter_pattern)
		path_prefix = adapter.object_path
	for path, ifaces in objects.items():
		device = ifaces.get(DEVICE_INTERFACE)
		if device is None:
			continue
		if (device["Address"] == device_address and
						path.startswith(path_prefix)):
			obj = bus.get_object(SERVICE_NAME, path)
			return dbus.Interface(obj, DEVICE_INTERFACE)

	raise Exception("Bluetooth device not found")

def properties(adapter_p, prop, onoff):
	if onoff == "on":
		status = dbus.Boolean(1)
	elif onoff == "off": 
		status = dbus.Boolean(0)
	else: 
		status = onoff
	print("\t%s = %s" % (prop, onoff))
	adapter_p.Set("org.bluez.Adapter1", prop, status)
