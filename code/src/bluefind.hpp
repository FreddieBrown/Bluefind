#include "global.hpp"

#include "discover.hpp"

#ifndef BLUEFIND
#define BLUEFIND

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

static gboolean signalHandler (gpointer data);

// Introspectable

static void
handle_method_call (GDBusConnection       *connection,
                    const gchar           *sender,
                    const gchar           *object_path,
                    const gchar           *interface_name,
                    const gchar           *method_name,
                    GVariant              *parameters,
                    GDBusMethodInvocation *invocation,
                    gpointer               user_data);

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

static void on_name_lost(GDBusConnection * connection,
             const gchar * name,
             gpointer user_data);

static void on_name_acquired (GDBusConnection *connection,
                  const gchar     *name,
                  gpointer         user_data);


static const GDBusInterfaceVTable interface_vtable =
{
  handle_method_call,
  handle_get_property,
  handle_set_property
};

// signalSub

extern Discover dis;

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
#endif