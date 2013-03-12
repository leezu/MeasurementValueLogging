***********************
Developer information
***********************

Structure
=========
MeasurementValueLogging is grouped into three python modules: :ref:`devices-module`, :ref:`ui-module` and :ref:`console-module`. Furthermore MeasurementValueLogging uses some third-party tools to achieve various goals, like creating documentation, providing stand-alone executables or gaining (simple & multi-platform) access to serial ports.

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
The devices module contains code representing physical devices as well as the code necessary to manage them. It is furthermore divided into

devices.devices
"""""""""""""""""
The devices module contains classes, representing phyiscal devices and measurement values. Device objects have varoius methods, for example to return a measurement value (a Value object). 

.. automethod:: devices.devices.Device.getRawValue

The (hopefully) returned Value object then has functions to access its data:

.. automethod:: devices.devices.Value.getDisplayedValue
.. automethod:: devices.devices.Value.getUnit
.. automethod:: devices.devices.Value.getFactor

In particular there are so called MutliboxDevices like the XLS200, which allow to use multiple devices on just one serial connection. They additionally provide methods to open, close or "get" one of their subdevices.

.. automethod:: devices.devices.MultiboxDevice.openDevice
.. automethod:: devices.devices.MultiboxDevice.closeDevice
.. automethod:: devices.devices.MultiboxDevice.getDevice

Some devices, like balances provide - in additon to the base device methods - more methods.

.. automethod:: devices.devices.Balance.setTypeOfValue

For a complete overview please see the :class:`devices.devices` documentation.

devices.devicemanager
"""""""""""""""""""""
The devicemanager module contains a DeviceManager class to manage devices. Please see :class:`devices.devicemanager.DeviceManager`.

The DeviceManager can run it's own thread, constantly updating measurement values. It has methods which give instant access to the last acquired value from a device (identified by a deviceID).

.. _ui-module:

UI module
^^^^^^^^^^
This module contains a graphical user interface to the DeviceManager.
For more information see :class:`ui`.

.. _console-module:

Console module
^^^^^^^^^^^^^^^
This module contains a console user interface to the DeviceManager.
For more information see :class:`console`.


Module documentation
=====================

Devices
--------

.. automodule:: devices.devices
	:members:

Devicemanager
--------------

.. automodule:: devices.devicemanager
	:members:

UI
---

.. automodule:: ui
	:members:

Console
--------

.. automodule:: console
	:members: