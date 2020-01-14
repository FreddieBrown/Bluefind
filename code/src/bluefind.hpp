#ifndef BLUEFIND
#define BLUEFIND
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
#include <glib-unix.h>

#include <algorithm>
#include <cassert>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <map>
#include <memory>
#include <queue>
#include <string>
#include <vector>


#include <glib.h>
#include <gio/gio.h>

#include <dbus/dbus.h>

#include "discover.hpp"

#define BT_ADDRESS_STRING_SIZE 18

extern GDBusConnection *con;
extern Discover dis;
extern guint bus_name;
extern guint registration_id;
extern GDBusNodeInfo *introspection_data;
extern std::vector<struct bth_device_info> devices;

static const gchar *introspection_xml =
  "<node>"
  "  <interface name='org.bluez.Device1'>"
  "    <annotation name='org.bluez.Annotation' value='OnInterface'/>"
  "    <method name='Pair'/>"
  "    <method name='CancelPairing'/>"
  "    <method name='Connect'/>"
  "    <method name='Disconnect'/>"
  "    <method name='ConnectProfile'/>"
  "      <arg type='s' name='UUID'/>" 
  "    <method name='DisconnectProfile'/>"
  "      <arg type='s' name='UUID'/>"
  "    <property type='ao' name='GattServices' access='read'/>"
  "    <property type='as' name='UUIDs' access='read'/>"
  "    <property type='b' name='Blocked' access='readwrite'/>"
  "    <property type='b' name='Connected' access='read'/>"
  "    <property type='b' name='LegacyPairing' access='read'/>"
  "    <property type='b' name='Paired' access='read'/>"
  "    <property type='b' name='Trusted' access='read'/>"
  "    <property type='{sv}' name='ServiceData' access='read'/>"
  "    <property type='{iv}' name='ManufacturerData' access='read'/>"
  "    <property type='n' name='RSSI' access='read'/>"
  "    <property type='n' name='TxPower' access='read'/>"
  "    <property type='o' name='Adapter' access='read'/>"
  "    <property type='s' name='Address' access='read'/>"
  "    <property type='s' name='Alias' access='readwrite'/>"
  "    <property type='s' name='Icon' access='read'/>"
  "    <property type='s' name='Modalias' access='read'/>"
  "    <property type='s' name='Name' access='read'/>"
  "    <property type='q' name='Appearance' access='read'/>"
  "    <property type='u' name='Class' access='read'/>"
  "  </interface>"
  "  <interface name='org.bluez.Input1'>"
  "    <property type='s' name='ReconnectMode' access='read'/>"
  "  </interface>"
  "</node>";

struct bth_device_info{
    const gchar* address;
    const gchar* alias;
    const gchar* devclass;
};

//bluefind.cpp
static gboolean signalHandler (gpointer data);

// signalSub.cpp
static void new_device(GDBusConnection *sig,
				const gchar *sender_name,
				const gchar *object_path,
				const gchar *interface,
				const gchar *signal_name,
				GVariant *parameters,
				gpointer user_data);

static void device_disappeared(GDBusConnection *sig,
				const gchar *sender_name,
				const gchar *object_path,
				const gchar *interface,
				const gchar *signal_name,
				GVariant *parameters,
				gpointer user_data);

static void signal_adapter_changed(GDBusConnection *conn,
					const gchar *sender,
					const gchar *path,
					const gchar *interface,
					const gchar *signal,
					GVariant *params,
					void *userdata);


// Introspectable.cpp
// Not implemented yet
static void
handle_method_call (GDBusConnection       *connection,
                    const gchar           *sender,
                    const gchar           *object_path,
                    const gchar           *interface_name,
                    const gchar           *method_name,
                    GVariant              *parameters,
                    GDBusMethodInvocation *invocation,
                    gpointer               user_data);

// Not implemented yet
static GVariant *
handle_get_property (GDBusConnection  *connection,
                     const gchar      *sender,
                     const gchar      *object_path,
                     const gchar      *interface_name,
                     const gchar      *property_name,
                     GError          **error,
                     gpointer          user_data);

// Not implemented yet
static gboolean
handle_set_property (GDBusConnection  *connection,
                     const gchar      *sender,
                     const gchar      *object_path,
                     const gchar      *interface_name,
                     const gchar      *property_name,
                     GVariant         *value,
                     GError          **error,
                     gpointer          user_data);


// nameClaim.cpp

static void
on_name_lost(GDBusConnection * connection,
             const gchar * name,
             gpointer user_data);

static void
on_name_acquired (GDBusConnection *connection,
                  const gchar     *name,
                  gpointer         user_data);


static const GDBusInterfaceVTable interface_vtable =
{
  handle_method_call,
  handle_get_property,
  handle_set_property
};

#endif