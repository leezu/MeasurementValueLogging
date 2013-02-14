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
        self.value = "Please wait"

    def run(self):
        self.openDevice()

        while not self.stop_event.is_set():
            self.updateValue()

    def openDevice(self):
        if self.config.get("serial", "device") == "XLS200":
            self.device = XLS200.openRS232(self.config.get("serial", "port"))

            if self.config.get("serial", "subdevice1") != "None":
                self.device.openDevice(eval(self.config.get("serial", "subdevice1")), input = 1)

            if self.config.get("serial", "subdevice2") != "None":
                self.device.openDevice(eval(self.config.get("serial", "subdevice2")), input = 2)

            if self.config.get("serial", "subdevice3") != "None":
                self.device.openDevice(eval(self.config.get("serial", "subdevice3")), input = 3)

        elif self.config.get("serial", "device") == "KernPCB":
            self.device = KernPCB.openRS232(self.config.get("serial", "port"),
                typeOfValue = self.config.get("serial", "kernPcbTypeOfValue"))

        else:
            self.device = eval(self.config.get("serial", "device")).openRS232(self.config.get("serial", "port"))

    def updateValue(self):
        val = "\n"

        if isinstance(self.device, XLS200):
            if self.config.get("serial", "subdevice1") != "None":
                rawval = self.device.getRawValue(input = 1)
                val += (str(rawval.getDisplayedValue()) + " " +
                    str(rawval.getFactor(type = "prefix")) +
                    str(rawval.getUnit()) + "\n")

            if self.config.get("serial", "subdevice2") != "None":
                rawval = self.device.getRawValue(input = 2)
                val += (str(rawval.getDisplayedValue()) + " " +
                    str(rawval.getFactor(type = "prefix")) +
                    str(rawval.getUnit()) + "\n")

            if self.config.get("serial", "subdevice3") != "None":
                rawval = self.device.getRawValue(input = 3)
                val += (str(rawval.getDisplayedValue()) + " " +
                    str(rawval.getFactor(type = "prefix")) +
                    str(rawval.getUnit()) + "\n")
        
        else:
            rawval = self.device.getRawValue()
            val += (str(rawval.getDisplayedValue()) + " " + str(rawval.getUnit()) + "\n")

        self.value = val[:-1]


class MesswertWidget(Widget):
    value_standard = "Press 'Start' to begin"
    value = kivy.properties.StringProperty(value_standard)

    thread_stop = None
    thread = None

    def startStop(self):
        from kivy.clock import Clock

        if self.tgl_btn.state == "down":
            self.thread_stop = threading.Event()
            self.thread = GetValueThread(self.thread_stop)
            self.thread.start()

            Clock.schedule_once(self.updateValue)
            Clock.schedule_interval(self.updateValue, 0.1)

        elif self.tgl_btn.state == "normal":
            Clock.unschedule(self.updateValue)
            self.thread_stop.set()
            self.thread_stop = None
            self.thread = None
            self.value = self.value_standard

    def updateValue(self, dt):
        self.value = str(self.thread.value)


class MesswertApp(App):
    use_kivy_settings = False

    def build_config(self, config):
        config.setdefaults('serial', {
            'port' : '/dev/ttyUSB0',
            'device' : 'TecpelDMM8061',
            'subdevice1' : 'None',
            'subdevice2' : 'None',
            'subdevice3' : 'None',
            'kernpcbtypeofvalue' : 'unstable'
            })

    def build_settings(self, settings):
        jsondata = """
            [
                {
                    "type": "string",
                    "title": "Serial Port",
                    "desc": "Set the serial port on which a device is connected",
                    "section": "serial",
                    "key": "port"
                },
                {
                    "type": "options",
                    "title": "Device",
                    "desc": "Device",
                    "section": "serial",
                    "options": ["TecpelDMM8061", "KernPCB", "XLS200"],
                    "key": "device"
                },
                {
                    "type": "title",
                    "title": "Multibox-Settings"
                },
                {
                    "type": "options",
                    "title": "Subdevice 1",
                    "desc": "Only applicable when a multibox-device like the XLS200 is used.",
                    "section": "serial",
                    "options": ["None", "TecpelDMM8061", "KernPCB"],
                    "key": "subdevice1"
                },
                {
                    "type": "options",
                    "title": "Subdevice 2",
                    "desc": "Only applicable when a multibox-device like the XLS200 is used.",
                    "section": "serial",
                    "options": ["None", "TecpelDMM8061", "KernPCB"],
                    "key": "subdevice2"
                },
                {
                    "type": "options",
                    "title": "Subdevice 3",
                    "desc": "Only applicable when a multibox-device like the XLS200 is used.",
                    "section": "serial",
                    "options": ["None", "TecpelDMM8061", "KernPCB"],
                    "key": "subdevice3"
                },
                    {
                    "type": "title",
                    "title": "KernPCB-Settings"
                },
                    {
                    "type": "options",
                    "title": "Type of Value",
                    "desc": "Does not work, when behind a multibox-device. (If behind a multibox-device unstable is used)",
                    "section": "serial",
                    "options": ["stable", "unstable"],
                    "key": "kernPcbTypeOfValue"
                }
            ]

        """

        settings.add_json_panel('Serial Settings', self.config, data=jsondata)


    def build(self):
        return MesswertWidget()

if __name__ == "__main__":
    MesswertApp().run()