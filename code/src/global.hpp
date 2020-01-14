#ifndef GLOBAL
#define GLOBAL
#include <stdio.h>
#include <errno.h>
#include <ctype.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <getopt.h>
#include <sys/param.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <signal.h>
#include <glib-unix.h>

#include <algorithm>
#include <cassert>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <map>
#include <memory>
#include <queue>
#include <string>
#include <vector>


#include <glib.h>
#include <gio/gio.h>

#include <dbus/dbus.h>

#define BT_ADDRESS_STRING_SIZE 18

extern GDBusConnection *con;
extern guint bus_name;
extern guint registration_id;
extern GDBusNodeInfo *introspection_data;
extern std::vector<struct bth_device_info> devices;

#endif