# Python Measurement Value Logging Software.
# Graphical User Interface
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

import sys
import pkgutil
import time
import os
import tempfile
import subprocess
from PyQt4 import QtCore, QtGui, uic

from devices.devicemanager import DeviceManager
from devices import si
import ui_data.qr

class NewDeviceDialog(QtGui.QDialog):
    """Dialog to add new devices."""

    def __init__(self, dm, parent=None):
        """

        :param dm: DeviceManager
        :type dm: DeviceManager

        """

        QtGui.QDialog.__init__(self, parent)
        qfile = QtCore.QFile(":/ui/newDeviceDialog.ui")
        qfile.open(QtCore.QIODevice.ReadOnly)
        self.ui = uic.loadUi(qfile, self)
        self.dm = dm

        self.deviceComboBox.addItems(self.dm.getValidDevices())
        self.portComboBox.addItems(self.dm.getAvailiablePorts())


class DoReallyDialog(QtGui.QDialog):
    """Dialog to ask whether a user wants really to do something."""

    def __init__(self, title, text, parent=None):
        """

        :param title: Dialog title
        :type title: String
        :param text: Dialog text
        :type text: String

        """

        QtGui.QDialog.__init__(self, parent)
        qfile = QtCore.QFile(":/ui/doReallyDialog.ui")
        qfile.open(QtCore.QIODevice.ReadOnly)
        self.ui = uic.loadUi(qfile, self)

        self.windowTitle = title
        self.label.setText(text)


class Xls200Dialog(QtGui.QDialog):
    """Dialog to chose XLS200 subdevices."""

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        qfile = QtCore.QFile(":/ui/xls200Dialog.ui")
        qfile.open(QtCore.QIODevice.ReadOnly)
        self.ui = uic.loadUi(qfile, self)

        settings = QtCore.QSettings()


class SettingsDialog(QtGui.QDialog):
    """The general settings dialog."""

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        qfile = QtCore.QFile(":/ui/settingsDialog.ui")
        qfile.open(QtCore.QIODevice.ReadOnly)
        self.ui = uic.loadUi(qfile, self)

        self.pathButton.clicked.connect(self.openFile)
        self.saveButton.clicked.connect(self.save)

        self.settings = QtCore.QSettings()

        self.path.setText(self.settings.value("office/path", "").toString())
        self.languageComboBox.setCurrentIndex(self.settings.value("i18n", -1).toInt()[0])

    def openFile(self):
        """Open a QFileDialog and save the path."""

        popup = QtGui.QFileDialog()
        self.path.setText(popup.getOpenFileName(self, self.tr("Search Office"), os.path.expanduser("~"), ""))

    def save(self):
        """Save the settings to QSettings."""

        self.settings.setValue("office/path", self.path.text())
        self.settings.setValue("i18n", self.languageComboBox.currentIndex())


