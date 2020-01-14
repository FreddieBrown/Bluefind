#include "signalSub.hpp"
Discover dis;

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
