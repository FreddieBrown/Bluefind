#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include "discover.h"
int main(int argc, char* argv[]){

    printf("This is the project!\n"); 
    if(argc > 1 && strcmp(argv[1],"--le")  == 0){
        discover_le();
    }
    else{
        sdp_session_t *session = register_service();
        sleep(5);
        sdp_close(session);
        discover();
    }   
    return 1;
}
