#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

from Foundation import *
from PyObjCTools import AppHelper


wx2_service = CBUUID.UUIDWithString_(u'0C4C3000-7700-46F4-AA96-D5E974E32A54')
wx2_characteristic_data = CBUUID.UUIDWithString_(u'0C4C3001-7700-46F4-AA96-D5E974E32A54')

CoreBluetooth = NSBundle.bundleWithIdentifier_('com.apple.CoreBluetooth')
_ = CoreBluetooth.load()

constants = [
             ('CBCentralManagerScanOptionAllowDuplicatesKey', '@'),
             ('CBAdvertisementDataManufacturerDataKey', '@'),
             ('CBAdvertisementDataServiceUUIDsKey', '@'),
            ]

objc.loadBundleVariables(CoreBluetooth, globals(), constants)


Login = NSBundle.bundleWithPath_(
    '/System/Library/PrivateFrameworks/login.framework')
functions = [
             ('SACLockScreenImmediate', '@'),
            ]

objc.loadBundleFunctions(Login, globals(), functions)



class BleClass(object):

    def centralManagerDidUpdateState_(self, manager):
        self.manager = manager
        manager.scanForPeripheralsWithServices_options_(None,None)

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        self.peripheral = peripheral
        if peripheral.name() != 'Tile':
            return
        print 'DeviceName' + repr(peripheral.UUID)
        if "CC112152-37E5-4FE8-8A4C-B858AE1883A8" in repr(peripheral.UUID):
            print "pairing..."
            print "data: " + repr(data)
            ad_data = data.get(CBAdvertisementDataManufacturerDataKey, None)
            if ad_data != None:
                companyIDRange = NSMakeRange(0,2);
                companyIdentifier = ad_data.getBytes_range_(None, companyIDRange)
                if (ord(companyIdentifier[0]) == 0x4C):
                    # print "1. got compIdentifier 0x4C"
                    dataTypeRange = NSMakeRange(2,1);
                    dataType = ad_data.getBytes_range_(None, dataTypeRange)
                    if (ord(dataType) == 0x02):
                        # print "2. got dataType 0x02"
                        dataLengthRange = NSMakeRange(3,1);
                        dataLength = ad_data.getBytes_range_(None, dataLengthRange)
                        #print "dataLength: %s" % ord(dataLength)
                        if (ord(dataLength) == 0x15):
                            # print "3. got dataLength 0x15"
                            uuidRange = NSMakeRange(4, 16)
                            ad_bytes = ad_data.getBytes_range_(None, uuidRange)
                            # print ad_bytes
                            proximityUUID = NSUUID.alloc().initWithUUIDBytes_(
                                ad_bytes)
                            print "proximityUUID: %s" % proximityUUID
                            # ^ uncomment this one to see beacons when you trigger them
                            #if str(proximityUUID) in approved_UUIDs:
                            if str(proximityUUID):
                                # Tile is in beacon mode; ie the button was
                                # double-clicked
                                print "You clicked it.\n"

            manager.connectPeripheral_options_(peripheral, None)
            manager.stopScan()
            #SACLockScreenImmediate()

    def centralManager_didConnectPeripheral_(self, manager, peripheral):
        print "connected " + repr(peripheral.UUID())
        # SACLockScreenImmediate()
        self.peripheral.discoverServices_([wx2_service])

    def peripheral_didUpdateValueForCharacteristic_error_(self, peripheral, characteristic, error):
        print repr(characteristic.value().bytes().tobytes())



if "__main__" == __name__:
    central_manager = CBCentralManager.alloc()
    central_manager.initWithDelegate_queue_options_(BleClass(), None, None)
    AppHelper.runConsoleEventLoop()
