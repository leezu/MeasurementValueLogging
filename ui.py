import sys
from PyQt4 import QtCore, QtGui, uic
from devices.devicemanager import DeviceManager, DeviceConfig

class NewDeviceDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/newDeviceDialog.ui", self)


class Xls200Dialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/xls200Dialog.ui", self)

        settings = QtCore.QSettings()


class SettingsDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/settingsDialog.ui", self)

        self.pathButton.clicked.connect(self.openFile)
        self.saveButton.clicked.connect(self.save)

        self.settings = QtCore.QSettings()

        self.path.setText(self.settings.value("office/path", "").toString())
        self.loggingInterval.setValue(self.settings.value("logging/interval", 1).toInt()[0])

    def openFile(self):
        import os
        popup = QtGui.QFileDialog()
        self.path.setText(popup.getOpenFileName(self, "Search Office", os.path.expanduser("~"), ""))

    def save(self):
        self.settings.setValue("office/path", self.path.text())
        self.settings.setValue("logging/interval", self.loggingInterval.value())


class DisplayWidget(QtGui.QWidget):
    def __init__(self, deviceID, dm, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = uic.loadUi("ui/displayWidget.ui", self)

        self.deviceID = deviceID
        self.unit = ""
        self.calibration = (1.0, 0.0)
        self.dm = dm
        self.deviceName.setText(str(dm.getDevice(self.deviceID)))

        self.settingsButton.clicked.connect(self.deviceSettings)

    def deviceSettings(self):
        popup = DeviceSettingsDialog(self.deviceID, self.dm)

        if isinstance(self.calibration[0], float):
            popup.slope.setValue(self.calibration[0])
            popup.intercept.setValue(self.calibration[1])
            popup.slopeInterceptButton.setChecked(True)

        elif len(self.calibration[0]) == 2:
            popup.is1.setValue(self.calibration[0][0])
            popup.should1.setValue(self.calibration[0][1])
            popup.is2.setValue(self.calibration[1][0])
            popup.should2.setValue(self.calibration[1][1])
            popup.valuesButton.setChecked(True)

        popup.unit.setText(self.unit)

        popup.exec_()

        if popup.valuesButton.isChecked():
            self.calibration = ((popup.is1.value(), popup.should1.value()), (popup.is2.value(), popup.should2.value()))

        elif popup.slopeInterceptButton.isChecked():
            self.calibration = (popup.slope.value(), popup.intercept.value())

        self.unit = str(popup.unit.text())


class DeviceSettingsDialog(QtGui.QDialog):
    def __init__(self, deviceID, dm, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/deviceSettingsDialog.ui", self)

        self.deviceID = deviceID
        self.dm = dm

        self.get1.clicked.connect(self.setCurrentValue1)
        self.get2.clicked.connect(self.setCurrentValue2)

    def setCurrentValue1(self):
        rv = self.dm.getLastRawValue(self.deviceID)
        self.is1.setValue(rv.getDisplayedValue())

    def setCurrentValue2(self):
        rv = self.dm.getLastRawValue(self.deviceID)
        self.is2.setValue(rv.getDisplayedValue())


class MainWindow(QtGui.QMainWindow):
    dm = None
    deviceIDs = []
    displayWidgets = []

    log = False
    tmpfile = None
    starttime = 0
    lasttime = 0
    loggingInterval = 3
    pathToLogFile = None

    officePath = None

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = uic.loadUi("ui/mainWindow.ui", self)

        self.measurementButton.clicked.connect(self.startStopMeasurement)
        self.loggingButton.clicked.connect(self.startStopLogging)
        self.saveButton.clicked.connect(self.saveLog)
        self.addDeviceButton.clicked.connect(self.addDevice)
        self.openButton.clicked.connect(self.openLog)

        self.actionSettings.triggered.connect(self.settingsDialog)

        self.dm = DeviceManager()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateValues)

        self.settings = QtCore.QSettings()
        self.officePath = str(self.settings.value("office/path", "").toString())
        self.loggingInterval = int(self.settings.value("logging/interval", 1).toInt()[0])

    def settingsDialog(self):
        popup = SettingsDialog()
        popup.exec_()

        self.officePath = str(self.settings.value("office/path", "").toString())
        self.loggingInterval = int(self.settings.value("logging/interval", 1).toInt()[0])

    def openLog(self):
        import subprocess

        if self.pathToLogFile:
            subprocess.call(self.officePath.split() + self.pathToLogFile.split())

    def addDevice(self):
        validDevices = self.dm.getValidDevices()

        popup = NewDeviceDialog()
        popup.deviceComboBox.addItems(validDevices)
        popup.portComboBox.addItems(self.dm.getAvailiablePorts())
        popup.exec_()

        if popup.result():
            device = str(popup.deviceComboBox.currentText())
            port = str(popup.portComboBox.currentText())

            if device == "XLS200":
                xls200Popup = Xls200Dialog()
                for i in (xls200Popup.subdevice1ComboBox,
                        xls200Popup.subdevice2ComboBox, xls200Popup.subdevice3ComboBox):
                    i.addItems([""] + validDevices)

                xls200Popup.exec_()

                if xls200Popup.result():
                    xls200ID = self.dm.openWithConfig(DeviceConfig((port, {}), device))
                    sub1 = str(xls200Popup.subdevice1ComboBox.currentText())
                    sub2 = str(xls200Popup.subdevice2ComboBox.currentText())
                    sub3 = str(xls200Popup.subdevice3ComboBox.currentText())
                    
                    if sub1 != "":
                            deviceID = self.dm.openWithConfig(DeviceConfig((xls200ID, {}, 1), sub1))
                            self.deviceIDs.append(deviceID)

                            sub1Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub1Widget)
                            self.displayWidgets.append(sub1Widget)

                    if sub2 != "":
                            deviceID = self.dm.openWithConfig(DeviceConfig((xls200ID, {}, 2), sub2))
                            self.deviceIDs.append(deviceID)

                            sub2Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub2Widget)
                            self.displayWidgets.append(sub2Widget)

                    if sub3 != "":
                            deviceID = self.dm.openWithConfig(DeviceConfig((xls200ID, {}, 3), sub3))
                            self.deviceIDs.append(deviceID)

                            sub3Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub3Widget)
                            self.displayWidgets.append(sub3Widget)

            else:
                deviceID = self.dm.openWithConfig(DeviceConfig((port, {}), device))
                self.deviceIDs.append(deviceID)

                deviceWidget = DisplayWidget(deviceID, self.dm)
                self.verticalLayout.addWidget(deviceWidget)
                self.displayWidgets.append(deviceWidget)

    def startStopMeasurement(self):
        if self.dm.getStatus() == False:
            self.dm.start()
            self.timer.start(500)
            self.measurementButton.setText("Stop")

        elif self.dm.getStatus() == True:
            self.timer.stop()
            self.dm.stop()
            self.measurementButton.setText("Start")

    def startStopLogging(self):
        import time
        import tempfile

        if self.log == False:
            self.tmpfile = tempfile.TemporaryFile()
            self.starttime = time.time()
            self.log = True
            self.loggingButton.setText("Stop logging")

        elif self.log:
            self.log = False
            self.loggingButton.setText("Start logging")

    def saveLog(self):
        import os

        if self.tmpfile:
	        popup = QtGui.QFileDialog()
	        filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", os.path.expanduser("~"), "")

	        if filename[-4:] != ".csv":
	            filename += ".csv"

	        self.tmpfile.seek(0, 0)
	        with open(filename, 'w') as stream:
	            stream.write(self.tmpfile.read())
	        self.pathToLogFile = str(filename)

    def updateValues(self):
        import time

        for i in self.displayWidgets:
            unit = None
            if i.unit != "":
                unit = i.unit

            rv = self.dm.getCalibratedLastRawValue(i.deviceID, i.calibration, i.unit)
            i.lcdNumber.display(rv.getDisplayedValue())
            i.label.setText(str(rv.getFactor("prefix") + rv.getUnit()).decode('utf-8'))
            # python3 incompatibility: in python3 .decode() is not needed anymore
            
            if self.log and ((time.time() - self.lasttime) > self.loggingInterval):
                self.tmpfile.write(str(rv.getDisplayedValue() * rv.getFactor()) + ",")

        if self.log and ((time.time() - self.lasttime) > self.loggingInterval):
            self.tmpfile.write("\n")
            self.lasttime = time.time()
        

class App(QtGui.QApplication):
    def __init__(self, *args, **kwargs):
        QtGui.QApplication.__init__(self, *args, **kwargs)
        self.main = MainWindow()
        self.connect(self, QtCore.SIGNAL("lastWindowClosed()"), self.byebye )
        self.main.show()

    def byebye(self):
        self.exit(0)

if __name__ == "__main__":
    App(sys.argv).exec_()