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
#include <getopt.h>
#include <sys/param.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <signal.h>


#include <glib.h>
#include <gio/gio.h>

#include <dbus/dbus.h>

#define COLORED_NEW	COLOR_GREEN "NEW" COLOR_OFF
#define COLORED_CHG	COLOR_YELLOW "CHG" COLOR_OFF
#define COLORED_DEL	COLOR_RED "DEL" COLOR_OFF

GDBusConnection *con;

void bluez_property_value(const gchar *key, GVariant *value);
typedef void (*method_cb_t)(GObject *, GAsyncResult *, gpointer);
int bluez_adapter_call_method(const char *method, GVariant *param, method_cb_t method_cb);
void bluez_get_discovery_filter_cb(GObject *con,
					  GAsyncResult *res,
					  gpointer data);
void bluez_device_appeared(GDBusConnection *sig,
				const gchar *sender_name,
				const gchar *object_path,
				const gchar *interface,
				const gchar *signal_name,
				GVariant *parameters,
				gpointer user_data);
void bluez_device_disappeared(GDBusConnection *sig,
				const gchar *sender_name,
				const gchar *object_path,
				const gchar *interface,
				const gchar *signal_name,
				GVariant *parameters,
				gpointer user_data);
void bluez_signal_adapter_changed(GDBusConnection *conn,
					const gchar *sender,
					const gchar *path,
					const gchar *interface,
					const gchar *signal,
					GVariant *params,
					void *userdata);
int bluez_adapter_set_property(const char *prop, GVariant *value);
int bluez_set_discovery_filter(char **argv);



#endif
