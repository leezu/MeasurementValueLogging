# -*- coding: utf-8 -*-

class Device(object):
    """This class is the base device class.

    Subclasses must define at least the methods defined in this base class
    or, when applicable inherit them unmodified.

    """

    import serial

    _ser = None # this is the serial device / connection
    _baudrate = 2400 # baudrate
    _rts = False # ready to send rs232 flag (used for setting up the rs232 connection)
    _dtr = False # data terminal ready rs232 flag (used for setting up the rs232 connection)
    _ownSer = False # does the device own the serial connection or is it just a user
    # (e.g. one of three devices, which are behind a multibox)
    _timeout = None # timeout value for reading from serial device

    def __init__(self, ser, *args, **kwargs):
        """Setup a device as new or subdevice.

        Assign ser to self._ser and if ser is already openend (the device is a sub device)
        do nothing. Otherwise set the in the class defined attributes and open the serial connection.
        If the connection has to be setup new, _ownSer flag is set.

        To setup the device as a subdevice simply pass the serial connection to the class constructor.
        To setup the device as a new device one has to use the openRS232 classmethod.

        Subclasses may use more positional or keyword arguments.

        """

        self._ser = ser
        
        if self.isAvailable() is False:
            # only do the following if the serial connection is not set up yet
            # (e.g. if the device is not behind a multimeter)
            self._ser.baudrate = self._baudrate
            self._ser.timeout = self._timeout

            self._ser.open()

            self._ownSer = True

            self._ser.setRTS(level=self._rts)
            self._ser.setDTR(level=self._dtr)

    def __del__(self):
        """Closes the serial connection if the device ownes the serial connection (if its not a subdevice)"""

        if self._ownSer is True:
            self._ser.close()

    @classmethod
    def openRS232(cls, port, *args, **kwargs):
        """Create a new serial connection and create a new object with it.

        One has to pass the port argument, which must be a valid argument following to
        the pyserial documentation ( http://pyserial.sourceforge.net/ ):

        - /dev/ttyUSB0 (Linux)
        - COM1 (Windows)

        For more examples see the pyserial documentation.

        """

        import serial

        ser = serial.Serial()
        ser.port = port
        
        return cls(ser, *args, **kwargs)

    def isAvailable(self):
        """Returns the device status (available or not)"""

        return self._ser.isOpen()

    def getRawValue(self):
        """Return a Value object."""

        raise NotImplementedError
    
    def getString(self, starttime):
        """Return a string representation of the currently displayed value
        
        This can be very useful for command line output

        """

        raise NotImplementedError

class MultiboxDevice(Device):
    """This is a special MultiboxDevice, which allows to use multiple
    other devices on just one serial connection.

    Every subclass must implement at least the in this class defined methods
    and the methods of the base device class.

    """

    def openDevice(self, deviceClass, input = 1, *args, **kwargs):
        """Open a device of deviceClass on input X

        *args and **kwargs are passed on to the devices __init__ methods.

        """

        raise NotImplementedError

    def closeDevice(self, input = 1):
        """Close the device on input X"""

        raise NotImplementedError

    def getDevice(self, input = 1):
        """This returns the device object on input X"""

        raise NotImplementedError


class Value(object):
    """This class represents one measurement result.

    Device classes must implement their own value subclass with at least the
    methods defined in this base class.

    """

    def getDisplayedValue(self):
        """Returns the displayed value (as a number)"""

        raise NotImplementedError

    def getUnit(self):
        """returns the unit (e.g. "g" (gram) or "V" (volt))"""

        raise NotImplementedError

    def getFactor(self):
        """returns the factor of the displayed value (According to the SI-Prefixes).

        For example 10^(-3) for the milli prefix.

        """

        raise NotImplementedError


