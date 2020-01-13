#include "bluefind.hpp"

#ifndef DISCOVER
#define DISCOVER
typedef void (*method_cb_t)(GObject *, GAsyncResult *, gpointer);

static void get_discovery_filter_cb(GObject *con,
                            GAsyncResult *res,
                            gpointer data);

class Discover{
    public:
        gchar* property_value(const gchar *key, GVariant *value);
        int hci0_call_method(const char* api, const char *method, GVariant *param, method_cb_t method_cb);
        int adapter_set_property(const char *prop, GVariant *value);
        GVariant* adapter_get_property(const char *prop);
        int set_discovery_filter(char **argv);
};

#endif