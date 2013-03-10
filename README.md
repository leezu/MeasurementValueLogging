=========================
MeasurementValueLogging
=========================

This application logs/displays measurement values from various serial devices.
It aims to be an open source alternative to the software provided by http://www.xlsmess.de/

There is a short introduction below, for real documentation see http://leezu.github.com/MeasurementValueLogging/ .

Installation
============

Stand-alone Executables
-----------------------
There are stand-alone executables, compiled with http://www.pyinstaller.org/ on http://sourceforge.net/projects/measurement-log/files/ . They do not require you to install anything on your computer. Simply execute the file.


Python Package
--------------
To use the program as a Python package, make sure you have a recent version of http://pyserial.sourceforge.net/ installed. To use the GUI you need a recent version of http://www.riverbankcomputing.co.uk/software/pyqt/ as well.

Then download and install the package from https://pypi.python.org/pypi/MeasurementValueLogging (or clone the git repo).

Usage
======
Console Interface
-----------------
To use the console interface simply run:

    python2 -m MeasurementValueLogging.console [-h] port device [-h] [device options...]
    
For further information use the -h or --help option.



GUI
----
To use the GUI simply run:

    python2 -m MeasurementValueLogging.ui