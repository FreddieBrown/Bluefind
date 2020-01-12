#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include<glib.h>
#include <bluetooth/bluetooth.h>
#include "discover.h"
int main(int argc, char* argv[]){

    printf("This is the project!\n"); 
    if(argc > 1 && strcmp(argv[1],"--le")  == 0){
        discover_le();
    }
    else{
        discover();
    }   
    return 1;
}
