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
#include <time.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <bluetooth/bluetooth.h>
#include <glib.h>
#include <gio.h>

#include <dbus/dbus.h>

#define COLORED_NEW	COLOR_GREEN "NEW" COLOR_OFF
#define COLORED_CHG	COLOR_YELLOW "CHG" COLOR_OFF
#define COLORED_DEL	COLOR_RED "DEL" COLOR_OFF

const u_char LE_ADV_REPORT = 0x02;

void scan(unsigned timeout);

void receiveAdv(int dd, unsigned timeout);


#endif