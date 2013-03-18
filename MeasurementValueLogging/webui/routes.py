from __future__ import absolute_import

import time

from flask import Flask, render_template
from devices.devicemanager import DeviceManager
 
app = Flask(__name__)
dm = DeviceManager()

id = dm.openDevice("TecpelDMM8061", "/dev/ttyUSB1")
dm.start()

@app.route("/")
def home():
    rv = dm.getLastRawValue(id)
    return render_template('measurement.html', val = rv.getDisplayedValue(),
        pref = rv.getFactor('prefix'), unit = rv.getUnit())

if __name__ == '__main__':
    app.run(debug=True)