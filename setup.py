#!/bin/env python3

import sys
import os
import shutil
import platform
import glob

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

includedirs = []
libdirs = []
print(f"system={platform.system()} machine={platform.machine()}", file=sys.stderr)
if platform.system() == "Darwin":
    #we are running on Mac OS X (with homebrew hopefully), stuff is in specific locations:
    if platform.machine().lower() == "arm64":
        print("(macos arm64 detected)", file=sys.stderr)
        libdirs.append("/opt/homebrew/lib")
        includedirs.append("/opt/homebrew/include")
        libdirs.append("/opt/homebrew/icu4c/lib")
        includedirs.append("/opt/homebrew/icu4c/include")
        libdirs.append("/opt/homebrew/libxml2/lib")
        includedirs.append("/opt/homebrew/libxml2/include")
        includedirs.append("/opt/homebrew/libxml2/include/libxml2")
        libdirs.append("/opt/homebrew/opt/icu4c/lib")
        includedirs.append("/opt/homebrew/opt/icu4c/include")
        libdirs.append("/opt/homebrew/opt/libxml2/lib")
        includedirs.append("/opt/homebrew/opt/libxml2/include")
        libdirs.append("/opt/homebrew/opt/boost-python3/lib")
        libdirs.append("/opt/homebrew/opt/boost/lib")
        includedirs.append("/opt/homebrew/opt/boost/include")
    else:
        #we are running on Mac OS X with homebrew, stuff is in specific locations:
        libdirs.append("/usr/local/opt/icu4c/lib")
        includedirs.append("/usr/local/opt/icu4c/include")
        libdirs.append("/usr/local/opt/libxml2/lib")
        includedirs.append("/usr/local/opt/libxml2/include")
        includedirs.append("/usr/local/opt/libxml2/include/libxml2")
        libdirs.append("/usr/local/opt/boost-python3/lib")
        includedirs.append("/usr/local/opt/boost-python3/lib")
        libdirs.append("/usr/local/opt/boost/lib")
        includedirs.append("/usr/local/opt/boost/include")

#add some common default paths
includedirs += ['/usr/include/', '/usr/include/libxml2','/usr/local/include/' ]
libdirs += ['/usr/lib','/usr/local/lib']
if 'VIRTUAL_ENV' in os.environ:
    includedirs.insert(0,os.environ['VIRTUAL_ENV'] + '/include')
    libdirs.insert(0,os.environ['VIRTUAL_ENV'] + '/lib')
if 'INCLUDE_DIRS' in os.environ:
    includedirs = list(os.environ['INCLUDE_DIRS'].split(':')) + includedirs
if 'LIBRARY_DIRS' in os.environ:
    libdirs = list(os.environ['LIBRARY_DIRS'].split(':')) + libdirs

if platform.system() == "Darwin":
    extra_options = ["--stdlib=libc++",'-D U_USING_ICU_NAMESPACE=1']
else:
    extra_options = ['-D U_USING_ICU_NAMESPACE=1']

print(f"include_dirs={' '.join(includedirs)} library_dirs={' '.join(libdirs)} extra_options={' '.join(extra_options)}", file=sys.stderr)

class BuildExt(build_ext):
    def initialize_options(self):
        build_ext.initialize_options(self)
        pyversion = sys.version.split(" ")[0]
        pyversion = pyversion.split(".")[0]  + pyversion.split(".")[1] #returns something like 312 for 3.12
        #Find boost
        self.findboost(libdirs, includedirs, pyversion)

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
        if os.path.exists('/opt/homebrew/opt/boost-python3'):
            self.boostlib = "boost_python3"
            libsearch.insert(0,'/opt/homebrew/opt/boost-python3/lib')
            libsearch.insert(0,'/opt/homebrew/opt/boost/lib')
            includesearch.insert(0,'/opt/homebrew/opt/boost/include')
        if os.path.exists('/opt/homebrew/opt/boost-python' + pyversion):
            self.boostlib = "boost_python" + pyversion
            libsearch.insert(0,f"/opt/homebrew/opt/boost-python{pyversion}/lib")
            libsearch.insert(0,'/opt/homebrew/opt/boost/lib')
            includesearch.insert(0,'/opt/homebrew/opt/boost/include')

        for d in libsearch:
            if os.path.exists(d + "/libboost_python-py"+pyversion+".so"):
                self.boost_library_dir = d
                self.boostlib = "boost_python-py" + pyversion
                break
            elif os.path.exists(d + "/libboost_python"+pyversion+".so"):
                self.boost_library_dir = d
                self.boostlib = "boost_python" + pyversion
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
            elif os.path.exists(d + "/libboost_python-py" + pyversion + ".dylib"): #Mac OS X
                self.boost_library_dir = d
                self.boostlib = "boost_python-py" + pyversion
                break
            elif os.path.exists(d + "/libboost_python" + pyversion + ".dylib"): #Mac OS X
                self.boost_library_dir = d
                self.boostlib = "boost_python" + pyversion
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
            print("Unable to find boost library directory automatically. Is libboost-python3 installed?",file=sys.stderr)
            self.boost_library_dir = libsearch[0]
        if self.boost_include_dir is not None:
            print("Detected boost headers in " + self.boost_include_dir ,file=sys.stderr)
        else:
            print("Unable to find boost headers automatically. Is libboost-python-dev installed?",file=sys.stderr)
            self.boost_include_dir = includesearch[0]

    def build_extensions(self):
        if newer("src/docstrings.h.in", "src/docstrings.h"):
            updateDocHeader("src/docstrings.h.in", "src/docstrings.h")

        for ext in self.extensions:
            ext.include_dirs += includedirs
            ext.library_dirs += libdirs

            compile_args = ["-std=c++17"]
            if platform.system() == "Darwin":
                compile_args.append("-stdlib=libc++")
            ext.extra_compile_args.extend(compile_args)
            ext.libraries.append(self.boostlib)

        build_ext.build_extensions(self)


timblModule = Extension("timblapi", ["src/timblapi.cc"],
                        libraries=["timbl"],
                        depends=["src/timblapi.h", "src/docstrings.h"])

setup(
    name="python3-timbl",
    version="2025.01.22",
    description="Python 3 language binding for the Tilburg Memory-Based Learner",
    author="Sander Canisius, Maarten van Gompel",
    author_email="S.V.M.Canisius@uvt.nl, proycon@anaproy.nl",
    url="http://github.com/proycon/python-timbl",
    classifiers=["Development Status :: 4 - Beta","Topic :: Text Processing :: Linguistic","Topic :: Scientific/Engineering","Programming Language :: Python :: 3","Operating System :: POSIX","Intended Audience :: Developers","Intended Audience :: Science/Research","License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
    license="GPL",
    py_modules=['timbl'],
    ext_modules=[timblModule],
    cmdclass={"build_ext": BuildExt})
