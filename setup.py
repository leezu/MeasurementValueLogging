from distutils.core import setup

desc="""
=========================
MeasurementValueLogging
=========================

This application logs/displays measurement values from various serial devices.
It aims to be an open source alternative to the software provided by http://www.xlsmess.de/

Please see http://leezu.github.com/MeasurementValueLogging/ for documentation and installation instructions."""


setup(name="MeasurementValueLogging",
	version="0.4.0",
	description="Display measurement values from various serial devices.",
	long_description=desc,
	author="Leonard Lausen",
	author_email="leonard@lausen.nl",
	url="https://github.com/leezu/MeasurementValueLogging",
	packages = ['MeasurementValueLogging', 'MeasurementValueLogging.devices',
		"MeasurementValueLogging.ui_data", "MeasurementValueLogging.webui_data"],
	requires = ["pyserial", "PyQt"],
	license = "GPLv3+",
	provides = ["MeasurementValueLogging"],
	classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Win32 (MS Windows)',
          'Environment :: X11 Applications :: Qt',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7'
          ]
	)