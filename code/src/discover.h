#ifndef DISCOVER
#define DISCOVER

#include <stdio.h>
#include <errno.h>
#include <ctype.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include <sys/param.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <signal.h>

#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>

#define FLAGS_AD_TYPE 0x01
#define FLAGS_LIMITED_MODE_BIT 0x01
#define FLAGS_GENERAL_MODE_BIT 0x02
#define EIR_NAME_SHORT              0x08  /* shortened local name */
#define EIR_NAME_COMPLETE           0x09

int discover();
int discover_le();
int check_report_filter(uint8_t procedure, le_advertising_info *info);
void eir_parse_name(uint8_t *eir, size_t eir_len,
						char *buf, size_t buf_len);
int read_flags(uint8_t *flags, const uint8_t *data, size_t size);

#endif