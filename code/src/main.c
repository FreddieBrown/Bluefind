#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include<glib.h>
#include <bluetooth/bluetooth.h>
#include "discover.h"
int main(int argc, char* argv[]){

    printf("This is the project!\n"); 
    discover();   
    return 1;
}
