Introduction
============

This application logs/displays measurement values from various serial devices.
It aims to be an open source alternative to the software provided by `XLSmess <http://www.xlsmess.de/>`_

Installation
-----------
Stand-alone Executables
^^^^^^^^^^^^^^^^^^^^^^^^
There are stand-alone executables, compiled with `PyInstaller <http://www.pyinstaller.org/>`_ on `SourceForge <http://sourceforge.net/projects/measurement-log/files/>`_ . They do not require you to install anything on your computer. Simply execute the file.

Python Package
^^^^^^^^^^^^^^
To use the program as a Python package, make sure you have a recent version of `PySerial <http://pyserial.sourceforge.net/>`_ installed. To use the GUI you need a recent version of `PyQT <http://www.riverbankcomputing.co.uk/software/pyqt/>`_ as well.

Then download and install the package from `PyPi <https://pypi.python.org/pypi/MeasurementValueLogging>`_.

Usage
------
Console Interface
^^^^^^^^^^^^^^^^^^
To use the console interface simply run::

    python2 -m MeasurementValueLogging.console [-h] port device [-h] [device options...]
    
For further information use the -h or --help option.

GUI
^^^^
To use the GUI simply run::

    python2 -m MeasurementValueLogging.ui