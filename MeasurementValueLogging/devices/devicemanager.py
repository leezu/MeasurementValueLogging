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
        assert isinstance(config.relationship, tuple) and (len(config.relationship) == 2 or len(config.relationship) == 3)
        assert isinstance(config.relationship[0], str) or isinstance(config.relationship[0], float)
        assert isinstance(config.relationship[1], dict)

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

    def openWithConfig(self, config):
        """Open a device with a config object. Returns a deviceID.

        :param config: DeviceConfig object
        :type config: DeviceConfig
        :returns: DeviceID of opened device
        :rtype: DeviceID

        """

        import time

        assert self._running == False # FIXME: use another error

        self._checkConfig(config)
        id = time.time()

        parentID = config.relationship[0]

        if isinstance(parentID, str):
            device = eval(config.deviceName).openRS232(config.relationship[0], *config.args, **config.kwargs)

        elif isinstance(parentID, float):
            assert self.devices[parentID] # FIXME: use another error (e.g. WrongIDError)

            self.devices[parentID].openDevice(eval(config.deviceName),
                input = config.relationship[2], *config.args, **config.kwargs)
            device = self.devices[parentID].getDevice(input = config.relationship[2])
            self.configs[parentID].relationship[1][id] = config.relationship[2]

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

        if isinstance(config.relationship[0], str):
            import copy
            relCopy = copy.copy(config.relationship[1])
            # prevent RuntimeError: dictionary changed size during iteration
            
            for subdeviceID, inputNumber in relCopy.iteritems():
                self.closeDevice(subdeviceID)

            del(self.devices[deviceID])
            del(self.configs[deviceID])

        elif isinstance(config.relationship[0], float):
            parentID = config.relationship[0]
            self.getDevice(parentID).closeDevice(input=config.relationship[2])
            del(self.devices[deviceID])
            del(self.configs[deviceID])
            del(self.configs[parentID].relationship[1][deviceID])

    def closeEmptyMultiboxDevices(self):
        """Close all MultiboxDevices without subDevices."""

        for i in self.getAllDeviceIDs():
            config = self.configs[i]
            if len(config.relationship[1]) == 0 and config.deviceName == "XLS200":
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

    relationship = () # ("parent" deviceID or rs232 port, {"subdeviceID":inputNumber}, inputNumber)
    deviceName = None
    args = ()
    kwargs = {}

    def __init__(self, relationship, deviceName, *args, **kwargs):
        """Create a DeviceConfig object of a relationship tuple and deviceName.
        
        :param relationship: (parent deviceID or rs232 port, {"subdeviceID":inputNumber}, inputNumber)
        :type relationship: Tuple
        :param deviceName: DeviceName
        :type deviceName: String
        :returns: deviceID of opened device.
        :rtype: deviceID

        """

        assert deviceName in DeviceManager._validDevices
        assert isinstance(relationship, tuple) and (len(relationship) == 2 or len(relationship) == 3)
        assert isinstance(relationship[0], str) or isinstance(relationship[0], float)
        assert isinstance(relationship[1], dict)

        self.relationship = relationship
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
                if isinstance(config.relationship[0], str):
                    if len(config.relationship[1]) == 0 and config.deviceName != "XLS200":
                            # If there are no subdevices and it's not an "empty" Multiboxdevice
                        rv = self.devices[key].getRawValue()
                        if rv:
                            self.rawValues[key] = rv
                        else:
                            pass

                    else:
                        for subID, subInput in config.relationship[1].iteritems():
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

if __name__ == '__main__':
    dm = DeviceManager()

    a = DeviceConfig(("/dev/ttyUSB0", {}), "XLS200")
    ida = dm.openWithConfig(a)
    b = DeviceConfig((ida, {}, 2), "TecpelDMM8061")
    idb = dm.openWithConfig(b)
    c = DeviceConfig((ida, {}, 3), "BS600", typeOfValue="stable")
    idc = dm.openWithConfig(c)
    
    dm.start()

    import time

    time.sleep(3)

    while True:
        time.sleep(0.5)
        rv = dm.getCalibratedLastRawValue(idb, ((pow(10,-6), 21), (4 * pow(10,-6), 30)), unit="°C")
        rvc  = dm.getLastRawValue(idc)
        print(str(rv.getDisplayedValue() * rv.getFactor()) + " " + rv.getUnit())
        print(str(rvc.getDisplayedValue() * rvc.getFactor()) + " " + rvc.getUnit())