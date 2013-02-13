# -*- coding: utf-8 -*-

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.config import ConfigParser
from kivy.uix.settings import Settings
from kivy.properties import ObjectProperty

import threading

from devices import TecpelDMM8061, XLS200, KernPCB


class GetRawValueThread(threading.Thread):
    def __init__(self, config, stop_event):
        threading.Thread.__init__(self)
        self.daemon = True
        self.stop_event = stop_event
        self.config = config
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


kivy.lang.Builder.load_file('ui.kv')

config = ConfigParser()
config.read('settings.ini')

class MesswertScreen(Screen):
    value_standard = "Press 'Start' to begin"
    value = kivy.properties.StringProperty(value_standard)

    thread_stop = None
    thread = None

    def startStop(self):
        from kivy.clock import Clock

        if self.tgl_btn.state == "down":
            self.thread_stop = threading.Event()
            self.thread = GetRawValueThread(config, self.thread_stop)
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


class SettingsScreen(Screen):
    pass

class MesswertApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        
        sm.add_widget(MesswertScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))

        sm.get_screen("settings").settings.add_json_panel('Serial Settings',
            config, 'settings_custom.json')
        sm.get_screen("settings").settings.add_kivy_panel()

        return sm

if __name__ == "__main__":
    MesswertApp().run()