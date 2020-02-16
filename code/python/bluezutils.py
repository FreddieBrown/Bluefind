import dbus
import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"
BLUEZ_SERVICE_NAME = 'org.bluez'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'

def get_managed_objects():
	"""
	Function to return the objects which are managed by 
	DBUS using the object manager interface.
	"""
	bus = dbus.SystemBus()
	manager = dbus.Interface(bus.get_object("org.bluez", "/"),
				"org.freedesktop.DBus.ObjectManager")
	return manager.GetManagedObjects()

def find_adapter(pattern=None):
	"""
	Method to find the first free device adapter which can 
	be used. 
	"""
	return find_adapter_in_objects(get_managed_objects(), pattern)

def find_adapter_path(bus, iface):
	"""
	Function to find the path of the adapter passed in 
	to the method.
	"""
	remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
							   DBUS_OM_IFACE)
	objects = remote_om.GetManagedObjects()

	for o, props in objects.items():
		if iface in props or (iface in props.keys()):
			return o

	return None

def find_adapter_in_objects(objects, pattern=None):
	"""
	Function which will, if given a dict of objects, will 
	go through the paths and interfaces of each object and 
	will check to see if the adapter is in there. If it is, 
	it will get the object of the adapter and return it.
	"""
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
	"""
	Function which will return the object for the interface 
	org.bluez.Device1.
	"""
	return find_device_in_objects(get_managed_objects(), device_address,
								adapter_pattern)

def find_device_in_objects(objects, device_address, adapter_pattern=None):
	"""
	Function which will, when provided with a dict of objects, find 
	the object which belongs to the interface org.bluez.Device1.
	"""
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
	"""
	Function will alter properties of an adapter if 
	passed the adapter properties interface.
	"""
	if onoff == "on":
		status = dbus.Boolean(1)
	elif onoff == "off": 
		status = dbus.Boolean(0)
	else: 
		status = onoff
	print("\t%s = %s" % (prop, onoff))
	adapter_p.Set("org.bluez.Adapter1", prop, status)

def get_mac_addr(bus):
	"""
	Function to get the MAC address of the current adapter being 
	used by the device.
	"""
	adapter = find_adapter()
	adapter_props = dbus.Interface(bus.get_object("org.bluez", adapter.object_path),
					"org.freedesktop.DBus.Properties")
	address = adapter_props.Get("org.bluez.Adapter1", "Address")
	print("Address is : {}".format(address))
	return address

def build_message(locations, addresses, filter_addr = None):
	"""
	Function which will take a list of locations and addresses and will 
	build a FIX-type message using tags 1 and 2. There is also a filter 
	which can filter out certain addresses from the message.
	"""
	message=[]
	if filter_addr:
		print("Addresses to filter: {}".format(filter_addr))
		
	for i in range(0,len(locations)):
		if filter_addr and addresses[i] in filter_addr :
			print("Filtering address: {}".format(addresses[i]))
			continue
		message.append("1=({})|2={}|".format(locations[i], addresses[i]))

	true_mess = ''.join(message)
	print("Built Message: "+true_mess)

	return true_mess

def break_down_message(message):
	"""
	When provided with a FIX-type message, the function will split 
	it up and will store the values in a dictionary, which will then 
	be returned.
	"""
	ret_dict = {}
	tvps = message.split("|")
	for tvp in tvps:
		tvp_no_equals = tvp.split("=")
		if len(tvp_no_equals) is 2:
			save = tvp_no_equals[1]
		elif len(tvp_no_equals) > 2:
			save = "=".join(tvp_no_equals[1:])
		# Check if entry for tag exists
		if tvp_no_equals[0] in ret_dict:
			# If it does, get list associated with it and add element to it
			ret_dict[tvp_no_equals[0]].append(save)
		else:
			ret_dict[tvp_no_equals[0]] = [save]
	return ret_dict
		

def to_byte_array(value):
	"""
	This function will take a string and will split it 
	down into an array of bytes. This will then be returned.
	"""
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
	"""
	When provided with a list of bytes, the function will convert 
	it into an ASCII string and will return it.
	"""
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
	Method splits message into 16byte chunks so they can be transmitted 
	using Bluetooth. 
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
	"""
	To get the MAC address of a device using DBUS, some information needs 
	to be cleaned off the address so it can be formed.
	"""
	return ":".join(name.lstrip("/org/bluez/hci0/dev_").split("_"))

def get_sequence_number(message):
	"""
	When given a message fragment, it will break it down based on the 
	SOH and will return the sequence number (before the SOH) and the 
	message fragment (after the SOH).
	"""
	message_parts = message.split("\x01")
	print("Sequence Number: {}".format(message_parts[0]))
	return message_parts[0], message_parts[1]

def add_to_db(db, broken_down_msg):
	"""
	When provided with a broken down message and a db connection, the function will 
	form tuples of data to add to the db and will insert it.
	"""
	now = datetime.datetime.now()
	coords = broken_down_msg['1']
	addresses = broken_down_msg['2']
	values = []
	if len(coords) == len(addresses):
		for i in range(0, len(coords)):
			values.append((addresses[i], coords[i].strip('()'), now))
	db.insert(values)

def generate_RSA_keypair():
	key = RSA.generate(1024)
	private = key.export_key()
	public = key.publickey().export_key()
	return {
		"private" : from_byte_array(private),
		"public" : from_byte_array(public),
	}

def build_generic_message(message_struct):
	"""
	Takes a dict where keys are tags, and each has a list with
	values for that tag, e.g 
	{
		1 : [...],
		2 : [...],
		3 : [...],
	}
	"""
	message = ""
	for key, value in message_struct.items():
		for item in value:
			message+="{}={}|".format(key, item)
	return message

def encrypt_message(public_key, message):
	key = RSA.importKey(public_key)
	cipher_rsa = PKCS1_OAEP.new(key)
	return cipher_rsa.encrypt(str.encode(message))

def decrypt_message(private_key, ciphertext):
	key = RSA.importKey(private_key)
	cipher = PKCS1_OAEP.new(key)
	return cipher.decrypt(ciphertext).decode()