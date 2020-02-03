from gattlib import DiscoveryService, GATTRequester, GATTResponse

#service = DiscoveryService("hci0")
#devices = service.discover(60)

#for address, name in devices.items():
#    print("name: {}, address: {}".format(name, address))

req = GATTRequester("B8:27:EB:E7:B4:70")
#req.connect(False)

response = GATTResponse()
req.read_by_handle_async(0xFFF1, response)
while not response.received():
    time.sleep(0.1)

print(response.received()[0])

req.write_cmd(0xFFF1, bytes([16, 1, 4]))
