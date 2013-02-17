# -*- coding: utf-8 -*-

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.factory import Factory

import threading
import os

from devices.devices import TecpelDMM8061, XLS200, KernPCB, BS600, FunctionDevice


class GetValueThread(threading.Thread):
    def __init__(self, stop_event):
        threading.Thread.__init__(self)
        self.daemon = True
        self.stop_event = stop_event
        self.config = App.get_running_app().config
        self.device = None
        self.strval = "Please wait"
        self.rawvals = () # tuple of value objects

    def run(self):
        self.openDevice()

        while not self.stop_event.is_set():
            self.updateValue()

    def openDevice(self):
        self.device = eval(self.config.get("general", "device")).openRS232(self.config.get("general", "port"),
            typeOfValue = self.config.get("balance", "typeOfValue"),
            in1=eval(self.config.get("xls200", "subdevice1")),
            in2=eval(self.config.get("xls200", "subdevice2")),
            in3=eval(self.config.get("xls200", "subdevice3")),
            functionDevice_subDeviceClass=eval(self.config.get("functiondevice", "subdevice")),
            functionDevice_value1=(int(self.config.get("functiondevice", "value1x")),
                int(self.config.get("functiondevice", "value1y"))),
            functionDevice_value2=(int(self.config.get("functiondevice", "value2x")),
                int(self.config.get("functiondevice", "value2y"))),
            functionDevice_unit=self.config.get("functiondevice", "unit"))

    def updateValue(self):
        strval = "\n"
        rawvals = []

        if isinstance(self.device, XLS200):
            if self.config.get("xls200", "subdevice1") != "None":
                rv = self.device.getRawValue(input = 1)
                strval += (str(rv.getDisplayedValue()) + " " +
                    str(rv.getFactor(type = "prefix")) +
                    str(rv.getUnit()) + "\n")
                rawvals.append(rv)

            if self.config.get("xls200", "subdevice2") != "None":
                rv = self.device.getRawValue(input = 2)
                strval += (str(rv.getDisplayedValue()) + " " +
                    str(rv.getFactor(type = "prefix")) +
                    str(rv.getUnit()) + "\n")
                rawvals.append(rv)

            if self.config.get("xls200", "subdevice3") != "None":
                rv = self.device.getRawValue(input = 3)
                strval += (str(rv.getDisplayedValue()) + " " +
                    str(rv.getFactor(type = "prefix")) +
                    str(rv.getUnit()) + "\n")
                rawvals.append(rv)
        
        else:
            rv = self.device.getRawValue()
            strval += (str(rv.getDisplayedValue()) + " " +
                str(rv.getFactor(type = "prefix")) +
                str(rv.getUnit()) + "\n")
            rawvals.append(rv)

        self.strval = strval[:-1]
        self.rawvals = tuple(rawvals)


