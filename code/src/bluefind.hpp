#ifndef BLUEFIND
#define BLUEFIND
#include "global.hpp"

#include "discover.hpp"
#include "introspectable.hpp"
#include "signalSub.hpp"

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
#endif