#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef DISCOVER
#define DISCOVER

#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>
#include <wordexp.h>

#include <glib.h>
#include "gdbus.h"

#include <dbus/dbus.h>

#define COLORED_NEW	COLOR_GREEN "NEW" COLOR_OFF
#define COLORED_CHG	COLOR_YELLOW "CHG" COLOR_OFF
#define COLORED_DEL	COLOR_RED "DEL" COLOR_OFF
#define	DISTANCE_VAL_INVALID	0x7FFF

struct adapter {
	GDBusProxy *proxy;
	GDBusProxy *ad_proxy;
	GList *devices;
};

struct adapter *default_ctrl;

void scan(int argc, char *argv[]);


#endif