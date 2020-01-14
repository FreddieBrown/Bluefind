#include "nameClaim.hpp"

guint registration_id;
/**
 * This functions deals with the consequences of not acquiring the 
 * name on the Bus.
 * 
 * @param connection 
 * @param name 
 * @param user_data 
 */
static void on_name_lost(GDBusConnection * connection,
             const gchar * name,
             gpointer user_data)
{
    exit(1);
}

/**
 * This functions deals with what happens when the name is 
 * claimed on the Bus. This sets up the introspectable data 
 * for other devices to interface with. 
 * 
 * @param connection 
 * @param name 
 * @param user_data 
 */
static void on_name_acquired (GDBusConnection *connection,
                  const gchar     *name,
                  gpointer         user_data)
{
    // Need to register the introspection data using the connection 
    // using g_dbus_connection_register_object
    // Before this, need to create a GDBusInterfaceVTable containing the 
    // functions for the interface.
    registration_id = g_dbus_connection_register_object (connection,
                                                       "/org/bluez/TestDevice",
                                                       introspection_data->interfaces[0],
                                                       &interface_vtable,
                                                       NULL,  /* user_data */
                                                       NULL,  /* user_data_free_func */
                                                       NULL); /* GError** */
}