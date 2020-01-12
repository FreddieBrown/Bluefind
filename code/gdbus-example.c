#include <stdio.h>
#include <gio/gio.h>

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

int main(void)
{
    GMainLoop *loop;
    GError *error;
    guint name;

    loop = g_main_loop_new(NULL, FALSE);
    name = g_bus_watch_name(G_BUS_TYPE_SYSTEM,
                            "org.bluez", // 
                            G_BUS_NAME_WATCHER_FLAGS_NONE,
                            name_appeared,
                            name_vanished,
                            NULL,
                            NULL);

    g_main_loop_run(loop);
}