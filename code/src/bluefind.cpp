#include "bluefind.hpp"
#include <stdio.h>
#include <gio/gio.h>
#include <glib.h>


GDBusConnection *con;
std::vector<struct bth_device_info> devices;
guint bus_name;
GDBusNodeInfo *introspection_data = NULL;
Discover dis;
guint registration_id;

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
    GError *error=NULL;
    const gchar* name = "net.noser";
    

	con = g_bus_get_sync(G_BUS_TYPE_SYSTEM, NULL, NULL);
	if(con == NULL) {
		g_print("Not able to get connection to system bus\n");
		return 1;
	}

    // Introspection data
    introspection_data = g_dbus_node_info_new_for_xml (introspection_xml, &error);
    if(introspection_data == NULL){
        g_warning ("Error %s", error->message);
    }

    // Claim name on BUS
    bus_name = g_bus_own_name_on_connection (con,
                              name,
                              G_BUS_NAME_OWNER_FLAGS_NONE,
                              on_name_acquired,
                              on_name_lost,
                              NULL,
                              NULL);

	loop = g_main_loop_new(NULL, FALSE);

    // g_unix_signal_add(SIGINT, signalHandler, loop);

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

    rc = dis.adapter_set_property("Discoverable", g_variant_new("b", TRUE));
    if(rc) {
		g_print("Not able to make it visible\n");
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
	g_bus_unown_name (bus_name);
    g_dbus_node_info_unref (introspection_data);
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
// static gboolean signalHandler (gpointer data)
// {
//     g_print(" SIGINT\n");
//     std::cout<<"Devices found: "<<devices.size()<<std::endl;
//     while(!devices.empty()){
//         struct bth_device_info device = devices.back();
//         devices.pop_back();
//         g_print("%s, %s\n", device.address, device.alias);
//     }
//     int rc = dis.adapter_set_property("Powered", g_variant_new("b", TRUE));
// 	if(rc) {
// 		g_print("Not able to enable the adapter\n");
// 	}
//     g_main_loop_quit((GMainLoop *)data);
//     return G_SOURCE_REMOVE;
// }

/**
 * This functions deals with the consequences of not acquiring the 
 * name on the Bus.
 * 
 * @param connection 
 * @param name 
 * @param user_data 
 */
static void on_name_lost(GDBusConnection * connection,
             const gchar * name,
             gpointer user_data)
{
    g_print("Name not acquired\n");
}

/**
 * This functions deals with what happens when the name is 
 * claimed on the Bus. This sets up the introspectable data 
 * for other devices to interface with. 
 * 
 * @param connection 
 * @param name 
 * @param user_data 
 */
static void on_name_acquired (GDBusConnection *connection,
                  const gchar     *name,
                  gpointer         user_data)
{
    // Need to register the introspection data using the connection 
    // using g_dbus_connection_register_object
    // Before this, need to create a GDBusInterfaceVTable containing the 
    // functions for the interface.
    registration_id = g_dbus_connection_register_object (connection,
                                                       "/org/bluez/TestDevice",
                                                       introspection_data->interfaces[0],
                                                       &interface_vtable,
                                                       NULL,  /* user_data */
                                                       NULL,  /* user_data_free_func */
                                                       NULL); /* GError** */
}

/**
 * Method to handle what happens when a method is called over DBus.
 * It takes information about where it has come from and the connection 
 * it has occured over. 
 * 
 * @param connection 
 * @param sender 
 * @param object_path 
 * @param interface_name 
 * @param method_name 
 * @param parameters 
 * @param invocation 
 * @param user_data 
 */

static void handle_method_call (GDBusConnection       *connection,
                    const gchar           *sender,
                    const gchar           *object_path,
                    const gchar           *interface_name,
                    const gchar           *method_name,
                    GVariant              *parameters,
                    GDBusMethodInvocation *invocation,
                    gpointer               user_data)
{
    return;
}

/**
 * Function to handle calls to get information over DBus
 * 
 * @param connection 
 * @param sender 
 * @param object_path 
 * @param interface_name 
 * @param property_name 
 * @param error 
 * @param user_data 
 * @return GVariant* 
 */
static GVariant *handle_get_property (GDBusConnection  *connection,
                     const gchar      *sender,
                     const gchar      *object_path,
                     const gchar      *interface_name,
                     const gchar      *property_name,
                     GError          **error,
                     gpointer          user_data)
{
    return (GVariant *) NULL;
}

/**
 * Function to handle Set calls over DBus
 * 
 * @param connection 
 * @param sender 
 * @param object_path 
 * @param interface_name 
 * @param property_name 
 * @param value 
 * @param error 
 * @param user_data 
 * @return gboolean 
 */
static gboolean handle_set_property (GDBusConnection  *connection,
                     const gchar      *sender,
                     const gchar      *object_path,
                     const gchar      *interface_name,
                     const gchar      *property_name,
                     GVariant         *value,
                     GError          **error,
                     gpointer          user_data)
{
    return (gboolean) NULL;
}

/**
 * This is a function which is used to track new devices which are found by 
 * adapter1. This is the main tennant of the searching framework. It gets called 
 * when there is a new adapter and will sort through the signal that it gets and 
 * extracts the critical information. 
 * 
 * @param sig 
 * @param sender_name 
 * @param object_path 
 * @param interface 
 * @param signal_name 
 * @param parameters 
 * @param user_data 
 */
static void new_device(GDBusConnection *sig,
				const gchar *sender_name,
				const gchar *object_path,
				const gchar *interface,
				const gchar *signal_name,
				GVariant *parameters,
				gpointer user_data)
{

	GVariantIter *interfaces;
	const char *object;
	const gchar *interface_name;
	GVariant *properties;

	g_variant_get(parameters, "(&oa{sa{sv}})", &object, &interfaces);
	while(g_variant_iter_next(interfaces, "{&s@a{sv}}", &interface_name, &properties)) {
        struct bth_device_info device;
		if(g_strstr_len(g_ascii_strdown(interface_name, -1), -1, "device")) {
			g_print("[ %s ]\n", object);
			const gchar *property_name;
			GVariantIter i;
			GVariant *prop_val;
			g_variant_iter_init(&i, properties);
            // Create Data structure here
			while(g_variant_iter_next(&i, "{&sv}", &property_name, &prop_val)){
                // Here is where the adapter information can be seen
                // Need to write more code to extract the address and alias 
                // for each device that is seen by the program.
                const gchar* val_string = dis.property_value(property_name, prop_val);
                if(strcasecmp(property_name, "address") == 0){
                    device.address = val_string;
                }
                else if(strcasecmp(property_name, "alias") == 0){
                    device.alias = val_string;
                }
            }
			g_variant_unref(prop_val);
            devices.push_back(device);
		}
		g_variant_unref(properties);
	}
	return;
}

/**
 * This function deals with when devices leave the range of the 
 * device and disappear. It will register this and print the 
 * MAC address of the device which has disappeared.
 * 
 * @param sig 
 * @param sender_name 
 * @param object_path 
 * @param interface 
 * @param signal_name 
 * @param parameters 
 * @param user_data 
 */
static void device_disappeared(GDBusConnection *sig,
				const gchar *sender_name,
				const gchar *object_path,
				const gchar *interface,
				const gchar *signal_name,
				GVariant *parameters,
				gpointer user_data)
{

	GVariantIter *interfaces;
	const char *object;
	const gchar *interface_name;
	char address[BT_ADDRESS_STRING_SIZE] = {'\0'};

	g_variant_get(parameters, "(&oas)", &object, &interfaces);
	while(g_variant_iter_next(interfaces, "s", &interface_name)) {
		if(g_strstr_len(g_ascii_strdown(interface_name, -1), -1, "device")) {
			int i;
			char *tmp = g_strstr_len(object, -1, "dev_") + 4;

			for(i = 0; *tmp != '\0'; i++, tmp++) {
				if(*tmp == '_') {
					address[i] = ':';
					continue;
				}
				address[i] = *tmp;
			}
			g_print("\nDevice %s removed\n", address);
		}
	}
	return;
}

/**
 * This function will register when an adapter has changed its information. 
 * It will take the signal and split off its parameters to look through. This 
 * function mainly looks for  whether the adapter is powered and is discovering 
 * devices.
 * 
 * @param conn 
 * @param sender 
 * @param path 
 * @param interface 
 * @param signal 
 * @param params 
 * @param userdata 
 */
static void signal_adapter_changed(GDBusConnection *conn,
					const gchar *sender,
					const gchar *path,
					const gchar *interface,
					const gchar *signal,
					GVariant *params,
					void *userdata)
{

	GVariantIter *properties = NULL;
	GVariantIter *unknown = NULL;
	const char *iface;
	const char *key;
	GVariant *value = NULL;
	const gchar *signature = g_variant_get_type_string(params);

	if(strcmp(signature, "(sa{sv}as)") != 0) {
		g_print("Invalid signature for %s: %s != %s", signal, signature, "(sa{sv}as)");
		goto done;
	}

	g_variant_get(params, "(&sa{sv}as)", &iface, &properties, &unknown);
	while(g_variant_iter_next(properties, "{&sv}", &key, &value)) {
		if(!g_strcmp0(key, "Powered")) {
			if(!g_variant_is_of_type(value, G_VARIANT_TYPE_BOOLEAN)) {
				g_print("Invalid argument type for %s: %s != %s", key,
						g_variant_get_type_string(value), "b");
				goto done;
			}
			g_print("Adapter is Powered \"%s\"\n", g_variant_get_boolean(value) ? "on" : "off");
		}
		if(!g_strcmp0(key, "Discovering")) {
			if(!g_variant_is_of_type(value, G_VARIANT_TYPE_BOOLEAN)) {
				g_print("Invalid argument type for %s: %s != %s", key,
						g_variant_get_type_string(value), "b");
				goto done;
			}
			g_print("Adapter scan \"%s\"\n", g_variant_get_boolean(value) ? "on" : "off");
		}
        else{
            dis.property_value(key, value);
        }
	}
done:
	if(properties != NULL)
		g_variant_iter_free(properties);
	if(value != NULL)
		g_variant_unref(value);
}
