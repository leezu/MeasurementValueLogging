measurement-value-logging
=========================

This application logs/displays measurement values from various serial devices.
It aims to be an open source alternative to the software provided by www.xlsmess.de

Installation
============
Make sure you have a recent version of http://pyserial.sourceforge.net/ installed. To use the GUI you need a recent version of http://www.riverbankcomputing.co.uk/software/pyqt/ as well.

An easy installation will follow soon. Until then you have to clone the repo and move everything to an appropriate path.

Usage
======
Console Interface
-----------------
To use the console interface simply run:

    python2 console.py [-h] port device [-h] [device options...]
    
For further information use the -h or --help option.



GUI
----
To use the GUI simply run:

    python2 ui.py
