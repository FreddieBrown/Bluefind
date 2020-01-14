#ifndef NAME
#define NAME

#include "global.hpp"

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