import bluepy
from bluepy.btle import Scanner, UUID, Peripheral, DefaultDelegate

address = 'DC:A6:32:26:CE:70'
scanner = Scanner()
devices = scanner.scan(5.0)
for dev in devices:
    print("Scan Data: {}".format(dev.getScanData()))
