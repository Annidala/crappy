"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path, uname, system
from subprocess import call
from multiprocessing import cpu_count
from distutils.command.build import build
from distutils.core import setup, Extension

comediModule = Extension('sensor.comediModule', sources = ['sources/comediModule/comediModule.c', 'sources/comediModule/common.c'], extra_link_args=["-l", "comedi", "-l", "python2.7"])
ximeaModule = Extension('sensor.ximeaModule', sources = ['sources/XimeaLib/ximea.cpp', 'sources/XimeaLib/pyXimea.cpp'], extra_compile_args = ["-std=c++11"], extra_link_args=["-L", "../bin", "-L", "../bin/X64", "-L" , "../bin/ARM",  "-l", "m3api", "-l", "python2.7"])
here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


class LibBuild(build):
  
    def run(self):
		# run original build code
		build.run(self)
		self.run_command("build_ext -b ../crappy/")
		jai_build_path = path.join(here, 'sources/JaiLib/')
		jai_cmd = [
			'make',
			'OUT=' + jai_build_path,
			'V=' + str(self.verbose),
			]
		try:
			jai_cmd.append('-j%d' % cpu_count())
		except NotImplementedError:
			print 'Unable to determine number of CPUs. Using single threaded make.'
		
		def compile():
			if(uname()[2]=='3.2.0-70-generic'):
				call(jai_cmd, cwd=jai_build_path)
			else:
				print "Wrong Kernel version, Jai library not compiled.\n"
			
		self.execute(compile, [], 'Compiling libraries')

class LibClean(build):
  
	def run(self):
		# run original build code
		build.run(self)
		jai_build_path = path.join(here, 'sources/JaiLib/')
		jai_cmd = [
			'make clean',
			'OUT=' + jai_build_path,
			'V=' + str(self.verbose),
			]
		def clean():
			if(uname()[2]=='3.2.0-70-generic'):
				call(jai_cmd, cwd=jai_build_path)
			else:
				print "Wrong Kernel version, unable to find Jai library\n"
			
		self.execute(clean, [], 'Deleting shared objects.')


setup(
    name='crappy',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.1.0',

    description='Command and Real-time Acquisition Parallelized in Python',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/LaboratoireMecaniqueLille',

    # Author details
    author='LML',
    author_email='None', ## Create a mailing list!

    # Choose your license
    license='GPL V2', ### to confirm

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers, Science/Research',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.2',
        #'Programming Language :: Python :: 3.3',
        #'Programming Language :: Python :: 3.4',
        'Operating System :: POSIX :: Linux',
    ],

    # What does your project relate to?
    keywords='control command acquisition multiprocessing',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    
    ext_package='crappy',
    ext_modules = [comediModule, ximeaModule],
	
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['numpy', 'matplotlib','pandas'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    
    cmdclass={
        'build': LibBuild,
        'clean': LibClean,
    },
    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
        #'sample': ['package_data.dat'],
    #},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
        #'console_scripts': [
            #'sample=sample:main',
        #],
    #},
)
system('cp build/lib.linux-x86_64-2.7/crappy/sensor/ximeaModule.so crappy/sensor/')
system('cp build/lib.linux-x86_64-2.7/crappy/sensor/comediModule.so crappy/sensor/')