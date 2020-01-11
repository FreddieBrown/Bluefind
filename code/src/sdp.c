#include "sdp.h"

sdp_session_t *register_service()
{
    uint32_t service_uuid_int[] = { 0, 0, 0, 0xABCD };
    uint8_t rfcomm_channel = 11;
    bdaddr_t interface;
    const char *service_name = "BlueFind";
    const char *service_dsc = "Service to locate people in bad situations";
    const char *service_prov = "Noser Inc.";

    uuid_t root_uuid, l2cap_uuid, rfcomm_uuid, svc_uuid;
    sdp_list_t *l2cap_list = 0, 
               *rfcomm_list = 0,
               *root_list = 0,
               *proto_list = 0, 
               *access_proto_list = 0;
    sdp_data_t *channel = 0;

    bacpy(&interface, BDADDR_ANY);

    printf("Declared variables!\n");

    sdp_record_t *record = sdp_record_alloc();

    printf("Allocated data for record!\n");

    // set the general service ID
    sdp_uuid128_create( &svc_uuid, &service_uuid_int );
    sdp_set_service_id( record, svc_uuid );

    printf("Creating general service ID!\n");

    // make the service record publicly browsable
    sdp_uuid16_create(&root_uuid, PUBLIC_BROWSE_GROUP);
    root_list = sdp_list_append(0, &root_uuid);
    sdp_set_browse_groups( record, root_list );

    printf("Making record publically browsable!\n");

    // set l2cap information
    sdp_uuid16_create(&l2cap_uuid, L2CAP_UUID);
    l2cap_list = sdp_list_append( 0, &l2cap_uuid );
    proto_list = sdp_list_append( 0, l2cap_list );

    printf("Setting L2Cap information!\n");

    // set rfcomm information
    sdp_uuid16_create(&rfcomm_uuid, RFCOMM_UUID);
    channel = sdp_data_alloc(SDP_UINT8, &rfcomm_channel);
    rfcomm_list = sdp_list_append( 0, &rfcomm_uuid );
    sdp_list_append( rfcomm_list, channel );
    sdp_list_append( proto_list, rfcomm_list );

    printf("Setting RFCOMM information!\n");

    // attach protocol information to service record
    access_proto_list = sdp_list_append( 0, proto_list );
    sdp_set_access_protos( record, access_proto_list );

    printf("Attatching protocol information!\n");

    // set the name, provider, and description
    sdp_set_info_attr(record, service_name, service_prov, service_dsc);
    sdp_session_t *session = 0;

    printf("Setting names!\n");

    // connect to the local SDP server, register the service record, and 
    // disconnect
    session = sdp_connect( BDADDR_ANY, BDADDR_LOCAL, SDP_RETRY_IF_BUSY );

    printf("Connecting to local SDP server!\n");

    sdp_device_record_register(session, &interface, &record, SDP_RECORD_PERSIST);

    printf("Registering service!\n");

    // cleanup
    sdp_data_free( channel );
    sdp_list_free( l2cap_list, 0 );
    sdp_list_free( rfcomm_list, 0 );
    sdp_list_free( root_list, 0 );
    sdp_list_free( access_proto_list, 0 );

    printf("Freeing things!\n");

    return session;
}
