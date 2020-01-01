#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include "discover.h"
int main(void){

    printf("This is the project!\n"); 
    discover();   
    return 1;
}
