#include "discover.h"


void name_appeared(GDBusConnection *connection,
                   const gchar *name,
                   const gchar *name_owner,
                   gpointer user_data)
{
    printf("Name appeared: %s\n", name);
    printf("Owned by: %s\n", name_owner);
}

void name_vanished(GDBusConnection *connection,
                   const gchar *name,
                   gpointer user_data)
{
    printf("Name vanished: %s\n", name);
}