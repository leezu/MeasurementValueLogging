import sys
from PyQt4 import QtCore, QtGui, uic
from devices.devicemanager import DeviceManager, DeviceConfig

class NewDeviceDialog(QtGui.QDialog):
    def __init__(self, dm, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/newDeviceDialog.ui", self)
        self.dm = dm

        self.deviceComboBox.addItems(self.dm.getValidDevices())
        self.portComboBox.addItems(self.dm.getAvailiablePorts())


class DoReallyDialog(QtGui.QDialog):
    def __init__(self, title, text, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/doReallyDialog.ui", self)

        self.windowTitle = title
        self.label.setText(text)


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
        self.languageComboBox.setCurrentIndex(self.settings.value("i18n", -1).toInt()[0])

    def openFile(self):
        import os
        popup = QtGui.QFileDialog()
        self.path.setText(popup.getOpenFileName(self, self.tr("Search Office"), os.path.expanduser("~"), ""))

    def save(self):
        self.settings.setValue("office/path", self.path.text())
        self.settings.setValue("logging/interval", self.loggingInterval.value())
        self.settings.setValue("i18n", self.languageComboBox.currentIndex())


class DevicemanagerDialog(QtGui.QDialog):
    ids = []

    def __init__(self, dm, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui/devicemanagerDialog.ui", self)
        self.dm = dm

        self.deleteButton.clicked.connect(self.deleteItem)

        self.refreshList()

    def refreshList(self):
        self.ids = self.dm.getAllDeviceIDs()

        self.listWidget.clear()

        for id in self.ids:
            item = QtGui.QListWidgetItem(str(self.dm.getDevice(id)))
            self.listWidget.addItem(item)

    def deleteItem(self):
        row = self.listWidget.currentRow()

        self.dm.closeDevice(self.ids[row])

        self.refreshList()


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
        self.deleteButton.clicked.connect(self.close)

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

    def delete(self):
        self.deleteLater()

    def close(self):
        if self.dm.getStatus() == False:
            self.dm.closeDevice(self.deviceID)
        else:
            popup = DoReallyDialog(self.tr("Warning"),
                self.tr("You have to stop the measurement to delete a device."))
            popup.exec_()


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
    displayWidgets = {}

    running = False

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
        self.actionDevicemanager.triggered.connect(self.devicemanagerDialog)

        self.dm = DeviceManager()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

        self.settings = QtCore.QSettings()
        self.officePath = str(self.settings.value("office/path", "").toString())
        self.loggingInterval = int(self.settings.value("logging/interval", 1).toInt()[0])

    def settingsDialog(self):
        popup = SettingsDialog()
        popup.exec_()

        self.officePath = str(self.settings.value("office/path", "").toString())
        self.loggingInterval = int(self.settings.value("logging/interval", 1).toInt()[0])

    def devicemanagerDialog(self):
        if self.dm.getStatus() == False:
            popup = DevicemanagerDialog(self.dm)
            popup.exec_()
        else:
            popup = DoReallyDialog(self.tr("Warning"),
                self.tr("You have to stop the measurement to open the devicemanager."))
            popup.exec_()

    def openLog(self):
        import subprocess

        if self.pathToLogFile:
            subprocess.call(self.officePath.split() + self.pathToLogFile.split())
        else:
            popup = DoReallyDialog(self.tr("Warning"),
                self.tr("You have not saved a log yet."))
            popup.exec_()

    def addDevice(self):
        popup = NewDeviceDialog(self.dm)
        popup.exec_()

        if popup.result():
            device = str(popup.deviceComboBox.currentText())
            port = str(popup.portComboBox.currentText())

            if device == "XLS200":
                xls200Popup = Xls200Dialog()
                for i in (xls200Popup.subdevice1ComboBox,
                        xls200Popup.subdevice2ComboBox, xls200Popup.subdevice3ComboBox):
                    i.addItems([""] + self.dm.getValidDevices())

                xls200Popup.exec_()

                if xls200Popup.result():
                    xls200ID = self.dm.openWithConfig(DeviceConfig((port, {}), device))
                    sub1 = str(xls200Popup.subdevice1ComboBox.currentText())
                    sub2 = str(xls200Popup.subdevice2ComboBox.currentText())
                    sub3 = str(xls200Popup.subdevice3ComboBox.currentText())
                    
                    if sub1 != "":
                            deviceID = self.dm.openWithConfig(DeviceConfig((xls200ID, {}, 1), sub1))
                            sub1Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub1Widget)
                            self.displayWidgets[deviceID] = sub1Widget

                    if sub2 != "":
                            deviceID = self.dm.openWithConfig(DeviceConfig((xls200ID, {}, 2), sub2))
                            sub2Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub2Widget)
                            self.displayWidgets[deviceID] = sub2Widget

                    if sub3 != "":
                            deviceID = self.dm.openWithConfig(DeviceConfig((xls200ID, {}, 3), sub3))
                            sub3Widget = DisplayWidget(deviceID, self.dm)
                            self.verticalLayout.addWidget(sub3Widget)
                            self.displayWidgets[deviceID] = sub3Widget

            else:
                deviceID = self.dm.openWithConfig(DeviceConfig((port, {}), device))
                deviceWidget = DisplayWidget(deviceID, self.dm)
                self.verticalLayout.addWidget(deviceWidget)
                self.displayWidgets[deviceID] = deviceWidget

    def startStopMeasurement(self):
        if self.dm.getStatus() == False:
            self.dm.start()
            self.running = True
            self.measurementButton.setText(self.tr("Stop"))

        elif self.dm.getStatus() == True:
            self.dm.stop()
            self.running = False
            self.measurementButton.setText(self.tr("Start"))

    def startStopLogging(self):
        import time
        import tempfile

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
        import os

        if self.tmpfile:
	        popup = QtGui.QFileDialog()
	        filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"), os.path.expanduser("~"), "")

	        if filename[-4:] != ".csv":
	            filename += ".csv"

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
        import time
        # python3 incompatibility: .iteritems()
        # Delete unnecessary widgets
        deviceIDsToBeDeleted = []
        for deviceID, widget in self.displayWidgets.iteritems():
            if deviceID not in self.dm.getAllDeviceIDs():
                deviceIDsToBeDeleted.append(deviceID)
        for i in deviceIDsToBeDeleted:
            try:
                self.displayWidgets[i].delete()
                del(self.displayWidgets[i])
            except KeyError:
                # Some devices don't have widgets (e.g. xls200), so there are no widgets to be deleted
                pass

        if self.running:
            # update widgets
            for deviceID, widget in self.displayWidgets.iteritems():
                unit = None
                if widget.unit != "":
                    unit = widget.unit

                rv = self.dm.getCalibratedLastRawValue(widget.deviceID, widget.calibration, widget.unit)
                widget.lcdNumber.display(rv.getDisplayedValue())
                widget.label.setText(str(rv.getFactor("prefix") + rv.getUnit()).decode('utf-8'))
                # python3 incompatibility: in python3 .decode() is not needed anymore
            
            # log    
            if self.log and ((time.time() - self.lasttime) > self.loggingInterval):
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

if __name__ == "__main__":
    app = App(sys.argv)

    translator = QtCore.QTranslator()
    langVal = QtCore.QSettings().value("i18n", -1).toInt()[0]
    
    if langVal == -1:
        locale = QtCore.QLocale.system().name()
        if translator.load(locale, "i18n"):
            app.installTranslator(translator)
    if langVal == 1:
        translator.load("de", "i18n")
        app.installTranslator(translator)

    app.setup()
    app.exec_()