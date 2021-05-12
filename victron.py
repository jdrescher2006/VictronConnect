#!/usr/bin/python3

import gatt
import time
import threading
from datetime import datetime, timedelta

#  Set to your BT-dongles MAC-address
mac_address = "ec:32:8d:c1:65:96"

device_manager = gatt.DeviceManager(adapter_name="hci0")
device_manager.update_devices() #don't know about this, is it really needed?

charactersistcs = {}

class VictronDevice(gatt.Device):
    def __init__(self, mac_address, manager):
        super().__init__(mac_address=mac_address, manager=manager)
        self.last_notify = datetime.now() + timedelta(seconds=10)
        self.char_buffer = {}

    def connect_succeeded(self):
        print("Connected!")
        time.sleep(10)
        device.disconnect()

    def connect_failed(self, error):        
        print("Connection failed: %s" % (str(error)))

    def disconnect_succeeded(self):
        print("Disconnected!")
        self.manager.stop()

    def characteristic_enable_notifications_succeeded(self, characteristic,):
        print("[{}] Notifications enabled...".format(characteristic.uuid))

    def characteristic_enable_notifications_failed(self, characteristic, error):
        print("[{}] Notifications not enabled {}".format(characteristic.uuid, error))


    def characteristic_value_updated(self, characteristic, value):
        self.last_notify = datetime.now() 
        if characteristic.uuid == "306b0004-b081-4037-83dc-e59fcc3cdfd0":
            print("[{}] Changed to {}".format(characteristic.uuid, value))
            self.getBulkValue(characteristic.uuid, value)
        elif characteristic.uuid == "306b0003-b081-4037-83dc-e59fcc3cdfd0":
            pass
        else:
            print("[{}] Changed to {}".format(characteristic.uuid, value))
            self.getValue(characteristic.uuid, value)
        

    def getBulkValue(self, char, value):
        print("getBulkValue: ", value)
        start = int.from_bytes(value[0:2], byteorder="little")
        if start == 776:
            self.char_buffer[char] = value
        else:
            self.char_buffer[char] = self.char_buffer[char] + value[:]
        if len(self.char_buffer[char]) > 20:
            i = 0
            while i + 8 <= len(self.char_buffer[char]):
                val = self.char_buffer[char][i:i+8]
                self.getValue(char, val)
                i = i + 8

#   08 03 19 22 00 42 dc 59 
#   08 03 19 22 00 42 d9 59 
#   08 03 19 22 00 42 dc 59 
#   08 03 19 ed 8d 42 35 05 
#   08 03 19 ed 8d 42 34 05                                      


    def getValue(self, char, value):
        print("getValue: ", value)
        if len(value) == 8:
            packet3 = value[3]
            packet4 = value[4]
            packet6 = value[6]
            packet7 = value[7]
            ptype = int.from_bytes(value[3:5], byteorder="little")
            pval  = int.from_bytes(value[6:8], byteorder="little")
            if ptype == 34:
                print("Output voltage: {} V".format(pval * 0.01))
            elif ptype == 36333:
                print("Input voltage: {} V".format(pval * 0.01))
            elif ptype == 290:
                if pval == 0:
                    print("Output Power turned off")
                elif pval == 65534:
                    print("Output Power turned on")
                else:
                    print("Current: {} A".format(pval * 0.1))
            else:
                print("?? {}: {}".format(ptype, pval))
                print("P3 {}, P4 {}, P6 {}, P7 {}".format(packet3, packet4, packet6, packet7))
        if len(value) == 7:
            # Probably power?
            # 08 03 19 02 00 41 05 
            ptype = int(str(value[4]), 16)
            pval  = int(str(value[6]), 16)
            state = "?"
            if ptype == 0:
                if pval == 2:
                    state = "on"
                if pval == 4:
                    state = "off"
                if pval == 5:
                    state = "eco"
                print("PowerSwitch - {} Type: {} Value {}".format(state, ptype, pval))
            if ptype == 1:
                if pval == 0:
                    state = "off"
                if pval == 1:
                    state = "eco"
                if pval == 9:
                    state = "on"
                print("PowerState - {} Type: {} Value {}".format(state, ptype, pval))
            # if packet3 == 34 and packet4 == 0

device = VictronDevice(mac_address=mac_address, manager=device_manager)

device.connect()
time.sleep(5)   #why this sleep?
device_manager.run()