class MesswertWidget(Widget):
    import tempfile

    value_standard = "Press 'Start' to begin"
    value = kivy.properties.StringProperty(value_standard)
    rawvals = None

    thread_stop = None
    thread = None

    tmpfile = tempfile.TemporaryFile()
    log = False
    pathToLogFile = None
    starttime = None
    lasttime = 0

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    _popup = None

    def startStopMeasurement(self):
        from kivy.clock import Clock

        if self.tgl_btn_measurement.state == "down":
            self.thread_stop = threading.Event()
            self.thread = GetValueThread(self.thread_stop)
            self.thread.start()

            Clock.schedule_once(self.updateValue)
            Clock.schedule_interval(self.updateValue, 0.1)

        elif self.tgl_btn_measurement.state == "normal":
            Clock.unschedule(self.updateValue)
            self.thread_stop.set()
            self.thread_stop = None
            self.thread = None
            self.value = self.value_standard

    def startStopLogging(self):
        import time
        import tempfile

        if self.tgl_btn_logging.state == "down":
            self.tmpfile = tempfile.TemporaryFile()
            self.starttime = time.time()
            self.log = True

        elif self.tgl_btn_logging.state == "normal":
            self.log = False

    def saveLog(self):
        self.show_save()

    def openLog(self):
        import subprocess

        if self.pathToLogFile:
            subprocess.call(["libreoffice", "--calc", self.pathToLogFile])
            # FIXME: Windows support? Add Try, Except
        else:
            Popup(title='Warning', content=Label(text="There is no log to open!"),
                size_hint=(None, None), size=(250,100)).open()

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_save(self):
        import os.path

        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        content.filechooser.path = os.path.expanduser("~")
        self._popup = Popup(title="Save file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        self.tmpfile.seek(0, 0)
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.tmpfile.read())
        self.pathToLogFile = os.path.join(path, filename)
        self.dismiss_popup()

    def updateValue(self, dt):
        import time

        self.value = str(self.thread.strval)
        self.rawvals = self.thread.rawvals

        if self.log and ((time.time() - self.lasttime) >
                int(App.get_running_app().config.get("general", "logging_interval"))):

            if self.rawvals != ():
                for i in self.rawvals:
                    self.tmpfile.write(str(i.getDisplayedValue() * i.getFactor()) + ",")

            self.tmpfile.write("\n")

            self.lasttime = time.time()


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MesswertApp(App):
    use_kivy_settings = False

    def build_config(self, config):
        config.setdefaults('general', {
            'port' : '/dev/ttyUSB0',
            'device' : 'TecpelDMM8061',
            'logging_interval': '1'})
        config.setdefaults('xls200', {
            'subdevice1' : 'None',
            'subdevice2' : 'None',
            'subdevice3' : 'None'})
        config.setdefaults('balance', {
            'typeofvalue' : 'unstable'})
        config.setdefaults('functiondevice', {
            'value1x' : 0,
            'value1y' : 0,
            'value2x' : 1,
            'value2y' : 1,
            'unit' : "°C",
            'subdevice' : 'TecpelDMM8061'
            })

    def build_settings(self, settings):
        general_settings = """

            [
                {
                    "type": "string",
                    "title": "Serial Port",
                    "desc": "Set the serial port on which a device is connected",
                    "section": "general",
                    "key": "port"
                },
                {
                    "type": "options",
                    "title": "Device",
                    "desc": "Device",
                    "section": "general",
                    "options": ["TecpelDMM8061", "KernPCB", "BS600", "XLS200", "FunctionDevice"],
                    "key": "device"
                },
                {
                    "type": "numeric",
                    "title": "Logging Interval",
                    "desc": "Interval between logging events",
                    "section": "general",
                    "key": "logging_interval"
                }
            ]

        """

        xls200_settings = """

            [
                {
                    "type": "options",
                    "title": "Subdevice 1",
                    "desc": "Device on XLS200 Input 1",
                    "section": "xls200",
                    "options": ["None", "TecpelDMM8061", "KernPCB", "BS600", "FunctionDevice"],
                    "key": "subdevice1"
                },
                {
                    "type": "options",
                    "title": "Subdevice 2",
                    "desc": "Device on XLS200 Input 2",
                    "section": "xls200",
                    "options": ["None", "TecpelDMM8061", "KernPCB", "BS600", "FunctionDevice"],
                    "key": "subdevice2"
                },
                {
                    "type": "options",
                    "title": "Subdevice 3",
                    "desc": "Device on XLS200 Input 3",
                    "section": "xls200",
                    "options": ["None", "TecpelDMM8061", "KernPCB", "BS600", "FunctionDevice"],
                    "key": "subdevice3"
                }
            ]

        """

        balance_settings = """

            [
                {
                    "type": "options",
                    "title": "Type of Value",
                    "desc": "See device manual",
                    "section": "balance",
                    "options": ["stable", "unstable"],
                    "key": "typeOfValue"
                }
            ]

        """

        functionDevice_settings = """

            [
                {
                    "type": "numeric",
                    "title": "Value 1: Is",
                    "desc": "The value displayed by the device.",
                    "section": "functiondevice",
                    "key": "value1x"
                },
                {
                    "type": "numeric",
                    "title": "Value 1: Should be",
                    "desc": "The should be value.",
                    "section": "functiondevice",
                    "key": "value1y"
                },
                {
                    "type": "numeric",
                    "title": "Value 2: Is",
                    "desc": "The value displayed by the device.",
                    "section": "functiondevice",
                    "key": "value2x"
                },
                {
                    "type": "numeric",
                    "title": "Value 2: Should be",
                    "desc": "The should be value.",
                    "section": "functiondevice",
                    "key": "value2y"
                },
                {
                    "type": "string",
                    "title": "Unit",
                    "desc": "Unit of the result.",
                    "section": "functiondevice",
                    "key": "unit"
                },
                {
                    "type": "options",
                    "title": "Subdevice",
                    "desc": "Subdevice function should be applied at",
                    "section": "functiondevice",
                    "options": ["TecpelDMM8061", "KernPCB", "BS600"],
                    "key": "subdevice"
                }
            ]

        """

        settings.add_json_panel('General Settings', self.config, data=general_settings)
        settings.add_json_panel('XLS200 Settings', self.config, data=xls200_settings)
        settings.add_json_panel('Balance Settings', self.config, data=balance_settings)
        settings.add_json_panel('Function Settings', self.config, data=functionDevice_settings)


    def build(self):
        return MesswertWidget()



Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == "__main__":
    kivy.config.Config.set('input', 'mouse', 'mouse,disable_multitouch')
    MesswertApp().run()