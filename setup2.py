#!/usr/bin/python
import os
import shutil
shutil.copyfile("setup2.py","setup.py")

from itertools import ifilter

from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext
from distutils.dep_util import newer
from distutils.unixccompiler import UnixCCompiler


def updateDocHeader(input, output):
	docstrings = {}
	execfile(input, docstrings)

	stream = open(output, "w")
	print >> stream, "#ifndef TIMBL_DOC_H"
	print >> stream, "#define TIMBL_DOC_H\n"
	print >> stream, "#include <Python.h>\n"

	for var in ifilter(lambda v: v.endswith("_DOC"), docstrings):
		print >> stream, "PyDoc_STRVAR(%s, \"%s\");\n" % (
			var, docstrings[var].strip().encode("string_escape"))

	print >> stream, "#endif"

	stream.close()


class BuildExt(build_ext):

	user_options = build_ext.user_options + [
		("boost-include-dir=", None, "directory for boost header files"),
		("boost-library-dir=", None, "directory for boost library files"),
		("timbl-include-dir=", None, "directory for TiMBL files"),
		("timbl-library-dir=", None, "directory for TiMBL library files"),
		("libxml2-include-dir=", None, "directory for LibXML2 files"),
		("libxml2-library-dir=", None, "directory for LibXML2 library files"),		
		("static-boost-python", "s", "statically link boost-python")]

	boolean_options = build_ext.boolean_options + [
		"static-boost-python"]

	def initialize_options(self):
		build_ext.initialize_options(self)
		self.boost_include_dir = "/usr/include"
		self.boost_library_dir = "/usr/lib"
		self.libxml2_include_dir = "/usr/include/libxml2"
		self.libxml2_library_dir = "/usr/lib"		
		self.timbl_include_dir = "/usr/local/include"
		self.timbl_library_dir = "/usr/local/lib"		
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

			if isinstance(self.compiler, UnixCCompiler) and \
				   self.static_boost_python:
				ext.extra_link_args.extend(
					"-Wl,-Bstatic -lboost_python -Wl,-Bdynamic".split())
			else:
				ext.libraries.append("boost_python")

		build_ext.build_extensions(self)


timblModule = Extension("timblapi", ["src/timblapi.cc"],
						libraries=["timbl"],
						depends=["src/timblapi.h", "src/docstrings.h"])


setup(
	name="python-timbl",
	version="2013.03.29-1",
	description="Python language binding for the Tilburg Memory-Based Learner",
	author="Sander Canisius, Maarten van Gompel",
	author_email="S.V.M.Canisius@uvt.nl, proycon@anaproy.nl",
	url="http://github.com/proycon/python-timbl",
	license="GPL",
	classifiers=["Development Status :: 4 - Beta","Topic :: Text Processing :: Linguistic","Topic :: Scientific/Engineering","Programming Language :: Python :: 2.6","Programming Language :: Python :: 2.7","Operating System :: POSIX","Intended Audience :: Developers","Intended Audience :: Science/Research","License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
	py_modules=['timbl'],
	ext_modules=[timblModule],
	cmdclass={"build_ext": BuildExt})