class DisplayWidget(QtGui.QWidget):
    """Widget containing a lcd display and buttons to modify or delete a device."""
    calibrationType = 1 # 0: two values calibration, 1: slope and intercept calibration
    twoValueCalibration = (0.0, 0.0), (1.0, 1.0)
    slopeInterceptCalibration = 1.0, 0.0

    siNames = si.getSiNames("normal")

    is1PrefixIndex = siNames.index("") # QComboBox Index
    should1PrefixIndex = siNames.index("") # QComboBox Index
    is2PrefixIndex = siNames.index("") # QComboBox Index
    should2PrefixIndex = siNames.index("") # QComboBox Index

    is1 = 0
    should1 = 0
    is2 = 1
    should2 = 1

    calibration = slopeInterceptCalibration # either slopeInterceptCalibration or twoValueCalibration
    unit = QtCore.QString()

    def __init__(self, deviceID, dm, parent=None):
        """

        :param deviceID: DeviceID
        :type deviceID: DeviceID
        :param dm: DeviceManager
        :type dm: DeviceManager

        """

        QtGui.QWidget.__init__(self, parent)
        qfile = QtCore.QFile(":/ui/displayWidget.ui")
        qfile.open(QtCore.QIODevice.ReadOnly)
        self.ui = uic.loadUi(qfile, self)

        self.deviceID = deviceID
        self.dm = dm
        self.deviceName.setText(str(dm.getDevice(self.deviceID)))

        self.settingsButton.clicked.connect(self.deviceSettings)
        self.deleteButton.clicked.connect(self.close)

        self.settingsButton.setIcon(QtGui.QIcon(":/images/settings.png"))
        self.deleteButton.setIcon(QtGui.QIcon(":/images/close.png"))

    def deviceSettings(self):
        """Open a DeviceSettingsDialog."""

        popup = DeviceSettingsDialog(self.deviceID, self.dm)

        popup.slope.setValue(self.slopeInterceptCalibration[0])
        popup.intercept.setValue(self.slopeInterceptCalibration[1])
        popup.is1.setValue(self.is1)
        popup.should1.setValue(self.should1)
        popup.is2.setValue(self.is2)
        popup.should2.setValue(self.should2)

        # Add prefixes to combobox
        for i in [popup.is1Prefix, popup.should1Prefix, popup.is2Prefix, popup.should2Prefix]:
            i.clear()
            i.addItems(self.siNames)

        popup.is1Prefix.setCurrentIndex(self.is1PrefixIndex)
        popup.should1Prefix.setCurrentIndex(self.should1PrefixIndex)
        popup.is2Prefix.setCurrentIndex(self.is2PrefixIndex)
        popup.should2Prefix.setCurrentIndex(self.should2PrefixIndex)

        if self.calibrationType == 1:
            popup.slopeInterceptButton.setChecked(True)
        elif self.calibrationType == 0:
            popup.valuesButton.setChecked(True)

        popup.unit.setText(self.unit)

        popup.exec_()

        self.twoValueCalibration = popup.twoValueCalibration
        self.slopeInterceptCalibration = popup.slopeInterceptCalibration

        self.is1 = popup.is1.value()
        self.should1 = popup.should1.value()
        self.is2 = popup.is2.value()
        self.should2 = popup.should2.value()

        self.is1PrefixIndex = popup.is1Prefix.currentIndex()
        self.should1PrefixIndex = popup.should1Prefix.currentIndex()
        self.is2PrefixIndex = popup.is2Prefix.currentIndex()
        self.should2PrefixIndex = popup.should2Prefix.currentIndex()

        if popup.slopeInterceptButton.isChecked():
            self.calibrationType = 1
            self.calibration = self.slopeInterceptCalibration
        elif popup.valuesButton.isChecked():
            self.calibrationType = 0
            self.calibration = self.twoValueCalibration

        self.unit = popup.unit.text()

    def delete(self):
        """Delete Widget."""

        self.deleteLater()

    def close(self):
        """Close the device."""

        self.dm.closeDevice(self.deviceID)


class DeviceSettingsDialog(QtGui.QDialog):
    """Settings dialog for device specific settings."""

    def __init__(self, deviceID, dm, parent=None):
        """

        :param deviceID: DeviceID
        :type deviceID: DeviceID
        :param dm: DeviceManager
        :type dm: DeviceManager

        """
        QtGui.QDialog.__init__(self, parent)
        qfile = QtCore.QFile(":/ui/deviceSettingsDialog.ui")
        qfile.open(QtCore.QIODevice.ReadOnly)
        self.ui = uic.loadUi(qfile, self)

        self.deviceID = deviceID
        self.dm = dm

        self.settings = QtCore.QSettings()

        self.get1.clicked.connect(self.setCurrentValue1)
        self.get2.clicked.connect(self.setCurrentValue2)
        self.saveButton.clicked.connect(self.save)
        self.loadButton.clicked.connect(self.load)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        self.finished.connect(self._finish)

    def _finish(self):
        self.timer.stop()

    def update(self):
        self.twoValueCalibration = ((self.is1.value() * si.getFactor(str(self.is1Prefix.currentText())),
                self.should1.value()  * si.getFactor(str(self.should1Prefix.currentText()))),
            (self.is2.value() * si.getFactor(str(self.is2Prefix.currentText())), 
                self.should2.value() * si.getFactor(str(self.should2Prefix.currentText()))))

        self.slopeInterceptCalibration = self.slope.value(), self.intercept.value()
        
        if self.slopeInterceptButton.isChecked():
            self.calibration = self.slopeInterceptCalibration
        elif self.valuesButton.isChecked():
            self.calibration = self.twoValueCalibration

        crv = self.dm.getCalibratedLastRawValue(self.deviceID, self.calibration, self.unit)
        self.calibratedLabel.setText(str(crv.getDisplayedValue() * crv.getFactor()))

        rv = self.dm.getLastRawValue(self.deviceID)
        self.normalLabel.setText(str(rv.getDisplayedValue() * rv.getFactor()))


    def save(self):
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "is1", 
            self.is1.value())
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "should1", 
            self.should1.value())
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "is2", 
            self.is2.value())
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "should2", 
            self.should2.value())
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "is1PrefixIndex", 
            self.is1Prefix.currentIndex())
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "should1PrefixIndex", 
            self.should1Prefix.currentIndex())
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "is2PrefixIndex", 
            self.is2Prefix.currentIndex())
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "should2PrefixIndex", 
            self.should2Prefix.currentIndex())

        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "slope",
            self.slope.value())
        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "intercept",
            self.intercept.value())

        self.settings.setValue("calibration/" +
            self.slotComboBox.currentText() + "unit",
            self.unit.text())

    def load(self):
        allItems = [self.is1Prefix.itemText(i) for i in range(self.is1Prefix.count())]
        emptyStringIndex = allItems.index("")

        self.is1.setValue(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "is1", 0).toInt()[0])
        self.should1.setValue(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "should1", 0).toInt()[0])
        self.is2.setValue(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "is2", 1).toInt()[0])
        self.should2.setValue(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "should2", 1).toInt()[0])
        self.is1Prefix.setCurrentIndex(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "is1PrefixIndex", emptyStringIndex).toInt()[0])
        self.should1Prefix.setCurrentIndex(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "should1PrefixIndex", emptyStringIndex).toInt()[0])
        self.is2Prefix.setCurrentIndex(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "is2PrefixIndex", emptyStringIndex).toInt()[0])
        self.should2Prefix.setCurrentIndex(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "should2PrefixIndex", emptyStringIndex).toInt()[0])

        self.slope.setValue(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "slope", 1).toInt()[0])
        self.intercept.setValue(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "intercept", 0).toInt()[0])

        self.intercept.setValue(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "unit", 0).toInt()[0])

        self.unit.setText(self.settings.value("calibration/" +
            self.slotComboBox.currentText() + "unit", "").toString())

    def setCurrentValue1(self):
        """Get current displayedValue from Device."""

        rv = self.dm.getLastRawValue(self.deviceID)
        self.is1.setValue(rv.getDisplayedValue())

        name = si.getName(rv.getFactor())
        index = self.is1Prefix.findText(name)
        self.is1Prefix.setCurrentIndex(index)
        self.should1Prefix.setCurrentIndex(index)

    def setCurrentValue2(self):
        """Get current displayedValue from Device."""

        rv = self.dm.getLastRawValue(self.deviceID)
        self.is2.setValue(rv.getDisplayedValue())

        name = si.getName(rv.getFactor())
        index = self.is1Prefix.findText(name)
        self.is2Prefix.setCurrentIndex(index)
        self.should2Prefix.setCurrentIndex(index)


