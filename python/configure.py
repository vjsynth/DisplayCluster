import os
import sipconfig
from PyQt4 import pyqtconfig
import argparse

parser = argparse.ArgumentParser(description='Configure DisplayCluster Python module build')

parser.add_argument('-I', metavar='directoryList',
    action='append', nargs=1, dest='includeDirs',
    help='include directory list')

parser.add_argument('-L', metavar='directoryList',
    action='append', nargs=1, dest='libraryDirs',
    help='library directory list')

parser.add_argument('-l', metavar='directoryList',
    action='append', nargs=1, dest='libs',
    help='library list')

args = parser.parse_args()

includeDirs = ""
if args.includeDirs:
    for i in args.includeDirs:
        if includeDirs == "":
            includeDirs = i[0]
        else:
            includeDirs = includeDirs + ';' + i[0]

libraryDirs = ""
if args.libraryDirs:
    for i in args.libraryDirs:
        if libraryDirs == "":
            libraryDirs = i[0]
        else:
            libraryDirs = libraryDirs + ';' + i[0]

libs = ""
if args.libs:
    for i in args.libs:
        if libs == "":
            libs = i[0]
        else:
            libs = libs + ';' + i[0]

# The name of the SIP build file generated by SIP and used by the build
# system.
build_file = "pyapp.sbf"

# Get the PyQt configuration information.
config = pyqtconfig.Configuration()

# Get the extra SIP flags needed by the imported PyQt modules.  Note that
# this normally only includes those flags (-x and -t) that relate to SIP's
# versioning system.
pyqt_sip_flags = config.pyqt_sip_flags

# Run SIP to generate the code.  Note that we tell SIP where to find the qt
# module's specification files using the -I flag.
os.system(" ".join([config.sip_bin, "-c", ".", "-b", build_file, "-I", config.pyqt_sip_dir, pyqt_sip_flags, "pyapp.sip"]))

# We are going to install the SIP specification file for this module and
# its configuration module.
installs = []
installs.append(["point.sip", os.path.join(config.default_sip_dir, "pyapp")])
installs.append(["pyapp.py", config.default_mod_dir])

# Create the Makefile.  The QtGuiModuleMakefile class provided by the
# pyqtconfig module takes care of all the extra preprocessor, compiler and
# linker flags needed by the Qt library.
makefile = pyqtconfig.QtGuiModuleMakefile(
    configuration=config,
    build_file=build_file,
    installs=installs
)

makefile.extra_include_dirs.append("../src")
for i in includeDirs.split(';'):
	makefile.extra_include_dirs.append(i)

# Add the library we are wrapping.  The name doesn't include any platform
# specific prefixes or extensions (e.g. the "lib" prefix on UNIX, or the
# ".dll" extension on Windows).
# makefile.extra_libs = ["app"]

# Generate the Makefile itself.
makefile.generate()

# Now we create the configuration module.  This is done by merging a Python
# dictionary (whose values are normally determined dynamically) with a
# (static) template.
content = {
    # Publish where the SIP specifications for this module will be
    # installed.
    "pyapp_sip_dir":    config.default_sip_dir,

    # Publish the set of SIP flags needed by this module.  As these are the
    # same flags needed by the qt module we could leave it out, but this
    # allows us to change the flags at a later date without breaking
    # scripts that import the configuration module.
    "pyapp_sip_flags":  pyqt_sip_flags
}

# This creates the pyappconfig.py module from the pyappconfig.py.in
# template and the dictionary.
sipconfig.create_config_module("pyappconfig.py", "pyappconfig.py.in", content)
