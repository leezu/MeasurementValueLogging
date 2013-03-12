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

from devices.devicemanager import DeviceManager, DeviceConfig

def main():
    import argparse
    import time

    dm = DeviceManager()

    parser = argparse.ArgumentParser(description='Messwerterfassung')
    parser.add_argument('port', help="Serial Port (e.g. /dev/ttyUSB0 or COM1)")
    subparser = parser.add_subparsers(dest="device", help="device to use with port")

    parserTecpelDMM8061 = subparser.add_parser('TecpelDMM8061')
    parserKernPCB = subparser.add_parser('KernPCB')
    parserBS600 = subparser.add_parser('BS600')
    parserXLS200 = subparser.add_parser('XLS200', help="At least one of the sub-arguments must be specified.")

    parserXLS200.add_argument('input1', choices=dm.getValidDevices() + ["None"], help="device to use with input 1")
    parserXLS200.add_argument('input2', choices=dm.getValidDevices() + ["None"], help="device to use with input 2")
    parserXLS200.add_argument('input3', choices=dm.getValidDevices() + ["None"], help="device to use with input 3")

    args = parser.parse_args()

    if args.device == None:
        raise Exception("You have to specify a device")

    deviceIDs = []

    a = DeviceConfig(args.device, args.port)
    ida = dm.openWithConfig(a)

    deviceIDs.append(ida)

    if args.device == "XLS200":
        deviceIDs = []
        if args.input1 != "None":
            b = DeviceConfig(args.input1, ida, 1)
            idb = dm.openWithConfig(b)
            deviceIDs.append(idb)

        if args.input2 != "None":
            c = DeviceConfig(args.input2, ida, 2)
            idc = dm.openWithConfig(c)
            deviceIDs.append(idc)

        if args.input3 != "None":
            d = DeviceConfig(args.input3, ida, 3)
            idd = dm.openWithConfig(d)
            deviceIDs.append(idd)


    starttime = time.time()

    dm.start()

    try:
        while True:
            import time
            time.sleep(2)
            for i in deviceIDs:
                rv = dm.getLastRawValue(i)
                print(str(round(time.time() - starttime, 1)) + ": " + 
                    str(rv.getDisplayedValue()) + " " + rv.getFactor("prefix") +
                    rv.getUnit())
            
    except KeyboardInterrupt:
        dm.stop()
        print("Closing")


if __name__ == "__main__":
    main()