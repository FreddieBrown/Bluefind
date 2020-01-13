#include "discover.hpp"

/**
 * Method to take a key and a GVariant and print out the 
 * value of the GVariant if it is a single value.
 * 
 * @param key 
 * @param value 
 */
void Discover::property_value(const gchar *key, GVariant *value)
{
	const gchar *type = g_variant_get_type_string(value);

	g_print("\t%s : ", key);
	switch(*type) {
		case 'o':
		case 's':
			g_print("%s\n", g_variant_get_string(value, NULL));
			break;
		case 'b':
			g_print("%d\n", g_variant_get_boolean(value));
			break;
		case 'u':
			g_print("%d\n", g_variant_get_uint32(value));
			break;
		case 'a':
		/* TODO Handling only 'as', but not array of dicts */
			if(g_strcmp0(type, "as"))
				break;
			g_print("\n");
			const gchar *uuid;
			GVariantIter i;
			g_variant_iter_init(&i, value);
			while(g_variant_iter_next(&i, "s", &uuid))
				g_print("\t\t%s\n", uuid);
			break;
		default:
			g_print("Other\n");
			break;
	}
}

/**
 * This function is use the object path /org/bluez/hci0. It takes an adapter name, method name, parameters 
 * and an optional call back method. This is used to 
 * 
 * @param adapter
 * @param method 
 * @param param 
 * @param method_cb 
 * @return int 
 */
int Discover::hci0_call_method(const char* api, const char *method, GVariant *param, method_cb_t method_cb)
{
	GError *error = NULL;

	g_dbus_connection_call(con,
			     "org.bluez",
			     "/org/bluez/hci0",
			     api,
			     method,
			     param,
			     NULL,
			     G_DBUS_CALL_FLAGS_NONE,
			     -1,
			     NULL,
			     method_cb,
			     &error);
	if(error != NULL)
		return 1;
	return 0;
}

int Discover::adapter_set_property(const char *prop, GVariant *value)
{
	GVariant *result;
	GError *error = NULL;

	result = g_dbus_connection_call_sync(con,
					     "org.bluez",
					     "/org/bluez/hci0",
					     "org.freedesktop.DBus.Properties",
					     "Set",
					     g_variant_new("(ssv)", "org.bluez.Adapter1", prop, value),
					     NULL,
					     G_DBUS_CALL_FLAGS_NONE,
					     -1,
					     NULL,
					     &error);
	if(error != NULL)
		return 1;

	g_variant_unref(result);
	return 0;
}

GVariant* Discover::adapter_get_property(const char *prop)
{
	GVariant *result;
	GError *error = NULL;

	result = g_dbus_connection_call_sync(con,
					     "org.bluez",
					     "/org/bluez/hci0",
					     "org.freedesktop.DBus.Properties",
					     "Get",
					     g_variant_new("(ss)", "org.bluez.Adapter1", prop),
					     NULL,
					     G_DBUS_CALL_FLAGS_NONE,
					     -1,
					     NULL,
					     &error);
	if(error != NULL)
		return NULL;

    return result;

}

int Discover::set_discovery_filter(char **argv)
{
	int rc;
	GVariantBuilder *b = g_variant_builder_new(G_VARIANT_TYPE_VARDICT);
	g_variant_builder_add(b, "{sv}", "Transport", g_variant_new_string(argv[1]));
	g_variant_builder_add(b, "{sv}", "RSSI", g_variant_new_int16(-g_ascii_strtod(argv[2], NULL)));
	g_variant_builder_add(b, "{sv}", "DuplicateData", g_variant_new_boolean(FALSE));
    g_variant_builder_add(b, "{sv}", "Discoverable", g_variant_new_boolean(TRUE));

	GVariantBuilder *u = g_variant_builder_new(G_VARIANT_TYPE_STRING_ARRAY);
	g_variant_builder_add(u, "s", argv[3]);
	g_variant_builder_add(b, "{sv}", "UUIDs", g_variant_builder_end(u));

	GVariant *device_dict = g_variant_builder_end(b);
	g_variant_builder_unref(u);
	g_variant_builder_unref(b);
	rc = hci0_call_method("org.bluez.Adapter1", "SetDiscoveryFilter", g_variant_new_tuple(&device_dict, 1), NULL);
	if(rc) {
		g_print("Not able to set discovery filter\n");
		return 1;
	}

	rc = hci0_call_method("org.bluez.Adapter1", "GetDiscoveryFilters",
			NULL,
			get_discovery_filter_cb);
	if(rc) {
		g_print("Not able to get discovery filter\n");
		return 1;
	}
	return 0;
}