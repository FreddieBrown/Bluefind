#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include<glib.h>
#include <bluetooth/bluetooth.h>
#include "discover.h"
int main(){

    printf("This is the project!\n"); 
    discover(); 
    GDBusClient gdbc;  
    return 1;
}
