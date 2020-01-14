#include "bluefind.hpp"
#include <stdio.h>
#include <gio/gio.h>


GDBusConnection *con;
Discover dis;
std::vector<struct bth_device_info> devices;
guint bus_name;
GDBusNodeInfo *introspection_data;

/**
 * Main function of the project. This is where everything starts and is run from.
 * 
 * @param argc 
 * @param argv 
 * @return int 
 */
int main(int argc, char **argv)
{
	GMainLoop *loop;
	int rc;
	guint prop_changed;
	guint iface_added;
	guint iface_removed;
    GVariant* power;
    const gchar* name = "net.noser.bluefind";
    

	con = g_bus_get_sync(G_BUS_TYPE_SYSTEM, NULL, NULL);
	if(con == NULL) {
		g_print("Not able to get connection to system bus\n");
		return 1;
	}

    // Introspection data
    introspection_data = g_dbus_node_info_new_for_xml (introspection_xml, NULL);

    // Claim name on BUS
    bus_name = g_bus_own_name_on_connection (con,
                              name,
                              G_BUS_NAME_OWNER_FLAGS_NONE,
                              on_name_acquired,
                              on_name_lost,
                              NULL,
                              NULL);

	loop = g_main_loop_new(NULL, FALSE);

    g_unix_signal_add(SIGINT, signalHandler, loop);

	prop_changed = g_dbus_connection_signal_subscribe(con,
						"org.bluez",
						"org.freedesktop.DBus.Properties",
						"PropertiesChanged",
						NULL,
						"org.bluez.Adapter1",
						G_DBUS_SIGNAL_FLAGS_NONE,
						signal_adapter_changed,
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
							device_disappeared,
							loop,
							NULL);
	rc = dis.adapter_set_property("Powered", g_variant_new("b", TRUE));
	if(rc) {
		g_print("Not able to enable the adapter\n");
		goto fail;
	}

    power = dis.adapter_get_property("Powered");
    g_print("Adapter1 Powered: %d\n",  g_variant_get_boolean(g_variant_get_child_value(g_variant_get_child_value(power,0),0)));
    g_variant_unref(power);

	if(argc > 3) {
		rc = dis.set_discovery_filter(argv);
		if(rc)
			goto fail;
	}

	rc =dis.hci0_call_method("org.bluez.Adapter1", "StartDiscovery", NULL, NULL);
	if(rc) {
		g_print("Not able to scan for new devices\n");
		goto fail;
	}

	g_main_loop_run(loop);
	if(argc > 3) {
		rc = dis.hci0_call_method("org.bluez.Adapter1", "SetDiscoveryFilter", NULL, NULL);
		if(rc)
			g_print("Not able to remove discovery filter\n");
	}

	rc = dis.hci0_call_method("org.bluez.Adapter1", "StopDiscovery", NULL, NULL);
	if(rc)
		g_print("Not able to stop scanning\n");
	g_usleep(100);

	rc = dis.adapter_set_property("Powered", g_variant_new("b", FALSE));
	if(rc)
		g_print("Not able to disable the adapter\n");
fail:
	g_dbus_connection_signal_unsubscribe(con, prop_changed);
	g_dbus_connection_signal_unsubscribe(con, iface_added);
	g_dbus_connection_signal_unsubscribe(con, iface_removed);
	g_object_unref(con);
	return 0;
}
/**
 * Signal Handler. This is what happens when CRTL^C is used. 
 * It will print information about all devices that it has seen and 
 * will quit the program.
 * 
 * @param sig 
 */
static gboolean signalHandler (gpointer data)
{
    g_print(" SIGINT\n");
	g_object_unref(con);
    std::cout<<"Devices found: "<<devices.size()<<std::endl;
    while(!devices.empty()){
        struct bth_device_info device = devices.back();
        devices.pop_back();
        g_print("%s, %s\n", device.address, device.alias);
    }
    g_debug("Got SIGINT");
    g_main_loop_quit((GMainLoop *)data);
    // unref bus name
    g_bus_unown_name (bus_name);
    g_dbus_node_info_unref (introspection_data);
    return G_SOURCE_REMOVE;
}
