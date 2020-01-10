#include "discover.h"

/**
 * @brief Inspects Bluetooth devices which are open for connection 
 * and gets their information and prints it. 
 * 
 * @return int 
 */
int discover(){
    inquiry_info* devices = NULL;
    int adapter_id, sock, num_rsp, i;
    int len = 8;
    int max_rsp = 255;
    int flags = IREQ_CACHE_FLUSH;
    char addr[19] = {0};
    char name[248] = {0};
    struct hci_dev_info di;
    adapter_id = hci_get_route(NULL);

    if (hci_devinfo(adapter_id, &di) < 0) {
		perror("Can't get device info");
		exit(1);
	}

    
    if(adapter_id < 0) {
        perror("opening socket");
        exit(1);
    }
    
    devices = (inquiry_info*) malloc(max_rsp * sizeof(inquiry_info));

    printf("Scanning ...\n");
    num_rsp = hci_inquiry(adapter_id, len, max_rsp, NULL, &devices, flags);
    while(1){
        num_rsp = hci_inquiry(adapter_id, len, max_rsp, NULL, &devices, flags);
        if(num_rsp < 0){
            perror("hci_inquiry");
        }

        sock = hci_open_dev(adapter_id);
        if (sock < 0) {
            perror("HCI device open failed");
            free(devices);
            exit(1);
        }

        for(i=0; i < num_rsp; i++) {
            printf("Looking at device\n");
            ba2str(&(devices+i)->bdaddr, addr);
            memset(name, 0, sizeof(name));
            if(0 != hci_read_remote_name(sock, &(devices+i)->bdaddr, sizeof(name), name, 0)){
                strcpy(name, "[unknown]");            
            }
            printf("%s %s\n", addr, name);
        }
    }
    free(devices);
    close(sock);
    return 0;
}

/**
 * @brief Does very similar things as @see discover , except for it works for LE devices.
 * 
 * @return int 
 */
int discover_le(){
    int err, dd, dev_id;
	uint8_t own_type = LE_PUBLIC_ADDRESS;
	uint8_t scan_type = 0x01;
	uint8_t filter_type = 0;
	uint8_t filter_policy = 0x00;
	uint16_t interval = htobs(0x0010);
	uint16_t window = htobs(0x0010);
	uint8_t filter_dup = 0x01;
    unsigned char buf[HCI_MAX_EVENT_SIZE], *ptr;
	struct hci_filter nf, of;
	socklen_t olen;
	int len;

    dev_id = hci_get_route(NULL);
    dd = hci_open_dev(dev_id);

    if (dd < 0) {
		perror("Can't get device info");
		exit(1);
	}

    err = hci_le_set_scan_parameters(dd, scan_type, interval, window, own_type, filter_policy, 10000);
    if (err < 0) {
		perror("Set scan parameters failed");
		exit(1);
	}

    err = hci_le_set_scan_enable(dd, 0x01, filter_dup, 10000);
	if (err < 0) {
		perror("Enable scan failed");
		exit(1);
	}

    printf("LE Scan ...\n");

    olen = sizeof(of);
    // Get options for socket
	if (getsockopt(dd, SOL_HCI, HCI_FILTER, &of, &olen) < 0) {
		printf("Could not get socket options\n");
		return -1;
	}
    // 
    hci_filter_clear(&nf);
	hci_filter_set_ptype(HCI_EVENT_PKT, &nf);
	hci_filter_set_event(EVT_LE_META_EVENT, &nf);

    if (setsockopt(dd, SOL_HCI, HCI_FILTER, &nf, sizeof(nf)) < 0) {
		printf("Could not set socket options\n");
		return -1;
	}
    while (1) {
		evt_le_meta_event *meta;
		le_advertising_info *info;
		char addr[18];

		while ((len = read(dd, buf, sizeof(buf))) < 0) {
			if (errno == EINTR) {
				len = 0;
				goto done;
			}

			if (errno == EAGAIN || errno == EINTR)
				continue;
			goto done;
		}

		ptr = buf + (1 + HCI_EVENT_HDR_SIZE);
		len -= (1 + HCI_EVENT_HDR_SIZE);

		meta = (void *) ptr;

		if (meta->subevent != 0x02)
			goto done;

		/* Ignoring multiple reports */
		info = (le_advertising_info *) (meta->data + 1);
		if (check_report_filter(filter_type, info)) {
			char name[30];

			memset(name, 0, sizeof(name));

			ba2str(&info->bdaddr, addr);
			eir_parse_name(info->data, info->length,
							name, sizeof(name) - 1);

			printf("%s %s\n", addr, name);
		}
	}

done:
	setsockopt(dd, SOL_HCI, HCI_FILTER, &of, sizeof(of));

    err = hci_le_set_scan_enable(dd, 0x00, filter_dup, 10000);
	if (err < 0) {
		perror("Disable scan failed");
		exit(1);
	}
    hci_close_dev(dd);
	return 0;
}

int check_report_filter(uint8_t procedure, le_advertising_info *info)
{
	uint8_t flags;

	/* If no discovery procedure is set, all reports are treat as valid */
	if (procedure == 0)
		return 1;

	/* Read flags AD type value from the advertising report if it exists */
	if (read_flags(&flags, info->data, info->length))
		return 0;

	switch (procedure) {
	case 'l': /* Limited Discovery Procedure */
		if (flags & FLAGS_LIMITED_MODE_BIT)
			return 1;
		break;
	case 'g': /* General Discovery Procedure */
		if (flags & (FLAGS_LIMITED_MODE_BIT | FLAGS_GENERAL_MODE_BIT))
			return 1;
		break;
	default:
		fprintf(stderr, "Unknown discovery procedure\n");
	}

	return 0;
}
