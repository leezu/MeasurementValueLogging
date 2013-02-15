# -*- coding: utf-8 -*-

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

import threading

from devices.devices import TecpelDMM8061, XLS200, KernPCB


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
        if self.config.get("general", "device") == "XLS200":
            self.device = XLS200.openRS232(self.config.get("general", "port"))

            if self.config.get("xls200", "subdevice1") != "None":
                self.device.openDevice(eval(self.config.get("xls200", "subdevice1")), input = 1,
                typeOfValue = self.config.get("kernpcb", "kernPcbTypeOfValue"))

            if self.config.get("xls200", "subdevice2") != "None":
                self.device.openDevice(eval(self.config.get("xls200", "subdevice2")), input = 2,
                typeOfValue = self.config.get("kernpcb", "kernPcbTypeOfValue"))

            if self.config.get("xls200", "subdevice3") != "None":
                self.device.openDevice(eval(self.config.get("xls200", "subdevice3")), input = 3,
                typeOfValue = self.config.get("kernpcb", "kernPcbTypeOfValue"))

        else:
            self.device = eval(self.config.get("general", "device")).openRS232(self.config.get("general", "port"),
                typeOfValue = self.config.get("kernpcb", "kernPcbTypeOfValue"))

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
            strval += (str(rv.getDisplayedValue()) + " " + str(rv.getUnit()) + "\n")
            rawvals.append(rv)

        self.strval = strval[:-1]
        self.rawvals = tuple(rawvals)


class MesswertWidget(Widget):
    value_standard = "Press 'Start' to begin"
    value = kivy.properties.StringProperty(value_standard)
    rawvals = None

    thread_stop = None
    thread = None

    tmpfile = None
    starttime = None
    lasttime = 0

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
        import tempfile
        import time

        if self.tgl_btn_logging.state == "down":
            self.tmpfile = tempfile.TemporaryFile()
            self.starttime = time.time()

        elif self.tgl_btn_logging.state == "normal":
            self.tmpfile.close()
            self.tmpfile = None

    def updateValue(self, dt):
        import time

        self.value = str(self.thread.strval)
        self.rawvals = self.thread.rawvals

        if self.tmpfile and ((time.time() - self.lasttime) >
                int(App.get_running_app().config.get("general", "logging_interval"))):

            if self.rawvals != ():
                for i in self.rawvals:
                    self.tmpfile.write(str(i.getDisplayedValue()) + ",")

            self.tmpfile.write("\n")

            self.lasttime = time.time()


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
        config.setdefaults('kernpcb', {
            'kernpcbtypeofvalue' : 'unstable'
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
                    "options": ["TecpelDMM8061", "KernPCB", "XLS200"],
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
                    "desc": "Only applicable when a multibox-device like the XLS200 is used.",
                    "section": "xls200",
                    "options": ["None", "TecpelDMM8061", "KernPCB"],
                    "key": "subdevice1"
                },
                {
                    "type": "options",
                    "title": "Subdevice 2",
                    "desc": "Only applicable when a multibox-device like the XLS200 is used.",
                    "section": "xls200",
                    "options": ["None", "TecpelDMM8061", "KernPCB"],
                    "key": "subdevice2"
                },
                {
                    "type": "options",
                    "title": "Subdevice 3",
                    "desc": "Only applicable when a multibox-device like the XLS200 is used.",
                    "section": "xls200",
                    "options": ["None", "TecpelDMM8061", "KernPCB"],
                    "key": "subdevice3"
                }
            ]

        """

        kernpcb_settings = """

            [
                {
                    "type": "options",
                    "title": "Type of Value",
                    "desc": "See device manual",
                    "section": "kernpcb",
                    "options": ["stable", "unstable"],
                    "key": "kernPcbTypeOfValue"
                }
            ]

        """

        settings.add_json_panel('General Settings', self.config, data=general_settings)
        settings.add_json_panel('Multibox Settings', self.config, data=xls200_settings)
        settings.add_json_panel('KernPCB Settings', self.config, data=kernpcb_settings)


    def build(self):
        return MesswertWidget()

if __name__ == "__main__":
    MesswertApp().run()