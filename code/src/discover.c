#include "bluefind.h"

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