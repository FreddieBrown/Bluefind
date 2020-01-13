#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef DISCOVER
#define DISCOVER

#include <stdio.h>
#include <errno.h>
#include <ctype.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <getopt.h>
#include <sys/param.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <signal.h>


#include <glib.h>
#include <gio/gio.h>

#include <dbus/dbus.h>

#define BT_ADDRESS_STRING_SIZE 18

GDBusConnection *con;

void property_value(const gchar *key, GVariant *value);
typedef void (*method_cb_t)(GObject *, GAsyncResult *, gpointer);
int hci0_call_method(const char* api, const char *method, GVariant *param, method_cb_t method_cb);
void get_discovery_filter_cb(GObject *con,
					  GAsyncResult *res,
					  gpointer data);
void new_device(GDBusConnection *sig,
				const gchar *sender_name,
				const gchar *object_path,
				const gchar *interface,
				const gchar *signal_name,
				GVariant *parameters,
				gpointer user_data);
void device_disappeared(GDBusConnection *sig,
				const gchar *sender_name,
				const gchar *object_path,
				const gchar *interface,
				const gchar *signal_name,
				GVariant *parameters,
				gpointer user_data);
void signal_adapter_changed(GDBusConnection *conn,
					const gchar *sender,
					const gchar *path,
					const gchar *interface,
					const gchar *signal,
					GVariant *params,
					void *userdata);
int adapter_set_property(const char *prop, GVariant *value);
GVariant* adapter_get_property(const char *prop);
int set_discovery_filter(char **argv);
void sigHandler(int sig);



#endif
