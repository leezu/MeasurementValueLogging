***********************
Developer information
***********************

Structure
=========
MeasurementValueLogging is divided into two parts: The devices backend, which contains the logic to gather values and manage devices as well as the frontend part which includes various frontends (command line, GUI, website) which use the backend to display measurement values and configure devices.

To provide it's functionality MeasurementValueLogging uses some third-party tools. They are used for example to generate documentation, provide stand-alone executables or gain (simple & multi-platform) access to serial ports.

Third-party tools and modules
------------------------------

Sphinx
^^^^^^^
MeasurementValueLogging uses `Sphinx <http://sphinx-doc.org>`_ and its `autodoc extension <http://sphinx-doc.org/ext/autodoc.html#module-sphinx.ext.autodoc>`_ to create its documentation. The Sphinx related files can be found in the docs/ directory.
Wikipedia describes Sphinx as follows:

	Sphinx is a documentation generator which converts reStructuredText files into HTML websites and other formats including PDF, EPub and man. It exploits the extensible nature of reStructuredText through a number of extensions (e.g. for autogenerating documentation from source code, writing mathematical notation or highlighting source code). The first public release, version 0.1.61611, was announced on March 21, 2008. It was developed for, and used extensively by, the Python project for documentation.

	Since its introduction in 2008, Sphinx was adopted by many other important Python projects, such as Bazaar, SQLAlchemy, MayaVi, Sage, SciPy, Django and Pylons; it is also used for the Blender Python API documentation. In an effort to make maintenance of software documentation easier, the Read the Docs project was created. It automates the process of building and uploading Sphinx documentation after every commit. It is sponsored by the Python Software Foundation.

A gh-pages option has been added to the Makefile in docs/ . This allows to automatically update the `Github MeasurementValueLogging <https://github.com/leezu/MeasurementValueLogging>`_ page with the most recent Sphinx documentation as described by `Nikhil on his blog <http://blog.nikhilism.com/2012/08/automatic-github-pages-generation-from.html>`_.

QT
^^
MeasurementValueLogging uses `QT <https://qt-project.org/>`_ (`PyQt <www.riverbankcomputing.co.uk/software/pyqt/>`_) for it's graphical user interface. The gui is made with help of the `QT Designer <http://qt-project.org/doc/qt-4.8/designer-manual.html>`_ (see the .ui files in ui/). Furthermore `QResources <http://qt-project.org/doc/qt-4.8/qresource.html>`_, `QSettings <http://qt-project.org/doc/qt-4.8/qsettings.html>`_ and the `QT Internationalization capabilities <http://qt-project.org/doc/qt-4.8/internationalization.html>`__ are used. QResources allow to pack arbitrary data in a python module, so that it's more easily accessible and, more important allows to easily package MeasurementValueLogging in a single executable. QSettings provice persistent platform-independent application settings. The internationalization files can be found in the i18n/ directory.

Python Distribution Utilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`Python Distutils <http://docs.python.org/3/distutils/>`_ are used to create Python packages distributed on `PyPi <https://pypi.python.org/pypi/MeasurementValueLogging>`_.

PyInstaller
^^^^^^^^^^^
`PyInstaller <www.pyinstaller.org>`_ is used to package MeasurementValueLogging into stand-alone executables. This is done by calling the following command::

	pyinstaller --onefile --name=MeasurementValueLogging --windowed path/to/ui.py

Please see the `PyInstaller documentation <www.pyinstaller.org/export/v2.0/project/doc/Manual.html>`_ for more information. The stand-alone executables can be found on `SourceForge <http://sphinx.pocoo.org>`_.

PySerial
^^^^^^^^^
Last but not least MeasurementValueLogging uses the `PySerial module <http://pyserial.sourceforge.net/>`_ by Chris Liechti for its serial communication with the devices.


MeasurementValueLogging Modules
--------------------------------

.. _devices-module:

Devices module
^^^^^^^^^^^^^^^
The devices module contains the logic to gather measurement values from various devices and manage them. In addition there is a module which helps converting between SI stuff. The devices module is divided into

