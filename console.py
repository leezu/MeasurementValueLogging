# -*- coding: utf-8 -*-

from devices import TecpelDMM8061, XLS200, KernPCB

def main():
    import argparse
    import time

    parser = argparse.ArgumentParser(description='Messwerterfassung')
    parser.add_argument('port', help="Serial Port (e.g. /dev/ttyUSB0 or COM1)")
    subparser = parser.add_subparsers(dest="device", help="device to use with port")

    parserTecpelDMM8061 = subparser.add_parser('TecpelDMM8061')
    parserKernPCB = subparser.add_parser('KernPCB')
    parserXLS200 = subparser.add_parser('XLS200', help="At least one of the sub-arguments must be specified.")

    parserXLS200.add_argument('input1', choices=["TecpelDMM8061", "KernPCB", "None"], help="device to use with input 1")
    parserXLS200.add_argument('input2', choices=["TecpelDMM8061", "KernPCB", "None"], help="device to use with input 2")
    parserXLS200.add_argument('input3', choices=["TecpelDMM8061", "KernPCB", "None"], help="device to use with input 3")

    args = parser.parse_args()

    if args.device == None:
        raise Exception("You have to specify a device")

    x = eval(args.device).openRS232(args.port)

    if args.device == "XLS200":
    	if args.input1 != "None":
    		x.openDevice(eval(args.input1), input=1)

    	if args.input2 != "None":
    		x.openDevice(eval(args.input2), input=2)

    	if args.input3 != "None":
    		x.openDevice(eval(args.input3), input=3)


    starttime = time.time()

    try:
        while True:
            print(x.getString(starttime))
            
    except KeyboardInterrupt:
        print("Closing")


if __name__ == "__main__":
    main()