#include "bluefind.h"
// #include <gio/gio.h>
#include <stdio.h>
#include "gdbus.h"

// void bus_watch_loop(){
//     GMainLoop *loop;
//     GError *error;
//     guint name;

//     loop = g_main_loop_new(NULL, FALSE);
//     name = g_bus_watch_name(G_BUS_TYPE_SYSTEM,
//                             "org.bluez", // 
//                             G_BUS_NAME_WATCHER_FLAGS_NONE,
//                             name_appeared,
//                             name_vanished,
//                             NULL,
//                             NULL);

//     g_main_loop_run(loop);
// }

void connect_handler(DBusConnection *connection, void *user_data)
{}

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
    // bus_watch_loop();
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

    g_dbus_client_unref(client);

	dbus_connection_unref(dbus_conn);


    

}
