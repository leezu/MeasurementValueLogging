from flask import Flask, render_template
from devices.devicemanager import DeviceManager
import console
 
app = Flask(__name__)
dm = DeviceManager()

deviceIDs = console.openDevicesFromConsoleArgs(dm)

dm.start()

@app.route("/")
def home():
    rvs = [dm.getLastRawValue(id) for id in deviceIDs]
    vals = [(x.getDisplayedValue(), x.getFactor("prefix"), x.getUnit()) for x in rvs]
    return render_template('measurement.html', vals = vals)

if __name__ == '__main__':
    app.run(debug=True)