class TecpelDMM8061(Device):
    """Multimeter

    TECPEL DMM 8061 or VOLTCRAFT VC 840

    """

    import time
    
    _baudrate = 2400
    _rts = False
    _dtr = True

    class __Value(Value):
        class __Digit:
            """Represents one digit on the screen"""

            a = 0
            b = 0
            c = 0
            d = 0
            e = 0
            f = 0
            g = 0
            ex = 0

            def getDigit(self):
                """Returns a decimal digit.

                If there is no correct digit stored (e.g. overload), 0 is returned

                """

                if (self.a and self.b and self.c and self.d and self.e and self.f and self.g):
                    return 8
                elif (self.a and self.b and self.c and self.d and self.e and self.f):
                    return 0
                elif (self.a and self.c and self.d and self.e and self.f and self.g):
                    return 6
                elif (self.a and self.b and self.c and self.d and self.f and self.g):
                    return 9
                elif (self.a and self.c and self.d and self.f and self.g):
                    return 5
                elif (self.a and self.b and self.d and self.e and self.g):
                    return 2
                elif (self.a and self.b and self.c and self.d and self.g):
                    return 3
                elif (self.b and self.c and self.f and self.g):
                    return 4
                elif (self.a and self.b and self.c):
                    return 7
                elif (self.b and self.c):
                    return 1
                else:
                    return 0 #e.g. for overload

                    # FIXME: return -1 for overload, check for this in getDisplayedValue and give better output

        properties = ["rs232", "diode_test", "continuity_buzzer", "battery_low",
            "duty_cycle", "hold", "delta", "auto", "dc", "ac"]

        rs232 = 0
        diode_test  = 0
        continuity_buzzer = 0
        battery_low = 0
        duty_cycle = 0
        hold = 0
        delta = 0

        auto = 0
        dc = 0
        ac = 0

        d4 = __Digit()
        d3 = __Digit()
        d2 = __Digit()
        d1 = __Digit()

        nano = 0
        micro = 0
        milli = 0
        kilo = 0
        mega = 0
        
        ohm = 0
        farad = 0
        hertz = 0
        volt = 0
        ampere = 0

        time = 0


        def getDisplayedValue(self):
            result = self.d4.getDigit() * 1000 + self.d3.getDigit() * 100 + self.d2.getDigit() * 10 + self.d1.getDigit()
            if (self.d4.ex):
                result *= -1
            if (self.d3.ex):
                result /= 1000
            elif (self.d2.ex):
                result /= 100
            elif (self.d1.ex):
                result /= 10

            return result

        def getUnit(self, type="unit"):
            if type == "name":
                if self.ohm:
                    return "ohm"
                elif self.farad:
                    return "farad"
                elif self.hertz:
                    return "hertz"
                elif self.volt:
                    return "volt"
                elif self.ampere:
                    return "ampere"
                else:
                    return ""

            elif type == "unit":
                if self.ohm:
                    return "Ω"
                elif self.farad:
                    return "F"
                elif self.hertz:
                    return "Hz"
                elif self.volt:
                    return "V"
                elif self.ampere:
                    return "A"
                else:
                    return ""

        def getFactor(self, type="value"):
            if type == "value":
                if self.nano:
                    return (10 ^ (-9))
                elif self.micro:
                    return (10 ^ (-6))
                elif self.milli:
                    return (10 ^ (-3))
                elif self.kilo:
                    return (10 ^ (3))
                elif self.mega:
                    return (10 ^ (6))
                else:
                    return (10 ^ (0))

            elif type == "prefix":
                if self.nano:
                    return "n"
                elif self.micro:
                    return "µ"
                elif self.milli:
                    return "m"
                elif self.kilo:
                    return "k"
                elif self.mega:
                    return "M"
                else:
                    return ""

        def batteryLow(self):
            return self.battery_low

    def _testBit(self, b, number):
        """Return the numberED bit in b"""

        if (b & (1 << number)) > 0:
            return 1
        elif (b & (1 << number)) == 0:
            return 0
        else:
            raise Exception

    def getRawValue(self):
        import time
        assert self.isAvailable()

        bytesrecived = 0
        result = self.__Value()

        #There are 14 bytes to be received, for every received byte the corresponding bit in bytesreceived is set
        while(bytesrecived != int('11111111111111', base=2)):
            b = ord(self._ser.read())
            id = (b & int('11110000', base=2)) >> 4 #convert the higher nibble to the id
            
            if id > 0: #Sometimes id seems to be 0 if DMM8061 is (re)started while running the program
                bytesrecived |= 1 << (id-1)
            else:
                continue

            if id == 1:
                result.rs232  = self._testBit(b, 0)
                result.auto  = self._testBit(b, 1)
                result.dc  = self._testBit(b, 2)
                result.ac = self._testBit(b, 3)

            elif id == 2:
                result.d4.a  = self._testBit(b, 0)
                result.d4.f  = self._testBit(b, 1)
                result.d4.e  = self._testBit(b, 2)
                result.d4.ex = self._testBit(b, 3)

            elif id == 3:
                result.d4.b = self._testBit(b, 0)
                result.d4.g = self._testBit(b, 1)
                result.d4.c = self._testBit(b, 2)
                result.d4.d = self._testBit(b, 3)

            elif id == 4:
                result.d3.a  = self._testBit(b, 0)
                result.d3.f  = self._testBit(b, 1)
                result.d3.e  = self._testBit(b, 2)
                result.d3.ex = self._testBit(b, 3)

            elif id == 5:
                result.d3.b = self._testBit(b, 0)
                result.d3.g = self._testBit(b, 1)
                result.d3.c = self._testBit(b, 2)
                result.d3.d = self._testBit(b, 3)

            elif id == 6:
                result.d2.a  = self._testBit(b, 0)
                result.d2.f  = self._testBit(b, 1)
                result.d2.e  = self._testBit(b, 2)
                result.d2.ex = self._testBit(b, 3)

            elif id == 7:
                result.d2.b = self._testBit(b, 0)
                result.d2.g = self._testBit(b, 1)
                result.d2.c = self._testBit(b, 2)
                result.d2.d = self._testBit(b, 3)

            elif id == 8:
                result.d1.a  = self._testBit(b, 0)
                result.d1.f  = self._testBit(b, 1)
                result.d1.e  = self._testBit(b, 2)
                result.d1.ex = self._testBit(b, 3)

            elif id == 9:
                result.d1.b = self._testBit(b, 0)
                result.d1.g = self._testBit(b, 1)
                result.d1.c = self._testBit(b, 2)
                result.d1.d = self._testBit(b, 3)

            elif id == 10:
                result.diode_test = self._testBit(b, 0)
                result.kilo = self._testBit(b, 1)
                result.nano = self._testBit(b, 2)
                result.micro = self._testBit(b, 3)

            elif id == 11:
                result.continuity_buzzer = self._testBit(b, 0)
                result.mega = self._testBit(b, 1)
                result.duty_cycle = self._testBit(b, 2)
                result.milli = self._testBit(b, 3)

            elif id == 12:
                result.hold = self._testBit(b, 0)
                result.delta = self._testBit(b, 1)
                result.ohm = self._testBit(b, 2)
                result.farad = self._testBit(b, 3)

            elif id == 13:
                result.battery_low = self._testBit(b, 0)
                result.hertz = self._testBit(b, 1)
                result.volt = self._testBit(b, 2)
                result.ampere = self._testBit(b, 3)

            elif id == 14:
                # SEG 14 does not contain any useful information on the RS232 output
                pass

        result.time = time.time()

        return result

    def getString(self, starttime):
        assert self.isAvailable()

        result = self.getRawValue()

        return (str(round(result.time - starttime, 3)) + ": " + str(result.getDisplayedValue()) + " " +
            str(result.getFactor("prefix")) + str(result.getUnit("unit")))


