from distutils.core import setup

setup(name="MeasurementValueLogging",
	version="0.1",
	description="Display measurement values from various serial devices.",
	author="Leonard Lausen",
	author_email="leonard@lausen.nl",
	url="https://github.com/leezu/measurement-value-logging",
	packages = ['MeasurementValueLogging', 'MeasurementValueLogging.devices'],
	package_data={'MeasurementValueLogging': ['ui/*.ui', 'ui/*.png', 'i18n/*.qm']},
	requires = ["pyserial", "PyQt"],
	)