devices.devices
"""""""""""""""""
The devices.devices module contains classes, representing phyiscal devices as well as their measurement values. The Device objects have varoius methods, for example to return a measurement value (a Value object). 

.. automethod:: devices.devices.Device.getRawValue

The returned Value object has some attributes which hold its data:

.. autoattribute:: devices.devices.Value.value
.. autoattribute:: devices.devices.Value.factor
.. autoattribute:: devices.devices.Value.unit
.. autoattribute:: devices.devices.Value.time

Furthermore there are so called MutliboxDevices like the `XLS200 <http://www.xlsmess.de/html/xls_200.html>`_, which allow to use multiple devices on just one serial connection. They additionally provide methods to open, close or get values from one of their subdevices.

.. automethod:: devices.devices.MultiboxDevice.openDevice
.. automethod:: devices.devices.MultiboxDevice.closeDevice

Some devices, like balances provide - in additon to the base device methods - more methods.

.. automethod:: devices.devices.Balance.setTypeOfValue

For a complete overview please see the :class:`devices.devices` documentation.

devices.devicemanager
"""""""""""""""""""""
The devicemanager module contains a DeviceManager class to manage devices. It runs it's own thread, constantly updating measurement values and provides easy access to them.

There are methods to open or close devices as well as more sophisticated methods which allow to calibrate gained values measurement values. Devices are identified by a deviceID which is returned when opening a device.

.. automethod:: devices.devicemanager.DeviceManager.openDevice
.. automethod:: devices.devicemanager.DeviceManager.closeDevice

Access to the measurement values is provided with an first-in-first-out queue.

.. autoattribute:: devices.devicemanager.DeviceManager.queue

For a complete overview please see the :class:`devices.devicemanager.DeviceManager` documentation.

devices.si
"""""""""""
The si module contains method to convert between different representations of SI prefixes, factors etc.

.. autofunction:: devices.si.getPrefix
.. autofunction:: devices.si.getName
.. autofunction:: devices.si.getNumberPrefix

For a complete overview please see the :class:`devices.si` documentation.


.. _ui-module:

Frontend
^^^^^^^^^^
GUI
"""
This module contains a graphical user interface to the DeviceManager. It allows to open and close devices, displays their values and enables the user to calibrate device with an easy to use GUI.
For more information see :class:`ui`.

.. _console-module:

Console
""""""""
The console module contains code for opening devices from command-line arguments. Furthermore it provides a simple main function which prints the gained values to the standard output.
For more information see :class:`console`.

Web-Interface
""""""""""""""
The webui module is a proof-of-concept. It opens devices with the code provided by the console module and displays their values on a website running on localhost:5000. It uses the `Flask <http://flask.pocoo.org/>`_ microframework.




Directory layout
====================
::

	.                                     	
	|-- docs                              	Files used to generate the documentation with sphinx-doc
	|   |-- conf.py                       	
	|   |-- developer.rst                 	
	|   |-- index.rst                     	
	|   |-- intro.rst                     	
	|   |-- make.bat                      	
	|   |-- Makefile                      	Makefiles with options to build the docs to pdf, html etc.
	|   `-- _templates                    	
	|       `-- layout.html               	
	|-- LICENSE.txt                       	GPLv3+
	|-- MeasurementValueLogging           	Contains the true program
	|   |-- console.py                    	Console module
	|   |-- devices                       	Devices module
	|   |   |-- devicemanager.py          	
	|   |   |-- devices.py                	
	|   |   |-- __init__.py               	
	|   |   `-- si.py                     	
	|   |-- __init__.py                   	
	|   |-- Makefile                      	Makefile with options to compile the ui files or generate translation
	|   |-- ui_data                       	Data used by the gui, ui files are generated with the QT Designer
	|   |   |-- close.png                 	
	|   |   |-- close.svg                 	
	|   |   |-- deviceSettingsDialog.ui   	
	|   |   |-- displayWidget.ui          	
	|   |   |-- doReallyDialog.ui         	
	|   |   |-- i18n                      	Translation files
	|   |   |   |-- de.qm                 	
	|   |   |   `-- de.ts                 	
	|   |   |-- __init__.py               	
	|   |   |-- mainWindow.ui             	
	|   |   |-- newDeviceDialog.ui        	
	|   |   |-- qr.py                     	*.ui files and translations compiled to a QResource file
	|   |   |-- resource.qrc              	defines the files to be compiled to a QResource
	|   |   |-- settingsDialog.ui         	
	|   |   |-- settings.png              	
	|   |   |-- settings.svg              	
	|   |   `-- xls200Dialog.ui           	
	|   |-- ui.py                         	gui module
	|   |-- webui_data                    	data used by the web-interface
	|   |   |-- __init__.py               	
	|   |   |-- routes.py                 	flask routes
	|   |   |-- static                    	
	|   |   |   |-- css                   	
	|   |   |   |   `-- main.css          	
	|   |   |   `-- js                    	
	|   |   |       |-- jquery-1.9.1.min.j	
	|   |   |       `-- measurement.js    	
	|   |   `-- templates                 	
	|   |       |-- layout.html           	
	|   |       `-- measurement.html      	
	|   `-- webui.py                      	web-interface module
	|-- README.md                         	
	`-- setup.py                          	Python Distribution Utilities