class XLS200(MultiboxDevice):
    """XLS200

    http://www.xlsmess.de/html/xls_200.html

    This device passes one of the three input serial connections, depending
    in which combination DTR and RTS rs232 attributes are set.

    DTR True & RTS False -> 1
    DTR False & RTS True -> 2
    DTR False & RTS False -> 3

    """

    _in1 = None
    _in2 = None
    _in3 = None

    def __init__(self, ser, in1=None, in2=None, in3=None, *args, **kwargs):
        super(XLS200, self).__init__(ser)

        if in1:
            self.openDevice(in1, input = 1, *args, **kwargs)

        if in2:
            self.openDevice(in2, input = 2, *args, **kwargs)

        if in3:
            self.openDevice(in3, input = 3, *args, **kwargs)

    def _changeInput(self, input = 1):
        # DTR True & RTS False = 1
        # DTR False & RTS True = 2
        # DTR False & RTS False = 3
        
        assert self.isAvailable()

        if input == 1 and self._in1 is not None:
            self._ser.setRTS(level=False)
            self._ser.setDTR(level=True)
            self._ser.baudrate = self._in1._baudrate
            self._ser.timeout = self._in1._timeout

        if input == 2 and self._in2 is not None:
            self._ser.setRTS(level=True)
            self._ser.setDTR(level=False)
            self._ser.baudrate = self._in2._baudrate
            self._ser.timeout = self._in2._timeout

        if input == 3 and self._in3 is not None:
            self._ser.setRTS(level=False)
            self._ser.setDTR(level=False)
            self._ser.baudrate = self._in3._baudrate
            self._ser.timeout = self._in3._timeout

    def openDevice(self, deviceClass, input=1, *args, **kwargs):
        assert self.isAvailable()

        if input == 1:
            self._in1 = deviceClass(self._ser, *args, **kwargs)

        elif input == 2:
            self._in2 = deviceClass(self._ser, *args, **kwargs)

        elif input == 3:
            self._in3 = deviceClass(self._ser, *args, **kwargs)

        else:
            raise Exception("Input has to be in rage of 1 to 3")

    def closeDevice(self, input = 1):
        if input == 1:
            self._in1 = None

        elif input == 2:
            self._in2 = None

        elif input == 3:
            self._in3 = None

    def getRawValue(self, input = 1):
        if input == 1:
            self._changeInput(input = 1)
            return self._in1.getRawValue()

        elif input == 2:
            self._changeInput(input = 2)
            return self._in2.getRawValue()

        elif input == 3:
            self._changeInput(input = 3)
            return self._in3.getRawValue()


    def getString(self, starttime):
        returnValue = ""

        if self._in1:
            self._changeInput(input = 1)
            returnValue += ("Input 1:\n\t" + self._in1.getString(starttime) + "\n")

        if self._in2:
            self._changeInput(input = 2)
            returnValue += ("Input 2:\n\t" + self._in2.getString(starttime) + "\n")

        if self._in3:
            self._changeInput(input = 3)
            returnValue += ("Input 3:\n\t" + self._in3.getString(starttime) + "\n")

        return returnValue

    def getDevice(self, input = 1):
        if input == 1:
            self._changeInput(input = 1)
            return self._in1

        elif input == 2:
            self._changeInput(input = 2)
            return self._in2

        elif input == 3:
            self._changeInput(input = 3)
            return self._in3


