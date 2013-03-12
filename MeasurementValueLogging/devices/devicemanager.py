# -*- coding: utf-8 -*-

# Python Measurement Value Logging Software.
# Module for managing different devices
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

import threading
from .devices import Device, Value, NullValue, TecpelDMM8061, XLS200, KernPCB, BS600

class DeviceManager(object):
    """The DeviceManager manages devices.

    It provides methods to add or delete devices,
    get their most recent measurement values and various other things.

    """
    
    _validDevices = ["TecpelDMM8061", "XLS200", "KernPCB", "BS600"]
    _running = False
    _stopEvent = None
    _thread = None

    devices = {}
    configs = {}
    rawValues = {}

    def __init__(self):
        pass

    def _checkConfig(self, config):
        assert config.deviceName in self._validDevices
        assert isinstance(config.parent, str) or isinstance(config.parent, float)  # FIXME: Check for deviceID object when implemented
        assert isinstance(config.subDevices, dict)

    def _updateRawValues(self):
        if self._running:
            self.rawValues = self._thread.rawValues
        else:
            import sys
            sys.stderr.write("GetValuesThread not running. Can't update values.\n")

    def _getLinearFunction(self, value1, value2):
        """Return a linear function, which contains value1 and value2.

        :param value1: Tuple of x,y coordinates
        :type value1: Tuple x,y
        :param value2: Tuple of x,y coordinates
        :type value2: Tuple x,y

        """
        try:
            m = (value1[1] - value2[1]) / (value1[0] - value2[0])
        except ZeroDivisionError:
            import sys
            sys.stderr.write("ZeroDivisionError during slope computation.\nSetting slope to 1\n")
            m = 1

        c = value1[1] - m*value1[0]

        def result(x):
            return m*x +c
        
        return result

    def isValidDevice(self, deviceName):
        """Tests whether deviceName is a valid device.

        :param deviceName: DeviceName (e.g. XLS200, TecpelDMM8061 etc.)
        :type deviceName: String
        :returns: Whether deviceName is a valid deviceName
        :rtype: Boolean

        """

        return deviceName in self._validDevices

    def getValidDevices(self):
        """Returns a list of valid deviceNames.
        
        :returns: List of valid deviceNames
        :rtype: List of strings

        """

        return self._validDevices

    def getAllDeviceIDs(self):
        """Returns a complete list of registered deviceIDs.

        :returns: Complete list of registered deviceIDs
        :rtype: List of deviceIDs

        """

        ids = []
        for id in self.configs:
            ids.append(id)

        return ids

    def getAvailiablePorts(self):
        """Returns a list of valid and availiable serial ports.

        :returns: List of valid and availiable serial ports
        :rtype: List of strings

        """

        import serial.tools.list_ports
        portsTuple = serial.tools.list_ports.comports()
        portsList = []

        for i in portsTuple:
            portsList.append(i[0])

        return tuple(portsList)

    def getStatus(self):
        """Returns the status of the deviceManager.
        
        True if deviceManager is running, otherwise False.

        :returns: Status of deviceManager
        :rtype: Boolean

        """

        return self._running

    def openDevice(self, deviceName, serialPort, *args, **kwargs):
        """Open a device.
        
        :param deviceName: Classname of the device to openDevice
        :type deviceName: String
        :param serialPort: Serial port on which the device sits
        :type serialPort: String
        :param args: args to pass to the devices init method
        :param kwargs: kwargs to pass to the devices init method
        :returns: DeviceID of opened device
        :rtype: :class:`DeviceID`

        """

        return self.openWithConfig(DeviceConfig(deviceName, serialPort, *args, **kwargs))

    def openSubdevice(self, deviceName, parentDeviceID, inputNumber, *args, **kwargs):
        """Open a device.
        
        :param deviceName: Classname of the device to openDevice
        :type deviceName: String
        :param parentDeviceID: DeviceID of the parent device (the multiboxdevice)
        :type parentDeviceID: DeviceID
        :param inputNumber: Input the device sits on
        :type inputNumber: Int
        :param args: args to pass to the devices init method
        :param kwargs: kwargs to pass to the devices init method
        :returns: DeviceID of opened device
        :rtype: :class:`DeviceID`

        """

        return self.openWithConfig(DeviceConfig(deviceName, parentDeviceID, inputNumber, *args, **kwargs))

    def openWithConfig(self, config):
        """Open a device with a config object. Returns a deviceID.

        :param config: DeviceConfig object
        :type config: :class:`DeviceConfig`
        :returns: DeviceID of opened device
        :rtype: :class:`DeviceID`

        """

        import time

        assert self._running == False # FIXME: use another error

        self._checkConfig(config)
        id = time.time()

        parentID = config.parent

        if isinstance(parentID, str):
            device = eval(config.deviceName).openRS232(config.parent, *config.args, **config.kwargs)

        elif isinstance(parentID, float): # FIXME: Check for deviceID object when implemented
            assert self.devices[parentID] # FIXME: use another error (e.g. WrongIDError)

            self.devices[parentID].openDevice(eval(config.deviceName),
                input = config.inputNumber, *config.args, **config.kwargs)
            device = self.devices[parentID].getDevice(input = config.inputNumber)
            self.configs[parentID].subDevices[id] = config.inputNumber

        self.devices[id] = device
        self.configs[id] = config

        return id

    def closeDevice(self, deviceID):
        """Close device with deviceID.
        
        :param deviceID: DeviceID of device to close
        :type deviceID: DeviceID

        """

        assert self._running == False # FIXME: use another error

        config = self.configs[deviceID]

        if isinstance(config.parent, str):
            import copy
            relCopy = copy.copy(config.subDevices)
            # prevent RuntimeError: dictionary changed size during iteration
            
            for subdeviceID, inputNumber in relCopy.iteritems():
                self.closeDevice(subdeviceID)

            del(self.devices[deviceID])
            del(self.configs[deviceID])

        elif isinstance(config.parent, float): # FIXME: Check for deviceID object when implemented
            parentID = config.parent
            self.getDevice(parentID).closeDevice(input=config.inputNumber)
            del(self.devices[deviceID])
            del(self.configs[deviceID])
            del(self.configs[parentID].subDevices[deviceID])

    def closeEmptyMultiboxDevices(self):
        """Close all MultiboxDevices without subDevices."""

        for i in self.getAllDeviceIDs():
            config = self.configs[i]
            if len(config.subDevices) == 0 and config.deviceName == "XLS200":
                self.closeDevice(i)

    def getLastRawValue(self, deviceID):
        """Returns the last raw value of device with ID deviceID.

        If there is no last value (last value == None), it returns a NullValue.

        :param deviceID: deviceID (e.g. XLS200, TecpelDMM8061 etc.)
        :type deviceID: DeviceID
        :returns: Last Value object of device with deviceID
        :rtype: Value
        
        """

        self._updateRawValues()

        try:
            return self.rawValues[deviceID]

        except KeyError:
            import sys
            sys.stderr.write("KeyError in getLastRawValue (no value yet?)\n")
            
            return NullValue()

    def getCalibratedLastRawValue(self, deviceID, calibration, unit=None):
        """Return a calibrated value from the getLastRawValue method.
        
        :param deviceID: DeviceID
        :type deviceID: DeviceID
        :param calibration: Calibration tuple
        :type calibration: Tuple
        :param unit: Unit or None
        :type unit: String or None

        The calibration tuple must contain either two integers m, c
        to create a function of style f(x) = m x + c
        or two tuples containing two points on such a linear function,
        used to compute m and c.

        """
        try:
            linearFunction = self._getLinearFunction(calibration[0], calibration[1])
        except TypeError:
            def resultFunction(x): return (calibration[0] * x + calibration[1])
            linearFunction = resultFunction

        class __Value(Value):
            displayedValue = None
            unit = None
            factor = (pow(10, 0),"")

            def getDisplayedValue(self):
                return self.displayedValue

            def getUnit(self):
                return self.unit

            def getFactor(self, type="value"):
                if type == "value":
                    return self.factor[0]
                elif type == "prefix":
                    return self.factor[1]

        rv = self.getLastRawValue(deviceID)
        if rv == None: return None

        result = __Value()

        result.displayedValue = linearFunction(rv.getDisplayedValue())
        result.factor = (rv.getFactor(type="value"), rv.getFactor(type="prefix"))
        result._time = rv.getTime()

        if unit: result.unit = unit
        else: result.unit = rv.getUnit()

        return result

    def getDevice(self, deviceID):
        """Return device with deviceID.
        
        :param deviceID: DeviceID
        :type deviceID: DeviceID
        :returns: :class:`devices.devices.Device` with deviceID
        :rtype: :class:`devices.devices.Device`

        """

        try:
            return self.devices[deviceID]

        except KeyError:
            return None

    def start(self):
        """Start the DeviceManager."""

        self._stopEvent = threading.Event()
        self._thread = _GetValuesThread(self._stopEvent, self.devices, self.configs)
        self._thread.start()
        self._running = True

    def stop(self):
        """Stop the DeviceManager."""

        if self._running == True:
            self._stopEvent.set()
            self._running = False
            self._thread = None
            self._stopEvent = None


