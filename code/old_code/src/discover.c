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
    return 0;
}