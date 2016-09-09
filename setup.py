try:
	from setuptools import setup
except:
	from distutils.core import setup

setup(name="nfchook",
	version="0.1",
	description="NFC reader to webhook",
	author="Kawai, Hiroaki",
	author_email="hiroaki.kawai@gmail.com",
	url="https://github.com/hkwi/nfchook/",
	packages=["nfchook"],
	package_data={
		"nfchook":["templates/*", "static/*"]
	},
	entry_points = {
		"console_scripts": ["nfchook_web=nfchook.web:main",
			"nfchook_reader=nfchook.reader:main"],
	}
)
