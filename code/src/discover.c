#include "bluefind.h"

// void scan(int timeout){
//     int devId = hci_get_route(nullptr);
//     int dd = hci_open_dev(devId);
//     if (devId < 0 || dd < 0) {
//         printf("Couldn't open device\n");
//         return;
//     }

//     uint8_t localAddr = LE_PUBLIC_ADDRESS; //LE_PUBLIC_ADDRESS to use public on local device, LE_RANDOM_ADDRESS to use random
//     uint8_t scanType = 0x01; //0x01 = active, 0x00 = passive
//     uint8_t filterPolicy = 0x00; //0x00 = don't use whitelist, 0x01 = use whitelist
//     uint16_t interval = htobs(0x0010); //no idea, default for all except 'g' or 'l' filters that use htobs(0x0012)
//     uint16_t window = htobs(0x0010); //no idea, default for all except 'g' or 'l' filters that use htobs(0x0012)
//     uint8_t filterDup = 0x00; // 0x01 = filter duplicates, 0x00 = receive duplicates
//     int hciTimeout = 10000; // this is timeout for communication with the local adapter, not scanning

//     if (hci_le_set_scan_parameters(dd, scanType, interval, window, localAddr, filterPolicy, hciTimeout) < 0) {
//         printf("Set scan parameters failed\n");
//         hci_close_dev(dd);
//         return;
//     }

//     uint8_t scanEnable = 0x01;
//     if (hci_le_set_scan_enable(dd, scanEnable, filterDup, hciTimeout) < 0) {
//         printf("Enable scan failed\n");
//         hci_close_dev(dd);
//         return;
//     }

//     if (receiveAdv(dd, timeout) < 0) {
//         printf("Could not receive advertising events\n");
//         hci_close_dev(dd);
//         return;
//     }

//     hci_close_dev(dd);
//     return;
// }

// void receiveAdv(int dd, int timeout)
// {
//     u_char buff[HCI_MAX_EVENT_SIZE];
//     u_char *ptr;
//     hci_filter filter;
 
//     hci_filter_clear(&filter);
//     hci_filter_set_ptype(HCI_EVENT_PKT, &filter);
//     hci_filter_set_event(EVT_LE_META_EVENT, &filter);
 
//     if (setsockopt(dd, SOL_HCI, HCI_FILTER, &filter, sizeof(filter)) < 0) {
//         printf("Could not set socket options\n");
//         return false;
//     }

//     time_t endwait;
//     time_t start = time(NULL);
//     time_t seconds = timeout;

//     endwait = start + seconds;

//     while (start < endwait) {
//         if (read(dd, buff, sizeof(buff)) < 0) {
//             sleep(0.2);
//             continue;
//         }
 
//         ptr = buff + (1 + HCI_EVENT_HDR_SIZE);
//         evt_le_meta_event *meta = reinterpret_cast<evt_le_meta_event *>(ptr);
 
//         if (meta->subevent != LE_ADV_REPORT)
//             continue;
 
//         le_advertising_info *info = reinterpret_cast<le_advertising_info *>(meta->data + 1);
//         char addr[18];
//         ba2str(&info->bdaddr, addr);
//         int rssi = info->data[info->length]; //intentional, isn't out of bounds
//         printf("Detected device: %s, %i\n"addr,rssi);

//         start = time(NULL);
//     }
 
//     return true;
// }

/**
 * @brief Inspects Bluetooth devices which are open for connection 
 * and gets their information and prints it. 
 * 
 * @return int 
 */
int scan(){
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