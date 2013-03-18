from flask import Flask, render_template
from devices.devicemanager import DeviceManager
import console
 
app = Flask(__name__)
dm = DeviceManager()

deviceIDs = console.openDevicesFromConsoleArgs(dm)
id = deviceIDs[0]

dm.start()

@app.route("/")
def home():
    rv = dm.getLastRawValue(id)
    return render_template('measurement.html', val = rv.getDisplayedValue(),
        pref = rv.getFactor('prefix'), unit = rv.getUnit())

if __name__ == '__main__':
    app.run(debug=True)