Installation
=============
Stand-alone Executables
------------------------
There are stand-alone executables, compiled with `PyInstaller <http://www.pyinstaller.org/>`_ on `SourceForge <http://sourceforge.net/projects/measurement-log/files/>`_ . They do not require you to install anything on your computer. Simply execute the file.

Python Package
--------------
For easy installation the python package was uploaded to `PyPi <https://pypi.python.org/pypi/MeasurementValueLogging>`_. For installation with pip simply run::
	
	pip2 install MeasurementValueLogging

If you want to install the package by hand please make sure that you have a recent version of `PySerial <http://pyserial.sourceforge.net/>`_ installed. To use the GUI you need a recent version of `PyQT <http://www.riverbankcomputing.co.uk/software/pyqt/>`_ as well. If you want to try the webui you need the `Flask <http://flask.pocoo.org/>`_ microframework as well.

Then download and extract the tar.gz package from `PyPi <https://pypi.python.org/pypi/MeasurementValueLogging>`_. To install it change into the directory and run::

	python2 setup.py install

Source Code
-----------
The complete source code is available on `Github <https://github.com/leezu/MeasurementValueLogging>`_. You may report bugs or create pull requests there.

Usage
======
Console Interface
------------------
To use the console interface simply run::

    python2 -m MeasurementValueLogging.console [-h] port device [-h] [device options...]
    
For further information use the -h or --help option.

GUI
----
To use the GUI simply run::

    python2 -m MeasurementValueLogging.ui

Web Interface
-------------
The Web Interface uses the same syntax as the Console Interface. It starts a webserver on localhost:5000::

	python2 -m MeasurementValueLogging.webui [-h] port device [-h] [device options...]