#ifndef DISCOVER
#define DISCOVER

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/uuid.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>

int discover();

#endif