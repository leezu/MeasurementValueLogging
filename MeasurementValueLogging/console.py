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
import devices.si as si
import time
import argparse

def openDevicesFromConsoleArgs(dm):
    """Open devices specified by command line arguments.

    :param dm: DeviceManager
    :type dm: DeviceManager

    """

    parser = argparse.ArgumentParser(description='Messwerterfassung')
    parser.add_argument('port', help="Serial Port (e.g. /dev/ttyUSB0 or COM1)")
    subparser = parser.add_subparsers(dest="device", help="device to use with port")

    validDevices = dm.getValidDevices()
    validDevices.remove("XLS200")

    for i in validDevices:
        subparser.add_parser(i)

    parserXLS200 = subparser.add_parser('XLS200', help="At least one of the sub-arguments must be specified.")

    parserXLS200.add_argument('input1', choices=dm.getValidDevices() + ["None"], help="device to use with input 1")
    parserXLS200.add_argument('input2', choices=dm.getValidDevices() + ["None"], help="device to use with input 2")
    parserXLS200.add_argument('input3', choices=dm.getValidDevices() + ["None"], help="device to use with input 3")

    args = parser.parse_args()

    if args.device == None:
        raise Exception("You have to specify a device")

    deviceIDs = []

    ida = dm.openDevice(args.device, args.port)

    deviceIDs.append(ida)

    if args.device == "XLS200":
        deviceIDs = []
        if args.input1 != "None":
            idb = dm.openSubdevice(args.input1, ida, 1)
            deviceIDs.append(idb)

        if args.input2 != "None":
            idc = dm.openSubdevice(args.input2, ida, 2)
            deviceIDs.append(idc)

        if args.input3 != "None":
            idd = dm.openSubdevice(args.input3, ida, 3)
            deviceIDs.append(idd)

    return deviceIDs


def main():
    """Prints values gathered by the devicemanager to standard output."""
    
    dm = DeviceManager()
    deviceIDs = openDevicesFromConsoleArgs(dm)
    starttime = time.time()

    try:
        while True:
            deviceID, rv = dm.queue.get()
            print(u"{time}: {value} {factor}{unit}".format(
                time=round(time.time() - starttime, 1),
                value=rv.value, factor=rv.prefix, unit=rv.unit)
            )
            
    except KeyboardInterrupt:
        print("Closing")


if __name__ == "__main__":
    main()