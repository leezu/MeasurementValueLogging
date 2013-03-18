# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify
from devices.devicemanager import DeviceManager
import console
 
app = Flask(__name__)
dm = DeviceManager()

deviceIDs = console.openDevicesFromConsoleArgs(dm)

dm.start()

@app.route("/")
def home():
    return render_template('measurement.html')

@app.route("/_get_values")
def getValues():
    rvs = [dm.getLastRawValue(id) for id in deviceIDs]
    return jsonify(displayvals = [x.getDisplayedValue() for x in rvs],
        factors = [x.getFactor("prefix") for x in rvs],
        units = [x.getUnit() for x in rvs],
        len = len(rvs))