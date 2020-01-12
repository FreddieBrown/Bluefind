#include "bluefind.h"

void set_discovery_filter_reply(DBusMessage *message, void *user_data)
{
	DBusError error;

	dbus_error_init(&error);
	if (dbus_set_error_from_message(&error, message) == TRUE) {
		printf("SetDiscovery filter failed\n");
	}

	filter.set = true;

    printf("SetDiscovery filer success")
}

void clear_discovery_filter(DBusMessageIter *iter, void *user_data)
{
	DBusMessageIter dict;

	dbus_message_iter_open_container(iter, DBUS_TYPE_ARRAY,
				DBUS_DICT_ENTRY_BEGIN_CHAR_AS_STRING
				DBUS_TYPE_STRING_AS_STRING
				DBUS_TYPE_VARIANT_AS_STRING
				DBUS_DICT_ENTRY_END_CHAR_AS_STRING, &dict);

	dbus_message_iter_close_container(iter, &dict);
}

void set_discovery_filter_setup(DBusMessageIter *iter, void *user_data)
{
	struct set_discovery_filter_args *args = user_data;
	DBusMessageIter dict;

	dbus_message_iter_open_container(iter, DBUS_TYPE_ARRAY,
				DBUS_DICT_ENTRY_BEGIN_CHAR_AS_STRING
				DBUS_TYPE_STRING_AS_STRING
				DBUS_TYPE_VARIANT_AS_STRING
				DBUS_DICT_ENTRY_END_CHAR_AS_STRING, &dict);

	g_dbus_dict_append_array(&dict, "UUIDs", DBUS_TYPE_STRING,
							&args->uuids,
							args->uuids_len);

	if (args->pathloss != DISTANCE_VAL_INVALID)
		g_dbus_dict_append_entry(&dict, "Pathloss", DBUS_TYPE_UINT16,
						&args->pathloss);

	if (args->rssi != DISTANCE_VAL_INVALID)
		g_dbus_dict_append_entry(&dict, "RSSI", DBUS_TYPE_INT16,
						&args->rssi);

	if (args->transport != NULL)
		g_dbus_dict_append_entry(&dict, "Transport", DBUS_TYPE_STRING,
						&args->transport);

	if (args->duplicate)
		g_dbus_dict_append_entry(&dict, "DuplicateData",
						DBUS_TYPE_BOOLEAN,
						&args->duplicate);

	if (args->discoverable)
		g_dbus_dict_append_entry(&dict, "Discoverable",
						DBUS_TYPE_BOOLEAN,
						&args->discoverable);

	dbus_message_iter_close_container(iter, &dict);
}

void start_discovery_reply(DBusMessage *message, void *user_data)
{
	dbus_bool_t enable = GPOINTER_TO_UINT(user_data);
	DBusError error;

	dbus_error_init(&error);

	if (dbus_set_error_from_message(&error, message) == TRUE) {
		printf("Failed to start discovery\n");

	}

	printf("Discovery Enabled\n");

	filter.active = enable;
	/* Leave the discovery running even on noninteractive mode */
}

void set_discovery_filter(bool cleared)
{
	GDBusSetupFunction func;

	func = cleared ? clear_discovery_filter : set_discovery_filter_setup;

	if (g_dbus_proxy_method_call(default_ctrl->proxy, "SetDiscoveryFilter",
					func, set_discovery_filter_reply,
					&filter, NULL) == FALSE) {
		return bt_shell_noninteractive_quit(EXIT_FAILURE);
	}

	filter.set = true;
}


void scan(int argc, char *argv[]){
    dbus_bool_t enable = TRUE;
	const char *method;

    set_discovery_filter(false);
	method = "StartDiscovery";

    if (g_dbus_proxy_method_call(default_ctrl->proxy, method,
				NULL, start_discovery_reply,
				GUINT_TO_POINTER(enable), NULL) == FALSE) {
		printf("Failed to start discovery\n");
	}

}