from distutils.core import setup

setup(name="MeasurementValueLogging",
	version="0.1.1",
	description="Display measurement values from various serial devices.",
	long_description=open('README.md').read(),
	author="Leonard Lausen",
	author_email="leonard@lausen.nl",
	url="https://github.com/leezu/measurement-value-logging",
	packages = ['MeasurementValueLogging', 'MeasurementValueLogging.devices'],
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