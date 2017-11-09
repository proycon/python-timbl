#!/usr/bin/python3

import sys
import os
import shutil
if os.path.exists('setup3.py'):
    shutil.copyfile("setup3.py","setup.py")

from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext
from distutils.dep_util import newer
from distutils.unixccompiler import UnixCCompiler


def updateDocHeader(input, output):
    docstrings = {}
    exec(compile(open(input, "rb").read(), input, 'exec'), docstrings)

    stream = open(output, "w")
    print("#ifndef TIMBL_DOC_H",file=stream)
    print("#define TIMBL_DOC_H\n",file=stream)
    print("#include <Python.h>\n",file=stream)

    for var in filter(lambda v: v.endswith("_DOC"), docstrings):
        print("PyDoc_STRVAR(%s, \"%s\");\n" % (var, str(docstrings[var].strip().encode("unicode_escape"), 'ascii') ), file=stream)

    print("#endif", file=stream)

    stream.close()


class BuildExt(build_ext):

    user_options = build_ext.user_options + [
        ("boost-include-dir=", None, "directory for boost header files"),
        ("boost-library-dir=", None, "directory for boost library files"),
        ("timbl-include-dir=", None, "directory for TiMBL files"),
        ("timbl-library-dir=", None, "directory for TiMBL library files"),
        ("libxml2-include-dir=", None, "directory for LibXML2 files"),
        ("libxml2-library-dir=", None, "directory for LibXML2 library files"),
        ("static-boost-python3", "s", "statically link boost-python")]

    boolean_options = build_ext.boolean_options + [
        "static-boost-python3"]

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.boost_include_dir = "/usr/include"
        self.boost_library_dir = "/usr/lib"
        self.libxml2_include_dir = "/usr/include/libxml2"
        self.libxml2_library_dir = "/usr/lib"
        if 'VIRTUAL_ENV' in os.environ and os.path.exists(os.environ['VIRTUAL_ENV'] + '/include/timbl'):
            self.timbl_include_dir = os.environ['VIRTUAL_ENV'] + '/include'
            self.timbl_library_dir = os.environ['VIRTUAL_ENV'] + '/lib'
        elif os.path.exists("/usr/include/timbl"):
            self.timbl_include_dir = "/usr/include"
            self.timbl_library_dir = "/usr/lib"
        elif os.path.exists("/usr/local/include/timbl"):
            self.timbl_include_dir = "/usr/local/include"
            self.timbl_library_dir = "/usr/local/lib"
        else:
            raise Exception("Timbl not found, make sure to install Timbl and set --timbl-include-dir and --timbl-library-dir appropriately...")
        self.static_boost_python = False

    def finalize_options(self):
        build_ext.finalize_options(self)
        self.ensure_file_exists("boost_include_dir", "boost/python.hpp")
        self.ensure_dirname("boost_library_dir")
        self.ensure_file_exists("timbl_include_dir", "timbl/TimblAPI.h")
        self.ensure_dirname("timbl_library_dir")
        self.ensure_file_exists("libxml2_include_dir", "libxml/tree.h")
        self.ensure_dirname("libxml2_library_dir")

    def ensure_file_exists(self, option, filename):
        self.ensure_dirname(option)
        self._ensure_tested_string(
            option,
            lambda d: os.path.isfile(os.path.join(d, filename)),
            "directory name",
            "'%s' was not found in '%%s'" % filename)

    def build_extensions(self):
        if newer("src/docstrings.h.in", "src/docstrings.h"):
            updateDocHeader("src/docstrings.h.in", "src/docstrings.h")

        for ext in self.extensions:
            ext.include_dirs.append(self.boost_include_dir)
            ext.include_dirs.append(self.timbl_include_dir)
            ext.include_dirs.append(self.libxml2_include_dir)
            ext.library_dirs.append(self.timbl_library_dir)
            ext.library_dirs.append(self.boost_library_dir)
            ext.library_dirs.append(self.libxml2_library_dir)

            pyversion = sys.version[0:3][0] + sys.version[0:3][2] #returns something like 32
            if os.path.exists(self.boost_library_dir + "/libboost_python-py"+pyversion+".so"):
                boostlib = "boost_python-py" + pyversion
            elif os.path.exists(self.boost_library_dir + "/libboost_python3.so"):
                boostlib = "boost_python3"
            elif os.path.exists(self.boost_library_dir + "/libboost_python.so"):
                #probably goes wrong if this is for python 2!
                boostlib = "boost_python"
            elif os.path.exists(self.boost_library_dir + "/libboost_python3.dylib"): #Mac OS X
                boostlib = "boost_python3"
            elif os.path.exists(self.boost_library_dir + "/libboost_python.dylib"): #Mac OS X
                #probably goes wrong if this is for python 2!
                boostlib = "boost_python"
            else:
                print("Unable to find boost library",file=sys.stderr)
                sys.exit(65)

            ext.extra_compile_args.extend(["-std=c++11"])
            if isinstance(self.compiler, UnixCCompiler) and self.static_boost_python:
                ext.extra_link_args.extend(
                    "-Wl,-Bstatic -l" + boostlib + " -Wl,-Bdynamic".split())
            else:
                ext.libraries.append(boostlib)

        build_ext.build_extensions(self)


timblModule = Extension("timblapi", ["src/timblapi.cc"],
                        libraries=["timbl"],
                        depends=["src/timblapi.h", "src/docstrings.h"])


setup(
    name="python3-timbl",
    version="2017.11.09",
    description="Python 3 language binding for the Tilburg Memory-Based Learner",
    author="Sander Canisius, Maarten van Gompel",
    author_email="S.V.M.Canisius@uvt.nl, proycon@anaproy.nl",
    url="http://github.com/proycon/python-timbl",
    classifiers=["Development Status :: 4 - Beta","Topic :: Text Processing :: Linguistic","Topic :: Scientific/Engineering","Programming Language :: Python :: 3","Operating System :: POSIX","Intended Audience :: Developers","Intended Audience :: Science/Research","License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
    license="GPL",
    py_modules=['timbl'],
    ext_modules=[timblModule],
    cmdclass={"build_ext": BuildExt})
