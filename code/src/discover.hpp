#include "bluefind.hpp"

#ifndef DISCOVER
#define DISCOVER
typedef void (*method_cb_t)(GObject *, GAsyncResult *, gpointer);

class Discover{
    public:
        void property_value(const gchar *key, GVariant *value);
        int hci0_call_method(const char* api, const char *method, GVariant *param, method_cb_t method_cb);
        int adapter_set_property(const char *prop, GVariant *value);
        GVariant* adapter_get_property(const char *prop);
        int set_discovery_filter(char **argv);
};

#endif