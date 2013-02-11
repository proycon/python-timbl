======================
 README: python-timbl
======================

:Authors: Sander Canisius, Maarten van Gompel
:Contact: proycon@anaproy.nl
:Web site: http://github.com/proycon/python-timbl/

python-timbl is a Python extension module wrapping the full TiMBL C++
programming interface. With this module, all functionality exposed
through the C++ interface is also available to Python scripts. Being
able to access the API from Python greatly facilitates prototyping
TiMBL-based applications.

This is the 2013 release by Maarten van Gompel, building on the 2006 release by Sander Canisius. For those used to the old library, there is one backwards-incompatible change, adapt your scripts to use ``import timblapi`` instead of ``import timbl``, as the latter is now a higher-level interface. 

License
=======

python-timbl is free software, distributed under the terms of the GNU
`General Public License`_ with a special exception that allows linking
with TiMBL (which has a GPL-incompatible license). Do note, however,
that using python-timbl in your applications implies using TiMBL as
well. As a result, when using python-timbl in your applications, you
will also have to comply with the terms of the `TiMBL license`_. Among
others, this license requires proper citation in publication of
research that uses TiMBL.

.. _General Public License: http://www.gnu.org/licenses/gpl.html
.. _TiMBL license: http://ilk.uvt.nl/timbl/License.terms


Installation
============

python-timbl depends on two external packages, which must have been built and/or installed on your system in order to successfully build python-timbl. The first is TiMBL itself; download its tarball from TiMBL's homepage and follow the installation instructions, recent Ubuntu/Debian users will find timbl in their distribution's package repository. In the remainder of this section, it is assumed that ``$TIMBL_HEADERS`` points to the directory that contains ``timbl/TimblAPI.h``, and ``$TIMBL_LIBS`` the directory that has contains the Timbl libraries. Note that Timbl itself depends on additional dependencies. 

The second prerequisite is Boost.Python, a library that facilitates writing Python extension modules in C++. Many Linux distributions come with prebuilt packages of Boost.Python. If so, install this package; on Ubuntu/Debian this can be done as follows:

::
	$ sudo apt-get install libboost-python libboost-python-dev

If not, refer to the `Boost installation instructions`_ to build and install Boost.Python manually. In the remainder of this section, let ``$BOOST_HEADERS`` refer to the directory that contains the Boost header files, and ``$BOOST_LIBS`` to the directory that contains the Boost library files. If you installed Boost.Python with your distribution's package manager, these directories are probably ``/usr/include`` and ``/usr/lib`` respectively.

.. _Boost installation instructions: http://www.boost.org/more/getting_started.html


If both prerequisites have been installed on your system, python-timbl can be obtained through github: 

::
	$ git clone git://github.com/proycon/python-timbl.git
	$ cd python-timbl

and can then be built and installed with the following command:

::
        $ sudo python setup.py \
               build_ext --boost-include-dir=$BOOST_HEADERS \
                         --boost-library-dir=$BOOST_LIBS \
                         --timbl-include-dir=$TIMBL_HEADERS  \
                         --timbl-library-dir=$TIMBL_LIBS \
               install --prefix=/dir/to/install/in
               
This is the verbose variant, if default locations are used then the following may suffice already:

::
        $ sudo python setup.py install               
               

The ``--prefix`` option to the install command denotes the directory in which the module is to be installed. If you have the appropriate system permissions, you can leave out this option. The module will then be installed in the Python system tree. Otherwise, make sure that the installation directory is in the module search path of your Python
system.

Usage
=======

python-timbl offers two interface to the timbl API. A low-level interface contained in the module ``timblapi``, which is very much like the C++ library, and a high-level object oriented interface in the ``timbl`` module, which offers a ``TimblClassifier`` class. 

timbl.TimblClassifier: High-level interface
----------------------







timblapi: Low-level interface
-------------------------

For documentation on the low level ``timblapi`` interface you can consult the TiMBL API guide.  Although this document actually describes the C++ interface to TiMBL, the latter is similar enough to its Python binding for this document to be a useful reference for python-timbl as well. For most part, the Python TiMBL interface follows the C++ version closely. The differences are listed below.

**Naming style**

In the C++ interface, method names are in *UpperCamelCase*; for example, ``Classify``, ``SetOptions``, etc. In contrast, the Python interface uses *lowerCamelCase*: ``classify``, ``setOptions``, etc.
Method overloading TiMBL's ``Classify`` methods use the C++ method overloading feature to provide three different kinds of outputs. Method overloading is non-existant in Python though; therefore, python-timbl has three differently named methods to mirror the functionality of the overloaded Classify method. The mapping is as follows.

::

	# bool TimblAPI::Classify(const std::string& Line,
	#                         std::string& result);
	#
	def TimblAPI.classify(line) -> bool, result

	#
	# bool TimblAPI::Classify(const std::string& Line,
	#                         std::string& result,
	#                         double& distance);
	#
	def TimblAPI.classify2(line) -> bool, result, distance

	#
	# bool TimblAPI::Classify(const std::string& Line,
	#                         std::string& result,
	#                         std::string& Distrib,
	#                         double& distance);
	#
	def TimblAPI.classify3(line) -> bool, result, Distrib, distance


**Python-only methods**

Three TiMBL API methods print information to a standard C++ output stream object (ShowBestNeighbors, ShowOptions, ShowSettings, ShowSettings). In the Python interface, these methods will only work with Python (stream) objects that have a fileno method returning a valid file descriptor. Alternatively, three new methods are provided (bestNeighbo(u)rs, options, settings); these methods return the same information as a Python string object.