class DeviceConfig(object):
    """DeviceConfig objects can be passed to DeviceManager openWithConfig method."""

    parent = None # either deviceID or serial port
    subDevices = {} # {"subdeviceID":inputNumber} only applicable for multiboxdevices
    inputNumber = None # only applicable for subdevices
    deviceName = None
    args = ()
    kwargs = {}

    def __init__(self, deviceName, parent, inputNumber=None, *args, **kwargs):
        """Create a DeviceConfig object.
        
        :param deviceName: DeviceName
        :type deviceName: String
        :param parent: Parent deviceID or serial port
        :type parent: DeviceID or String
        :param inputNumber: InputNumber of the device (if the device is a subDevice)
        :type inputNumber: :class:`int` or :class:`None`
        :returns: deviceID of opened device.
        :rtype: deviceID

        """

        assert deviceName in DeviceManager._validDevices

        self.parent = parent
        self.inputNumber = inputNumber
        self.deviceName = deviceName
        self.args = args
        self.kwargs = kwargs


class _GetValuesThread(threading.Thread):
    devices = {}
    configs = {}
    rawValues = {}

    def __init__(self, stop_event, devices, configs):
        threading.Thread.__init__(self)
        self.daemon = True
        self.stop_event = stop_event

        self.devices = devices
        self.configs = configs

        for key in self.devices.iteritems():
            self.rawValues[key] = NullValue()

    def run(self):
        while not self.stop_event.is_set():
            self.updateValue()

    def updateValue(self):
        # python3 incompatibility: iteritems
        try:
            for key, config in self.configs.iteritems():
                if isinstance(config.parent, str):
                    if len(config.subDevices) == 0 and config.deviceName != "XLS200":
                            # If there are no subdevices and it's not an "empty" Multiboxdevice
                        rv = self.devices[key].getRawValue()
                        if rv:
                            self.rawValues[key] = rv
                        else:
                            pass

                    else:
                        for subID, subInput in config.subDevices.iteritems():
                            rv = self.devices[key].getRawValue(input = subInput)
                            if rv:
                                self.rawValues[subID] = rv
                            else:
                                pass

        except RuntimeError:
            # A RuntimeError: dictionary changed size during iteration
            # may occur here, if a device is deleted, but this updateValue
            # function is still trying to get an rawValue. (-> the devicemanager
            # is therefore not closed yet) It does no harm though,
            # as the device is going to be closed afterwards.
            pass