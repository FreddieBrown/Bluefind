def dbus_to_MAC(name):
	return ":".join(name.lstrip("/org/bluez/hci0/dev_").split("_"))
	
	


print(dbus_to_MAC("/org/bluez/hci0/dev_B8_27_EB_E7_B4_70"))
