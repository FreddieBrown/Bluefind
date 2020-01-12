#include "bluefind.h"
// #include <gio/gio.h>
#include <stdio.h>
#include "gdbus.h"

void connect_handler(DBusConnection *connection, void *user_data)
{
	printf("Connected\n");
}

void disconnect_handler(DBusConnection *connection, void *user_data)
{}

void message_handler(DBusConnection *connection,
					DBusMessage *message, void *user_data)
{}

void proxy_added(GDBusProxy *proxy, void *user_data)
{}

void proxy_removed(GDBusProxy *proxy, void *user_data)
{}

void property_changed(GDBusProxy *proxy, const char *name,
					DBusMessageIter *iter, void *user_data)
{}

void client_ready(GDBusClient *client, void *user_data)
{}


int main(void)
{
    DBusConnection *dbus_conn;
    GDBusClient *client;
	int status;
    dbus_conn = g_dbus_setup_bus(DBUS_BUS_SYSTEM, NULL, NULL);
    g_dbus_attach_object_manager(dbus_conn);

    client = g_dbus_client_new(dbus_conn, "org.bluez", "/org/bluez");

	g_dbus_client_set_connect_watch(client, connect_handler, NULL);
	g_dbus_client_set_disconnect_watch(client, disconnect_handler, NULL);
	g_dbus_client_set_signal_watch(client, message_handler, NULL);

	g_dbus_client_set_proxy_handlers(client, proxy_added, proxy_removed,
							property_changed, NULL);

	g_dbus_client_set_ready_watch(client, client_ready, NULL);
	
	while(1){}

    g_dbus_client_unref(client);

	dbus_connection_unref(dbus_conn);


    

}