class KernPCB(Device):
    _baudrate = 9600
    _timeout = 1
    _typeOfValue = "unstable"


    def __init__(self, ser, typeOfValue="unstable", *args, **kwargs):
        super(KernPCB, self).__init__(ser)

        if typeOfValue in ["stable", "unstable"]:
            self._typeOfValue = typeOfValue
        else:
            raise Exception("Invalid typeOfValue")

    @classmethod
    def openRS232(cls, port, *args, **kwargs):
        import serial

        ser = serial.Serial()
        ser.port = port
        
        return cls(ser, *args, **kwargs)

    class __Value(Value):
        string = None

        def getDisplayedValue(self):
            if 'Error' in self.string:
                return "ERROR"
            else:
                v = float(self.string[2:12])

                if self.string[1] is "-":
                    v *= -1

                return str(v)

        def getUnit(self, type="unit"):
            if type == "name":
                return "gram"

            elif type == "unit":
                return "g"

        def getFactor(self, type="value"):
            if type == "value":
                return (10 ^ (0))

            elif type == "prefix":
                return ""

    def getRawValue(self):
        assert self.isAvailable()

        result = self.__Value()

        if self._typeOfValue == "stable":
            while True:
                self._ser.write("s")
                s = self._ser.read(size = 18)

                try:
                    if ord(s[0]) == 32 and ord(s[16]) == 13 and ord(s[17]) == 10: # see documentation of rs232 output
                        result.string = s
                        return result

                except IndexError:
                    pass

        elif self._typeOfValue == "unstable":
            while True:
                self._ser.write("w")
                s = self._ser.read(size = 18)

                try:
                    if ord(s[0]) == 32 and ord(s[16]) == 13 and ord(s[17]) == 10: # see documentation of rs232 output
                        result.string = s
                        return result

                except IndexError:
                    pass

    def setTara(self):
        """Set taring.

        For more information see device manual.

        """

        assert self.isAvailable()

        return self._ser.write("t") # Should be 1 if write succeeds

    def getString(self, starttime):
        import time

        return (str(round(time.time() - starttime, 3)) + ":" + self.getRawValue().string[:16])
        # dont print the CR and LF at the end of the string (this would result in an unwanted newline in output)