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
import devices as devicesModule
import si
import serial
import time
import logging
import random
import copy
import serial.tools.list_ports

class DeviceManager(object):
    """The DeviceManager manages devices.

    It provides methods to add or delete devices,
    get their most recent measurement values and various other things.

    """

    _running = False
    _stopEvent = None
    _thread = None

    _iterator = None

    devices = {}
    configs = {}
    rawValues = {}

    def __init__(self):
        self._iterator = self._getIterator()
        self._start()

    def _getIterator(self):
        i = random.getrandbits(32)
        while True:
            yield i
            i += 1

    def _getUniqueID(self):
        return next(self._iterator)

    def _pause(function):
        def decoratedFunction(self, *args, **kwargs):
            self._stop()
            returnValue = function(self, *args, **kwargs)
            self._start()

            return returnValue

        return decoratedFunction

    def _updateRawValues(self):
        if self._running:
            self.rawValues = self._thread.rawValues
        else:
            logging.warn("GetValuesThread not running. Can't update values.\n")

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
            logging.warning("ZeroDivisionError while computing the slope. Setting slope to 1")
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

        return deviceName in devicesModule.deviceClassNames

    def getValidDevices(self):
        """Returns a list of valid deviceNames.
        
        :returns: List of valid deviceNames
        :rtype: List of strings

        """
        names = list(devicesModule.deviceClassNames)
        names.sort()
        return names

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

        return self._openWithConfig({"deviceName":deviceName,
                                    "parent":serialPort,
                                    "args":args,
                                    "kwargs":kwargs})

    def openSubdevice(self, deviceName, parentDeviceID, inputNumber, *args, **kwargs):
        """Open a device as subdevice of the device with parentDeviceID.
        
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

        return self._openWithConfig({"deviceName":deviceName,
                                    "parent":parentDeviceID,
                                    "inputNumber":inputNumber,
                                    "args":args,
                                    "kwargs":kwargs})

    @_pause
    def _openWithConfig(self, config):
        """Open a device with a config dictionary. Returns a deviceID.

        :param config: Config dictionary
        :type config: Dictionary
        :returns: DeviceID of opened device
        :rtype: :class:`DeviceID`

        """
        
        assert self._running == False # FIXME: use another error
        assert config["deviceName"] in devicesModule.deviceClassNames

        id = self._getUniqueID()

        config["subDevices"] = {}

        try:
            if isinstance(config["parent"], str):
                device = eval("devicesModule." + config["deviceName"]).openRS232(config["parent"],
                    *config["args"], **config["kwargs"])

            else:
                assert self.devices[config["parent"]] # FIXME: use another error (e.g. WrongIDError)

                self.devices[config["parent"]].openDevice(eval("devicesModule." + config["deviceName"]),
                    input = config["inputNumber"], *config["args"], **config["kwargs"])
                device = self.devices[config["parent"]].getDevice(input = config["inputNumber"])
                self.configs[config["parent"]]["subDevices"][id] = config["inputNumber"]

            self.devices[id] = device
            self.configs[id] = config

            return id

        except serial.serialutil.SerialException:
            logging.error("Caught SerialException: Could not configure port: (5, 'Input/output error')")
            return None

    @_pause
    def closeDevice(self, deviceID):
        """Close device with deviceID.
        
        :param deviceID: DeviceID of device to close
        :type deviceID: DeviceID

        """

        assert self._running == False # FIXME: use another error

        config = self.configs[deviceID]

        if isinstance(config["parent"], str):
            relCopy = copy.copy(config["subDevices"])
            # prevent RuntimeError: dictionary changed size during iteration
            
            for subdeviceID, inputNumber in relCopy.iteritems():
                self.closeDevice(subdeviceID)

            self.devices[deviceID].close()

            del(self.devices[deviceID])
            del(self.configs[deviceID])

        else:
            parentID = config["parent"]
            self.getDevice(parentID).closeDevice(input=config["inputNumber"])
            del(self.devices[deviceID])
            del(self.configs[deviceID])
            del(self.configs[parentID]["subDevices"][deviceID])

    def closeEmptyMultiboxDevices(self):
        """Close all MultiboxDevices without subDevices."""

        for i in self.getAllDeviceIDs():
            config = self.configs[i]
            if len(config["subDevices"]) == 0 and config["deviceName"] == "XLS200":
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
            logging.info("No value yet. Device: %s %s", deviceID, self.getDevice(deviceID))
            return devicesModule.NullValue()

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

        class __Value(devicesModule.Value):
            value = None
            unit = None

            def getDisplayedValue(self):
                x = si.getNumberPrefix(self.value)
                return x[0]

            def getUnit(self):
                return self.unit

            def getFactor(self, type="value"):
                x = si.getNumberPrefix(self.value)
                
                if type == "value":
                    return si.getFactor(x[1])
                elif type == "prefix":
                    return x[1]

        rv = self.getLastRawValue(deviceID)
        if rv == None: return None

        result = __Value()

        result.value = linearFunction(rv.getDisplayedValue() * rv.getFactor())
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

    def _start(self):
        """Start the DeviceManager."""

        if self._running == False:
            self._stopEvent = threading.Event()
            self._thread = _GetValuesThread(self._stopEvent,
                self.devices, self.configs)
            self._thread.start()
            self._running = True

    def _stop(self):
        """Stop the DeviceManager."""

        if self._running == True:
            self._stopEvent.set()
            self._thread.join()
            self._thread = None
            self._stopEvent = None
            self._running = False


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
            self.rawValues[key] = devicesModule.NullValue()

    def run(self):
        while not self.stop_event.is_set():
            self.updateValue()
            time.sleep(0.2) # Prevent 100% CPU usage

    def updateValue(self):
        # python3 incompatibility: iteritems
        for deviceID, config in self.configs.iteritems():
            if self.stop_event.is_set():
                break

            if isinstance(config["parent"], str):
                rv = self.devices[deviceID].getRawValue()
                if rv:
                    self.rawValues[deviceID] = rv
                else:
                    pass

            else:
                rv = self.devices[config["parent"]].getRawValue(config["inputNumber"])
                if rv:
                    self.rawValues[deviceID] = rv
                else:
                    pass