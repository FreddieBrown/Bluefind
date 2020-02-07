import bluepy
from bluepy.btle import Scanner, UUID, Peripheral, DefaultDelegate

address = 'DC:A6:32:26:CE:70'
SERVICE_UUID =  '0000FFF0-0000-1000-8000-00805f9b34fb'
RW_UUID = '0000FFF1-0000-1000-8000-00805f9b34fb'
scanner = Scanner()
devices = scanner.scan(5.0)
for dev in devices:
    print("Scan Data: {}".format(dev.getScanData()))
peri = Peripheral(address)
svc = peri.getServiceByUUID( SERVICE_UUID )
ch = svc.getCharacteristics( RW_UUID )[0]
print("READ: {}".format(ch.read()))
