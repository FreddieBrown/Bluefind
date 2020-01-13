#include "bluefind.h"
#include <stdio.h>
#include <gio/gio.h>


int main(int argc, char **argv)
{
	GMainLoop *loop;
	int rc;
	guint prop_changed;
	guint iface_added;
	guint iface_removed;

	con = g_bus_get_sync(G_BUS_TYPE_SYSTEM, NULL, NULL);
	if(con == NULL) {
		g_print("Not able to get connection to system bus\n");
		return 1;
	}

	loop = g_main_loop_new(NULL, FALSE);

	prop_changed = g_dbus_connection_signal_subscribe(con,
						"org.bluez",
						"org.freedesktop.DBus.Properties",
						"PropertiesChanged",
						NULL,
						"org.bluez.Adapter1",
						G_DBUS_SIGNAL_FLAGS_NONE,
						bluez_signal_adapter_changed,
						NULL,
						NULL);

	iface_added = g_dbus_connection_signal_subscribe(con,
							"org.bluez",
							"org.freedesktop.DBus.ObjectManager",
							"InterfacesAdded",
							NULL,
							NULL,
							G_DBUS_SIGNAL_FLAGS_NONE,
							new_device,
							loop,
							NULL);

	iface_removed = g_dbus_connection_signal_subscribe(con,
							"org.bluez",
							"org.freedesktop.DBus.ObjectManager",
							"InterfacesRemoved",
							NULL,
							NULL,
							G_DBUS_SIGNAL_FLAGS_NONE,
							bluez_device_disappeared,
							loop,
							NULL);

	rc = bluez_adapter_set_property("Powered", g_variant_new("b", TRUE));
	if(rc) {
		g_print("Not able to enable the adapter\n");
		goto fail;
	}

	if(argc > 3) {
		rc = bluez_set_discovery_filter(argv);
		if(rc)
			goto fail;
	}

	rc =hci0_call_method("org.bluez.Adapter1", "StartDiscovery", NULL, NULL);
	if(rc) {
		g_print("Not able to scan for new devices\n");
		goto fail;
	}

	g_main_loop_run(loop);
	if(argc > 3) {
		rc = hci0_call_method("org.bluez.Adapter1", "SetDiscoveryFilter", NULL, NULL);
		if(rc)
			g_print("Not able to remove discovery filter\n");
	}

	rc = hci0_call_method("org.bluez.Adapter1", "StopDiscovery", NULL, NULL);
	if(rc)
		g_print("Not able to stop scanning\n");
	g_usleep(100);

	rc = bluez_adapter_set_property("Powered", g_variant_new("b", FALSE));
	if(rc)
		g_print("Not able to disable the adapter\n");
fail:
	g_dbus_connection_signal_unsubscribe(con, prop_changed);
	g_dbus_connection_signal_unsubscribe(con, iface_added);
	g_dbus_connection_signal_unsubscribe(con, iface_removed);
	g_object_unref(con);
	return 0;
}
