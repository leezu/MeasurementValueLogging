# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify
from devices.devicemanager import DeviceManager
from console import openDevicesFromConsoleArgs
 
app = Flask(__name__)
dm = DeviceManager()

deviceIDs = openDevicesFromConsoleArgs(dm)

lastValues = {}

@app.route("/")
def home():
    return render_template('measurement.html')

@app.route("/_get_values")
def getValues():
    while not dm.queue.empty():
        deviceID, rv = dm.queue.get()
        lastValues[deviceID] = rv

    return jsonify(displayvals = [x.value for x in lastValues.values()],
        prefixes = [x.prefix for x in lastValues.values()],
        units = [x.unit for x in lastValues.values()],
        len = len(lastValues))

def main():
    app.run()