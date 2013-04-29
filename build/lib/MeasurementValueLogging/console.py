# -*- coding: utf-8 -*-

# Python Measurement Value Logging Software.
# Console interface
# 
# Copyright (C) 2013  Leonard Lausen <leonard@lausen.nl>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module contains a console interface."""

from devices.devicemanager import DeviceManager
import time
import argparse

def openDevicesFromConsoleArgs(devicemanager):
    parser = argparse.ArgumentParser(description='Messwerterfassung')
    parser.add_argument('port', help="Serial Port (e.g. /dev/ttyUSB0 or COM1)")
    subparser = parser.add_subparsers(dest="device", help="device to use with port")

    parserTecpelDMM8061 = subparser.add_parser('TecpelDMM8061')
    parserKernPCB = subparser.add_parser('KernPCB')
    parserBS600 = subparser.add_parser('BS600')
    parserXLS200 = subparser.add_parser('XLS200', help="At least one of the sub-arguments must be specified.")

    parserXLS200.add_argument('input1', choices=devicemanager.getValidDevices() + ["None"], help="device to use with input 1")
    parserXLS200.add_argument('input2', choices=devicemanager.getValidDevices() + ["None"], help="device to use with input 2")
    parserXLS200.add_argument('input3', choices=devicemanager.getValidDevices() + ["None"], help="device to use with input 3")

    args = parser.parse_args()

    if args.device == None:
        raise Exception("You have to specify a device")

    deviceIDs = []

    ida = devicemanager.openDevice(args.device, args.port)

    deviceIDs.append(ida)

    if args.device == "XLS200":
        deviceIDs = []
        if args.input1 != "None":
            idb = devicemanager.openSubdevice(args.input1, ida, 1)
            deviceIDs.append(idb)

        if args.input2 != "None":
            idc = devicemanager.openSubdevice(args.input2, ida, 2)
            deviceIDs.append(idc)

        if args.input3 != "None":
            idd = devicemanager.openSubdevice(args.input3, ida, 3)
            deviceIDs.append(idd)

    return deviceIDs


def main():
    dm = DeviceManager()
    deviceIDs = openDevicesFromConsoleArgs(dm)
    starttime = time.time()

    try:
        while True:
            time.sleep(2)
            for i in deviceIDs:
                rv = dm.getLastRawValue(i)
                print(str(round(time.time() - starttime, 1)) + ": " + 
                    str(rv.getDisplayedValue()) + " " + rv.getFactor("prefix") +
                    rv.getUnit())
            
    except KeyboardInterrupt:
        print("Closing")


if __name__ == "__main__":
    main()