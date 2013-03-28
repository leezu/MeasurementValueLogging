# -*- coding: utf-8 -*-

# Python Measurement Value Logging Software.
# Module for different devices
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


import si
import serial
import re
import time

deviceClassNames = ("TecpelDMM8061", "VoltcraftVC820", "XLS200", "KernPCB", "BS600")

class Device(object):
    """The base device class.

    Subclasses must define at least the methods defined in this base class
    or, when applicable inherit them unmodified.

    """

    _ser = None # this is the serial device / connection
    _baudrate = 2400 # baudrate
    _rts = False # ready to send rs232 flag (used for setting up the rs232 connection)
    _dtr = False # data terminal ready rs232 flag (used for setting up the rs232 connection)
    _ownSer = False # does the device own the serial connection or is it just a user
    # (e.g. one of three devices, which are behind a multibox)
    _timeout = 0.2 # timeout value for reading from serial device

    def __init__(self, ser):
        """Setup a device as new device or as subdevice.

        Assign ser to self._ser and if ser is not already openend (the device is not a sub device)
        set the in the class defined attributes and open the serial connection.
        If the connection has to be openend, _ownSer flag is set.

        To setup the device as a subdevice simply pass the serial connection to the class constructor.
        To setup the device as a new device one has to use the openRS232 classmethod.

        :param ser: Serial connection (pyserial module)
        :type ser: Serial

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

    def close(self):
        """Closes the serial connection if the device ownes the serial connection (if its not a subdevice)."""

        if self._ownSer is True:
            self._ser.close()

    @classmethod
    def openRS232(cls, port, *args, **kwargs):
        """Open a new serial connection and create a Device object with it.

        :param port: Serial port (see pyserial documentation)
        :type port: String
        :returns: Device object
        :rtype: Device

        Valid port parameters are for example:
            - /dev/ttyUSB0 (Linux)
            - COM1 (Windows)

        """

        ser = serial.Serial()
        ser.port = port
        
        return cls(ser, *args, **kwargs)

    def __repr__(self):
        return "{classname}(serial={serial!r}) # ownSer={ownser}".format(classname=self.__class__.__name__,
            serial=self._ser, ownser = self._ownSer)

    def __str__(self):
        return "{classname} (port={serialport!s}, baudrate={serialbaudr!s})".format(
            classname=self.__class__.__name__,
            serialport=self._ser.port,
            serialbaudr=self._baudrate)

    def isAvailable(self):
        """Returns the device status (available or not)
        
        :returns: Device status
        :rtype: Boolean

        """

        return self._ser.isOpen()

    def getRawValue(self):
        """Return a Value object or None.

        :returns: :class:`devices.devices.Value` or :class:`None`
        :rtype: :class:`devices.devices.Value` or :class:`None`

        """

        raise NotImplementedError


class MultiboxDevice(Device):
    """This is a special MultiboxDevice, which allows to use multiple
    subdevices on just one serial connection.

    Every subclass must implement at least the in this class defined methods
    and the methods of the base device class.

    """

    def openDevice(self, deviceClass, input, *args, **kwargs):
        """Open a device of deviceClass on input.

        \*args and \*\*kwargs are passed on to the devices __init__ methods.

        :param deviceClass: Class of the subdevice
        :type deviceClass: :class:`devices.devices.Device`
        :param input: Input number of subdevice
        :type input: Input

        """

        raise NotImplementedError

    def closeDevice(self, input):
        """Close the device on input.
        
        :param input: Input number of subdevice
        :type input: Input

        """

        raise NotImplementedError

    def getDevice(self, input):
        """This returns the device object on input.

        This does NOT sets the device to the right input.
        If you want to do any actual communication with the
        returned device, call changeInput(input) first.

        :param input: Input number of subdevice
        :type input: Input
        :returns: :class:`devices.devices.Device` on input
        :rtype: :class:`devices.devices.Device`

        """

        raise NotImplementedError


class Value(object):
    """This class represents one measurement result.

    Device classes must implement their own value subclass with at least the
    methods defined in this base class.

    """

    _time = 0

    def __repr__(self):
        return "< {classname}: displaydValue={!s}, factor={!s} >".format(
            self.getDisplayedValue(), self.getFactor(),
            classname = self.__class__.__name__)

    def __str__(self):
        return "{} {}".format(self.getDisplayedValue(), self.getFactor())

    def __unicode__(self):
        return "{} {}{}".format(self.getDisplayedValue(),
            self.getUnit(), self.getFactor())

    def getDisplayedValue(self):
        """Returns the displayed value (as a number).

        :returns: Displayed value
        :rtype: Float

        """

        raise NotImplementedError

    def getUnit(self):
        """Returns the unit (e.g. "g" (gram) or "V" (volt)).

        :returns: Unit
        :rtype: String

        """

        raise NotImplementedError

    def getFactor(self, type="value"):
        """Returns the factor of the displayed value (According to the SI-Prefixes).

        For example 10^(-3) for the milli prefix.
        If type == "prefix" it returns the SI-Prefixes.

        :returns: Factor of the displayed value as a number or a SI-Prefix
        :rtype: Int or String

        """

        raise NotImplementedError

    def getTime(self):
        """Returns the time the measurement value was taken in seconds since the epoch.
    
        :returns: Time the measurement value was taken
        :rtype: Float

        """

        return self._time


class NullValue(Value):
    """This class represents an "empty" measurement value."""

    def getDisplayedValue(self):
        return 0

    def getUnit(self):
        return ""

    def getFactor(self, type="value"):
        if type == "value":
            return pow(10, 0)
        elif type == "prefix":
            return ""


class TecpelDMM8061(Device):
    """This class represents a TECPEL DMM 8061 multimeter."""
    
    _baudrate = 2400
    _rts = False
    _dtr = True
    _timeout = 0.5

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

        def getDisplayedValue(self):
            result = self.d4.getDigit() * 1000 + self.d3.getDigit() * 100 + self.d2.getDigit() * 10 + self.d1.getDigit()
            if (self.d4.ex):
                result *= -1
            if (self.d3.ex):
                result /= 1000.0
            elif (self.d2.ex):
                result /= 100.0
            elif (self.d1.ex):
                result /= 10.0

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
                    return "celsius"

            elif type == "unit":
                if self.ohm:
                    return u"Ω"
                elif self.farad:
                    return "F"
                elif self.hertz:
                    return "Hz"
                elif self.volt:
                    return "V"
                elif self.ampere:
                    return "A"
                else:
                    return u"°C"

        def getFactor(self, type="value"):
            if type == "value":
                return si.getFactor(self.getFactor("prefix"))

            elif type == "prefix":
                if self.nano:
                    return "n"
                elif self.micro:
                    return u"µ"
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
        starttime = time.time()
        assert self.isAvailable()

        read = self._ser.read(26)

        self._ser.flushInput()

        idList = []
        for i in read:
            idList.append(ord(i) >> 4)

        try:
            startIndex = idList.index(1)

            # Test whether the read value is correct
            if idList[startIndex + 1] == 2 and idList[startIndex + 4] == 5 and idList[startIndex + 7] == 8 and\
                    idList[startIndex + 10] == 11 and idList[startIndex + 12] == 13:
                
                valueString = read[startIndex:(startIndex+13)]

                result = self.__Value()

                b = ord(valueString[0])
                result.rs232  = self._testBit(b, 0)
                result.auto  = self._testBit(b, 1)
                result.dc  = self._testBit(b, 2)
                result.ac = self._testBit(b, 3)

                b = ord(valueString[1])
                result.d4.a  = self._testBit(b, 0)
                result.d4.f  = self._testBit(b, 1)
                result.d4.e  = self._testBit(b, 2)
                result.d4.ex = self._testBit(b, 3)

                b = ord(valueString[2])
                result.d4.b = self._testBit(b, 0)
                result.d4.g = self._testBit(b, 1)
                result.d4.c = self._testBit(b, 2)
                result.d4.d = self._testBit(b, 3)

                b = ord(valueString[3])
                result.d3.a  = self._testBit(b, 0)
                result.d3.f  = self._testBit(b, 1)
                result.d3.e  = self._testBit(b, 2)
                result.d3.ex = self._testBit(b, 3)

                b = ord(valueString[4])
                result.d3.b = self._testBit(b, 0)
                result.d3.g = self._testBit(b, 1)
                result.d3.c = self._testBit(b, 2)
                result.d3.d = self._testBit(b, 3)

                b = ord(valueString[5])
                result.d2.a  = self._testBit(b, 0)
                result.d2.f  = self._testBit(b, 1)
                result.d2.e  = self._testBit(b, 2)
                result.d2.ex = self._testBit(b, 3)

                b = ord(valueString[6])
                result.d2.b = self._testBit(b, 0)
                result.d2.g = self._testBit(b, 1)
                result.d2.c = self._testBit(b, 2)
                result.d2.d = self._testBit(b, 3)

                b = ord(valueString[7])
                result.d1.a  = self._testBit(b, 0)
                result.d1.f  = self._testBit(b, 1)
                result.d1.e  = self._testBit(b, 2)
                result.d1.ex = self._testBit(b, 3)

                b = ord(valueString[8])
                result.d1.b = self._testBit(b, 0)
                result.d1.g = self._testBit(b, 1)
                result.d1.c = self._testBit(b, 2)
                result.d1.d = self._testBit(b, 3)

                b = ord(valueString[9])
                result.diode_test = self._testBit(b, 0)
                result.kilo = self._testBit(b, 1)
                result.nano = self._testBit(b, 2)
                result.micro = self._testBit(b, 3)

                b = ord(valueString[10])
                result.continuity_buzzer = self._testBit(b, 0)
                result.mega = self._testBit(b, 1)
                result.duty_cycle = self._testBit(b, 2)
                result.milli = self._testBit(b, 3)

                b = ord(valueString[11])
                result.hold = self._testBit(b, 0)
                result.delta = self._testBit(b, 1)
                result.ohm = self._testBit(b, 2)
                result.farad = self._testBit(b, 3)

                b = ord(valueString[12])
                result.battery_low = self._testBit(b, 0)
                result.hertz = self._testBit(b, 1)
                result.volt = self._testBit(b, 2)
                result.ampere = self._testBit(b, 3)

                result._time = time.time()

                return result

        except (ValueError, IndexError):
            pass

        return None


class VoltcraftVC820(TecpelDMM8061):
    """This class represents a VOLTCRAFT VC 840 multimeter

    The VC 40 is identical to the TecpelDMM8061.

    """


class XLS200(MultiboxDevice):
    """This class represents the XLS200 MultiboxDevice.

    http://www.xlsmess.de/html/xls_200.html

    This device passes one of the three input serial connections, depending
    in which combination DTR and RTS rs232 attributes are set.

    - DTR True & RTS False: Input 1
    - DTR False & RTS True: Input 2
    - DTR False & RTS False: Input 3

    """

    _in1 = None
    _in2 = None
    _in3 = None

    def __init__(self, ser):
        super(XLS200, self).__init__(ser)

    def __repr__(self):
        string = "{classname}(serial={serial!r}) # ownSer={ownser}".format(
            classname=self.__class__.__name__, serial=self._ser, ownser = self._ownSer)

        if self.getDevice(input=1):
            string += ", in1={in1}".format(in1=self.getDevice(input=1).__class__.__name__)
        if self.getDevice(input=2):
            string += ", in2={in2}".format(in2=self.getDevice(input=2).__class__.__name__)
        if self.getDevice(input=3):
            string += ", in3={in3}".format(in3=self.getDevice(input=3).__class__.__name__)

        return string

    def __str__(self):
        string = "{classname} (port={port!s}".format(
            classname=self.__class__.__name__, port=self._ser.port)

        if self.getDevice(input=1):
            string += ", in1={in1}".format(in1=self.getDevice(input=1).__class__.__name__)
        if self.getDevice(input=2):
            string += ", in2={in2}".format(in2=self.getDevice(input=2).__class__.__name__)
        if self.getDevice(input=3):
            string += ", in3={in3}".format(in3=self.getDevice(input=3).__class__.__name__)

        return string + ")"

    def changeInput(self, input):
        # DTR True & RTS False = 1
        # DTR False & RTS True = 2
        # DTR False & RTS False = 3
        
        assert self.isAvailable()

        if input == 1:
            self._ser.setRTS(level=False)
            self._ser.setDTR(level=True)
            if self._in1:
                self._ser.baudrate = self._in1._baudrate
                self._ser.timeout = self._in1._timeout
            self._ser.flushInput()

        elif input == 2:
            self._ser.setRTS(level=True)
            self._ser.setDTR(level=False)
            if self._in2:
                self._ser.baudrate = self._in2._baudrate
                self._ser.timeout = self._in2._timeout
            self._ser.flushInput()

        elif input == 3:
            self._ser.setRTS(level=False)
            self._ser.setDTR(level=False)
            if self._in3:
                self._ser.baudrate = self._in3._baudrate
                self._ser.timeout = self._in3._timeout
            self._ser.flushInput()

    def openDevice(self, deviceClass, input, *args, **kwargs):
        assert self.isAvailable()

        if input == 1:
            self._in1 = deviceClass(self._ser, *args, **kwargs)

        elif input == 2:
            self._in2 = deviceClass(self._ser, *args, **kwargs)

        elif input == 3:
            self._in3 = deviceClass(self._ser, *args, **kwargs)

        else:
            raise Exception("Input has to be in rage of 1 to 3")

    def closeDevice(self, input):
        if input == 1:
            self._in1.close()
            self._in1 = None

        elif input == 2:
            self._in2.close()
            self._in2 = None

        elif input == 3:
            self._in3.close()
            self._in3 = None

    def getRawValue(self, input=0):
        if input == 1:
            self.changeInput(1)
            return self._in1.getRawValue()

        elif input == 2:
            self.changeInput(2)
            return self._in2.getRawValue()

        elif input == 3:
            self.changeInput(3)
            return self._in3.getRawValue()
        
        else:
            return None

    def getDevice(self, input):
        if input == 1:
            return self._in1

        elif input == 2:
            return self._in2

        elif input == 3:
            return self._in3


class Balance(Device):
    """This class represents Balance Devices."""
    _typeOfValue = "all"

    def setTypeOfValue(self, typeOfValue):
        """Balance Devices have two different kind of values: Stable and unstable Values.

        This method sets, which kind of values should be returned by the getRawValue method.
        For more information please see the Device's manual.

        :param typeOfValue: Type of values, which should be returned by the getRawValue method - "stable" or "all"
        :type typeOfValue: String

        """

        if typeOfValue in ["stable", "all"]:
            self._typeOfValue = typeOfValue
        else:
            raise Exception("Invalid typeOfValue")



class KernPCB(Balance):
    """This class represents the KernPCB Balance."""

    _regex = re.compile(r"\s[\s-][\d\s\.]{10}\s.{3}\r\n")

    _baudrate = 9600

    class __Value(Value):
        string = None

        def getDisplayedValue(self):
            v = float(self.string[2:12])

            if self.string[1] is "-":
                v *= -1

            return v

        def getUnit(self, type="unit"):
            if type == "name":
                return "gram"

            elif type == "unit":
                return "g"

        def getFactor(self, type="value"):
            if type == "value":
                return pow(10, 0)

            elif type == "prefix":
                return ""

    def getRawValue(self):
        starttime = time.time()

        assert self.isAvailable()

        result = self.__Value()

        if self._typeOfValue == "stable":
            self._ser.write("s")
            s = self._ser.read(size = 35)
            # One value has 18 bytes, to make sure to get a complete one
            # (and not the second 1/2 of one, and the first 1/2 of another)
            # we read 35 bytes and match for one complete value
            self._ser.flushInput()

            try:
                result.string = self._regex.search(s).group()
                result._time = time.time()
                return result

            except AttributeError:
                pass

            return None

        elif self._typeOfValue == "all":
            self._ser.write("w")
            s = self._ser.read(size = 35)
            # One value has 18 bytes, to make sure to get a complete one
            # (and not the second 1/2 of one, and the first 1/2 of another)
            # we read 35 bytes and match for one complete value
            self._ser.flushInput()

            try:
                result.string = self._regex.search(s).group()
                result._time = time.time()
                return result

            except AttributeError:
                pass

            return None

    def setTara(self):
        """Set taring.

        For more information see device manual.

        """

        assert self.isAvailable()

        return self._ser.write("t") # Should be 1 if write succeeds


class BS600(Balance):
    """This class represents the BS600 Balance."""

    _stable = re.compile(r"[WCP][TC]ST[+-][\d\s\.]{7}.{4}")
    _all = re.compile(r"[WCP][TC][SU][TS][+-][\d\s\.]{7}.{4}")

    _baudrate = 2400

    class __Value(Value):
        string = None

        def getDisplayedValue(self):
            v = float(self.string[5:12])

            if self.string[4] is "-":
                v *= -1

            return v

        def getUnit(self):
            try:
                return self.string[12:16].strip()
            except IndexError:
                return ""

        def getFactor(self, type="value"):
            if type == "value":
                return pow(10, 0)

            elif type == "prefix":
                return ""
    
    def getRawValue(self):
        starttime = time.time()

        assert self.isAvailable()

        result = self.__Value()

        val = self._ser.read(size = 35)
        # One value has 18 bytes, to make sure to get a complete one
        # (and not the second 1/2 of one, and the first 1/2 of another)
        # we read 35 bytes and match for one complete value
        self._ser.flushInput()

        try:
            if self._typeOfValue == "stable":
                result.string = self._stable.search(val).group()
                result._time = time.time()
                return result

            elif self._typeOfValue == "all":
                result.string = self._all.search(val).group()
                result._time = time.time()
                return result

        except AttributeError:
            pass

        return None
