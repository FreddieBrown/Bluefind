from gattlib import DiscoveryService, GATTRequester, GATTResponse
import time

#service = DiscoveryService("hci0")
#devices = service.discover(60)

#for address, name in devices.items():
#    print("name: {}, address: {}".format(name, address))

req = GATTRequester("DC:A6:32:26:CE:70")
#req.connect(False)

response = GATTResponse()
req.read_by_uuid_async('0000FFF1-0000-1000-8000-00805f9b34fb', response)
while not response.received():
    time.sleep(0.1)

print(response.received()[0])
for i in range(0, 256):
    req.write_cmd(i, str(bytearray([4])))
