import dbus
import datetime

SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"
BLUEZ_SERVICE_NAME = 'org.bluez'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'

def get_managed_objects():
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("org.bluez", "/"),
				"org.freedesktop.DBus.ObjectManager")
	return manager.GetManagedObjects()

def find_adapter(pattern=None):
	return find_adapter_in_objects(get_managed_objects(), pattern)

def find_adapter_path(bus, iface):
	remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
							   DBUS_OM_IFACE)
	objects = remote_om.GetManagedObjects()

	for o, props in objects.items():
		if iface in props or (iface in props.keys()):
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

def get_mac_addr(bus):
	adapter = find_adapter()
	adapter_props = dbus.Interface(bus.get_object("org.bluez", adapter.object_path),
					"org.freedesktop.DBus.Properties")
	address = adapter_props.Get("org.bluez.Adapter1", "Address")
	print("Address is : {}".format(address))
	return address

def build_message(locations, addresses, filter_addr = None):
	message=[]
	for i in range(0,len(locations)):
        if filter_addr and filter_addr == addresses[i]:
            continue
		message.append("1=({})|2={}|".format(locations[i], addresses[i]))

	true_mess = ''.join(message)
	print("Built Message: "+true_mess)

	return true_mess

def break_down_message(message):
	ret_dict = {}
	tvps = message.split("|")
	for tvp in tvps:
		tvp_no_equals = tvp.split("=")
		# Check if entry for tag exists
		if tvp_no_equals[0] in ret_dict:
			# If it does, get list associated with it and add element to it
			ret_dict[tvp_no_equals[0]].append(tvp_no_equals[1])
		else:
			# If it doesn't, create new list with element in it associated with tag
			if len(tvp_no_equals) is 2:
				ret_dict[tvp_no_equals[0]] = [tvp_no_equals[1]]
	return ret_dict
		

def to_byte_array(value):
	# Convert string into some sort of char array
	char_arr = list(value)
	ret_list = []
	# For each member of the char array, get the ASCII code for each character
	for char in char_arr:
		ascii_v = ord(char)
		# Take each ASCII code and create a dbus.Byte object with it and add it to another array
		ret_list.append(dbus.Byte(ascii_v))
	# Once byte array built, return
	return ret_list

def from_byte_array(val_arr):
	med_arr = []
	# Take byte array and work out character of each value
	for value in val_arr:
		med_arr.append(chr(value)) 
	# With each character, add it to a string
	ret_string = ''.join(med_arr)
	# return string
	return ret_string

def split_message(message):
	"""
	Method splits message into 19byte chunks 
	"""
	mess_size = 16
	byte_arr = []
	message_len = len(message)
	for i in range(0, int(message_len/mess_size)):
		j = (i+1)*mess_size
		byte_arr.append(message[i*mess_size:j])
	if message_len%mess_size is not 0:
		byte_arr.append(message[(i+1)*mess_size:(i+1)*mess_size+message_len%mess_size])
	byte_arr.append(chr(5))
	return byte_arr

def dbus_to_MAC(name):
	return ":".join(name.lstrip("/org/bluez/hci0/dev_").split("_"))

def get_sequence_number(message):
	message_parts = message.split("\x01")
	print("Sequence Number: {}".format(message_parts[0]))
	return message_parts[0], message_parts[1]

def add_to_db(db, broken_down_msg):
    now = datetime.datetime.now()
    coords = broken_down_msg['1']
    addresses = broken_down_msg['2']
    values = []
    if len(coords) == len(addresses):
        for i in range(0, len(coords)):
            values.append((addresses[i], coords[i].strip('()'), now))
    db.insert(values)
