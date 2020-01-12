#include "discover.h"
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