class MainWindow(QtGui.QMainWindow):
    """Main window."""

    dm = None
    displayWidgets = {}

    log = False
    tmpfile = None
    starttime = 0
    lasttime = 0
    pathToLogFile = None

    officePath = None

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        qfile = QtCore.QFile(":/ui/mainWindow.ui")
        qfile.open(QtCore.QIODevice.ReadOnly)
        self.ui = uic.loadUi(qfile, self)

        self.settings = QtCore.QSettings()

        self.loggingButton.clicked.connect(self.startStopLogging)
        self.saveButton.clicked.connect(self.saveLog)
        self.addDeviceButton.clicked.connect(self.addDevice)
        self.openButton.clicked.connect(self.openLog)

        self.actionSettings.triggered.connect(self.settingsDialog)

        self.dm = DeviceManager()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        self.officePath = str(self.settings.value("office/path", "").toString())

        self.loggingInterval.setValue(self.settings.value("logging/interval", 1).toInt()[0])
        self.loggingInterval.valueChanged.connect(self.saveLoggingInterval)

    def saveLoggingInterval(self):
        self.settings.setValue("logging/interval", self.loggingInterval.value())

    def settingsDialog(self):
        """Open a SettingsDialog."""

        popup = SettingsDialog()
        popup.exec_()

        self.officePath = str(self.settings.value("office/path", "").toString())

    def openLog(self):
        """Open last log with office."""
        
        if self.pathToLogFile:
            subprocess.call('"' + self.officePath + '"' + ' ' + 
                '"' + self.pathToLogFile + '"', shell=True)
                    # FIXME: security flaw: shell=True 
        else:
            popup = DoReallyDialog(self.tr("Warning"),
                self.tr("You have not saved a log yet."))
            popup.exec_()

    def addDevice(self):
        """Open a NewDeviceDialog."""
        
        popup = NewDeviceDialog(self.dm)
        popup.exec_()

        if popup.result():
            device = str(popup.deviceComboBox.currentText())
            port = str(popup.portComboBox.currentText())

            if device == "XLS200":
                xls200Popup = Xls200Dialog()
                
                validDevices = self.dm.getValidDevices()
                validDevices.remove("XLS200") # Chaining XLS200 devices is not supported

                for i in (xls200Popup.subdevice1ComboBox,
                        xls200Popup.subdevice2ComboBox, xls200Popup.subdevice3ComboBox):
                    i.addItems([self.tr("No device")] + validDevices)

                xls200Popup.exec_()

                if xls200Popup.result():
                    xls200ID = self.dm.openDevice(device, port)

                    if xls200ID:
                        
                        if xls200Popup.subdevice1ComboBox.currentIndex() != 0:
                            sub1 = unicode(xls200Popup.subdevice1ComboBox.currentText())
                            deviceID = self.dm.openSubdevice(sub1, xls200ID, 1)
                            sub1Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub1Widget)
                            self.displayWidgets[deviceID] = sub1Widget

                        if xls200Popup.subdevice2ComboBox.currentIndex() != 0:
                            sub2 = unicode(xls200Popup.subdevice2ComboBox.currentText())
                            deviceID = self.dm.openSubdevice(sub2, xls200ID, 2)
                            sub2Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub2Widget)
                            self.displayWidgets[deviceID] = sub2Widget

                        if xls200Popup.subdevice3ComboBox.currentIndex() != 0:
                            sub3 = unicode(xls200Popup.subdevice3ComboBox.currentText())
                            deviceID = self.dm.openSubdevice(sub3, xls200ID, 3)
                            sub3Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub3Widget)
                            self.displayWidgets[deviceID] = sub3Widget

            else:
                deviceID = self.dm.openDevice(device, port)

                if deviceID:
                    deviceWidget = DisplayWidget(deviceID, self.dm)
                    self.verticalLayout.addWidget(deviceWidget)
                    self.displayWidgets[deviceID] = deviceWidget

    def startStopLogging(self):
        """Start/Stop logging."""

        if self.log == False:
            if self.tmpfile:
                popup = DoReallyDialog(self.tr("Overwrite last log"),
                    self.tr("Do you really want to overwrite the last (unsaved) log?\n")+
                    self.tr("If not, please cancel and save it first."))
                popup.exec_()

                if popup.result() == 0:
                    return

            self.tmpfile = tempfile.TemporaryFile()
            self.starttime = time.time()
            self.log = True
            self.loggingButton.setText(self.tr("Stop logging"))

        elif self.log:
            self.log = False
            self.loggingButton.setText(self.tr("Start logging"))

    def saveLog(self):
        """Save last log to file."""

        if self.tmpfile:
            popup = QtGui.QFileDialog()
            filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
                os.path.expanduser("~/" + str(self.tr("log", "Default filename of the exported log")) + ".csv"),
                "CSV (*.csv)")

            if filename != "":
                self.tmpfile.seek(0, 0)
                with open(filename, 'w') as stream:
                    stream.write(self.tmpfile.read())
                self.pathToLogFile = str(filename)
        else:
            popup = DoReallyDialog(self.tr("Warning"),
                self.tr("You first have to log something, to save it."))
            popup.exec_()

            if popup.result() == 0:
                return

    def update(self):
        """Update the displayWidgets and, when logging enabled log."""
        
        # python3 incompatibility: .iteritems()
        # Delete unnecessary widgets
        deviceIDsToBeDeleted = []
        for deviceID, widget in self.displayWidgets.iteritems():
            if deviceID not in self.dm.getAllDeviceIDs():
                deviceIDsToBeDeleted.append(deviceID)
        
        self.dm.closeEmptyMultiboxDevices()

        for i in deviceIDsToBeDeleted:
            self.displayWidgets[i].delete()
            del(self.displayWidgets[i])

        # update widgets
        for deviceID, widget in self.displayWidgets.iteritems():
            unit = None
            if widget.unit != "":
                unit = widget.unit

            rv = self.dm.getCalibratedLastRawValue(widget.deviceID, widget.calibration, widget.unit)
            widget.lcdNumber.display(rv.getDisplayedValue())
            widget.label.setText(rv.getFactor("prefix") + rv.getUnit())
        
        # log    
        if self.log and ((time.time() - self.lasttime) > self.loggingInterval.value()):
            for deviceID, widget in self.displayWidgets.iteritems():
                unit = None
                if widget.unit != "":
                    unit = widget.unit
                rv = self.dm.getCalibratedLastRawValue(widget.deviceID, widget.calibration, widget.unit)
                self.tmpfile.write(str(rv.getDisplayedValue() * rv.getFactor()) + ",")

            self.tmpfile.write("\n")
            self.lasttime = time.time()
        

class App(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        QtGui.QApplication.__init__(self, *args, **kwargs)
        self.connect(self, QtCore.SIGNAL("lastWindowClosed()"), self.byebye )

    def setup(self):
        self.main = MainWindow()
        self.main.show()

    def byebye(self):
        self.exit(0)

def main():
    app = App(sys.argv)

    QtCore.QCoreApplication.setOrganizationName("Lausen")
    QtCore.QCoreApplication.setOrganizationDomain("lausen.nl")
    QtCore.QCoreApplication.setApplicationName("MeasurementValueLogging")

    translator = QtCore.QTranslator()
    langVal = QtCore.QSettings().value("i18n", -1).toInt()[0]
    
    if langVal == -1:
        locale = QtCore.QLocale.system().name()
        if translator.load(":/i18n/" + locale + "qm"):
            app.installTranslator(translator)
    if langVal == 1:
        translator.load(":/i18n/de.qm")
        app.installTranslator(translator)

    app.setup()
    app.exec_()

if __name__ == "__main__":
    main()