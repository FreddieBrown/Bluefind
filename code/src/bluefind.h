#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef DISCOVER
#define DISCOVER

#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>
#include <wordexp.h>

#include <glib.h>

#include <gio/gio.h>
// #include <dbus/dbus.h>

#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>

#define COLORED_NEW	COLOR_GREEN "NEW" COLOR_OFF
#define COLORED_CHG	COLOR_YELLOW "CHG" COLOR_OFF
#define COLORED_DEL	COLOR_RED "DEL" COLOR_OFF

void name_appeared(GDBusConnection *connection,
                   const gchar *name,
                   const gchar *name_owner,
                   gpointer user_data);
void name_vanished(GDBusConnection *connection,
                   const gchar *name,
                   gpointer user_data);


#endif