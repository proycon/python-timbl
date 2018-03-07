#!/usr/bin/python3

import sys
import os
import shutil
import platform
import glob
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
        pyversion = sys.version[0:3][0] + sys.version[0:3][2] #returns something like 32
        libsearch = ['/usr/lib', '/usr/lib/' + platform.machine() + '-' + platform.system().lower() + '-gnu', '/usr/local/lib']
        includesearch = ['/usr/include', '/usr/local/include']
        if 'VIRTUAL_ENV' in os.environ and os.path.exists(os.environ['VIRTUAL_ENV'] + '/lib'):
            libsearch.insert(0, os.environ['VIRTUAL_ENV'] + '/lib')
        if 'VIRTUAL_ENV' in os.environ and os.path.exists(os.environ['VIRTUAL_ENV'] + '/include'):
            includesearch.insert(0, os.environ['VIRTUAL_ENV'] + '/include')

        #Find boost
        self.findboost(libsearch, includesearch, pyversion)

        #Find libxml2
        if os.path.exists('/usr/local/Cellar/libxml2'):
            #Mac OS X with homebrew
            versiondirs = []
            for d in glob.glob('/usr/local/Cellar/libxml2/*'):
                if os.path.isdir(d) and d[0] != '.':
                    versiondirs.append(os.path.basename(d))
            if versiondirs:
                versiondirs.sort()
                version = versiondirs[0]
                libsearch.insert(0,'/usr/local/Cellar/libxml2/' + version + '/lib')
                includesearch.insert(0,'/usr/local/Cellar/libxml2/' + version + '/include')

        for d in includesearch:
            if os.path.exists(d  + '/libxml2'):
                self.libxml2_include_dir = d + '/libxml2'
                self.libxml2_library_dir = d.replace('include','lib')
                break

        #Find timbl
        self.timbl_library_dir = None
        for d in includesearch:
            if os.path.exists(d  + '/timbl'):
                self.timbl_include_dir = d
                self.timbl_library_dir = d.replace('include','lib')
                break

        if self.timbl_library_dir is None:
            raise Exception("Timbl not found, make sure to install Timbl and set --timbl-include-dir and --timbl-library-dir appropriately...")

        self.static_boost_python = False

    def findboost(self, libsearch, includesearch, pyversion):
        self.boost_library_dir = None
        self.boost_include_dir = None
        self.boostlib = "boost_python"
        if os.path.exists('/usr/local/opt/boost-python3'):
            #Mac OS X with homebrew
            self.boostlib = "boost_python3"
            libsearch.insert(0,'/usr/local/opt/boost-python3/lib')
            libsearch.insert(0,'/usr/local/opt/boost/lib')
            includesearch.insert(0,'/usr/local/opt/boost/include')

        for d in libsearch:
            if os.path.exists(d + "/libboost_python-py"+pyversion+".so"):
                self.boost_library_dir = d
                self.boostlib = "boost_python-py" + pyversion
                break
            elif os.path.exists(d + "/libboost_python3.so"):
                self.boost_library_dir = d
                self.boostlib  = "boost_python3"
                break
            elif os.path.exists(d + "/libboost_python.so"):
                #probably goes wrong if this is for python 2!
                self.boost_library_dir = d
                self.boostlib = "boost_python"
                break
            elif os.path.exists(d + "/libboost_python3.dylib"): #Mac OS X
                self.boost_library_dir = d
                self.boostlib = "boost_python3"
                break
            elif os.path.exists(d + "/libboost_python.dylib"): #Mac OS X
                self.boost_library_dir = d
                #probably goes wrong if this is for python 2!
                self.boostlib = "boost_python"
                break
        for d in includesearch:
            if os.path.exists(d + "/boost"):
                self.boost_include_dir = d
                break

        if self.boost_library_dir is not None:
            print("Detected boost library in " + self.boost_library_dir + " (" + self.boostlib +")",file=sys.stderr)
        else:
            print("Unable to find boost library directory automatically. Is libboost-python3 installed? Set --boost-library-dir?",file=sys.stderr)
            self.boost_library_dir = libsearch[0]
        if self.boost_include_dir is not None:
            print("Detected boost headers in " + self.boost_include_dir ,file=sys.stderr)
        else:
            print("Unable to find boost headers automatically. Is libboost-python-dev installed? Set --boost-include-dir",file=sys.stderr)
            self.boost_include_dir = includesearch[0]

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

            compile_args = ["-std=c++11"]
            if platform.system() == "Darwin":
                compile_args.append("-stdlib=libc++")
            ext.extra_compile_args.extend(compile_args)
            if isinstance(self.compiler, UnixCCompiler) and self.static_boost_python:
                ext.extra_link_args.extend(
                    "-Wl,-Bstatic -l" + self.boostlib + " -Wl,-Bdynamic".split())
            else:
                ext.libraries.append(self.boostlib)


        build_ext.build_extensions(self)


timblModule = Extension("timblapi", ["src/timblapi.cc"],
                        libraries=["timbl"],
                        depends=["src/timblapi.h", "src/docstrings.h"])


setup(
    name="python3-timbl",
    version="2018.03.07",
    description="Python 3 language binding for the Tilburg Memory-Based Learner",
    author="Sander Canisius, Maarten van Gompel",
    author_email="S.V.M.Canisius@uvt.nl, proycon@anaproy.nl",
    url="http://github.com/proycon/python-timbl",
    classifiers=["Development Status :: 4 - Beta","Topic :: Text Processing :: Linguistic","Topic :: Scientific/Engineering","Programming Language :: Python :: 3","Operating System :: POSIX","Intended Audience :: Developers","Intended Audience :: Science/Research","License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
    license="GPL",
    py_modules=['timbl'],
    ext_modules=[timblModule],
    cmdclass={"build_ext": BuildExt})
