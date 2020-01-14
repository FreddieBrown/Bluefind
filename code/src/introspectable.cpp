#include "bluefind.hpp"

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

/**
 * Method to handle what happens when a method is called over DBus.
 * It takes information about where it has come from and the connection 
 * it has occured over. 
 * 
 * @param connection 
 * @param sender 
 * @param object_path 
 * @param interface_name 
 * @param method_name 
 * @param parameters 
 * @param invocation 
 * @param user_data 
 */

static void
handle_method_call (GDBusConnection       *connection,
                    const gchar           *sender,
                    const gchar           *object_path,
                    const gchar           *interface_name,
                    const gchar           *method_name,
                    GVariant              *parameters,
                    GDBusMethodInvocation *invocation,
                    gpointer               user_data)
{
    return;
}

/**
 * Function to handle calls to get information over DBus
 * 
 * @param connection 
 * @param sender 
 * @param object_path 
 * @param interface_name 
 * @param property_name 
 * @param error 
 * @param user_data 
 * @return GVariant* 
 */
static GVariant *
handle_get_property (GDBusConnection  *connection,
                     const gchar      *sender,
                     const gchar      *object_path,
                     const gchar      *interface_name,
                     const gchar      *property_name,
                     GError          **error,
                     gpointer          user_data)
{
    return (GVariant *) NULL;
}

/**
 * Function to handle Set calls over DBus
 * 
 * @param connection 
 * @param sender 
 * @param object_path 
 * @param interface_name 
 * @param property_name 
 * @param value 
 * @param error 
 * @param user_data 
 * @return gboolean 
 */
static gboolean
handle_set_property (GDBusConnection  *connection,
                     const gchar      *sender,
                     const gchar      *object_path,
                     const gchar      *interface_name,
                     const gchar      *property_name,
                     GVariant         *value,
                     GError          **error,
                     gpointer          user_data)
{
    return (gboolean) NULL;
}