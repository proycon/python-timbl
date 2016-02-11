.. image:: http://applejack.science.ru.nl/lamabadge.php/python-timbl
   :target: http://applejack.science.ru.nl/languagemachines/

======================
 README: python-timbl
======================

:Authors: Sander Canisius, Maarten van Gompel
:Contact: proycon@anaproy.nl
:Web site: https://github.com/proycon/python-timbl/

python-timbl is a Python extension module wrapping the full TiMBL C++
programming interface. With this module, all functionality exposed
through the C++ interface is also available to Python scripts. Being
able to access the API from Python greatly facilitates prototyping
TiMBL-based applications.

This is the 2013 release by Maarten van Gompel, building on the 2006 release by Sander Canisius. For those used to the old library, there is one backwards-incompatible change, adapt your scripts to use ``import timblapi`` instead of ``import timbl``, as the latter is now a higher-level interface. 

License
=======

python-timbl is free software, distributed under the terms of the GNU `General
Public License`_. Please cite TiMBL in  publication of research that uses
TiMBL.

.. _General Public License: http://www.gnu.org/licenses/gpl.html

Installation
============

python-timbl is distributed as part of **LaMachine**
(https://proycon.github.io/LaMachine), which significantly simplifies
compilation and installation. The remainder of the instructions in this section
refer to manual compilation and installation.

python-timbl depends on two external packages, which must have been built
and/or installed on your system in order to successfully build python-timbl.
The first is TiMBL itself; download its tarball from TiMBL's homepage and
follow the installation instructions, recent Ubuntu/Debian users will find
timbl in their distribution's package repository. In the remainder of this
section, it is assumed that ``$TIMBL_HEADERS`` points to the directory that
contains ``timbl/TimblAPI.h``, and ``$TIMBL_LIBS`` the directory that has
contains the Timbl libraries. Note that Timbl itself depends on additional
dependencies. 

The second prerequisite is Boost.Python, a library that facilitates writing
Python extension modules in C++. Many Linux distributions come with prebuilt
packages of Boost.Python. If so, install this package; on Ubuntu/Debian this
can be done as follows::

	$ sudo apt-get install libboost-python libboost-python-dev

If not, refer to the `Boost installation instructions`_ to build and install
Boost.Python manually. In the remainder of this section, let ``$BOOST_HEADERS``
refer to the directory that contains the Boost header files, and
``$BOOST_LIBS`` to the directory that contains the Boost library files. If you
installed Boost.Python with your distribution's package manager, these
directories are probably ``/usr/include`` and ``/usr/lib`` respectively.

.. _Boost installation instructions: http://www.boost.org/more/getting_started.html


If both prerequisites have been installed on your system, python-timbl can be
obtained through github::

	$ git clone git://github.com/proycon/python-timbl.git
	$ cd python-timbl

and can then be built and installed with the following command, use
``setup2.py`` for Python 2 and ``setup3.py`` for Python 3::

        $ sudo python setup3.py \
               build_ext --boost-include-dir=$BOOST_HEADERS \
                         --boost-library-dir=$BOOST_LIBS \
                         --timbl-include-dir=$TIMBL_HEADERS  \
                         --timbl-library-dir=$TIMBL_LIBS \
               install --prefix=/dir/to/install/in
               
This is the verbose variant, if default locations are used then the following may suffice already::

        $ sudo python setup3.py install               
               

The ``--prefix`` option to the install command denotes the directory in which the module is to be installed. If you have the appropriate system permissions, you can leave out this option. The module will then be installed in the Python system tree. Otherwise, make sure that the installation directory is in the module search path of your Python
system.

Usage
=======

python-timbl offers two interface to the timbl API. A low-level interface contained in the module ``timblapi``, which is very much like the C++ library, and a high-level object oriented interface in the ``timbl`` module, which offers a ``TimblClassifier`` class. 

timbl.TimblClassifier: High-level interface
----------------------------------------------

The high-level interface features as ``TimblClassifier`` class which can be used for training and testing classifiers. An example is provided in ``example.py``, parts of it will be discussed here.

After importing the necessary module, the classifier is instantiated by passing it an identifier which will be used as prefix used for all filenames written, and a string containing options just as you would pass them to Timbl::

	import timbl
	classifier = timbl.TimblClassifier("wsd-bank", "-a 0 -k 1" )

Normalization of theclass distribution is enabled by default (regardless of the ``-G`` option to Timbl), pass ``normalize=False`` to disable it.

Training instances can be added using the ``append(featurevector, classlabel)`` method::

	classifier.append( (1,0,0), 'financial')
	classifier.append( (0,1,0), 'furniture')
	classifier.append( (0,0,1), 'geographic')
	
Subsequently, you invoke the actual training, note that at each step Timbl may output considerable details about what it is doing to standard error output::

	classifier.train()
	
The results of this training is an instance base file, which you can save to file so you can load it again later::

	classifier.save()
		
	classifier = timbl.TimblClassifier("wsd-bank", "-a 0 -k 1" )	
	classifier.load() 	
	


The main advantage of the Python library is the fact that you can classify instances on the fly as follows, just pass a feature vector and optionally also a class label to ``classify(featurevector, classlabel)``::

	classlabel, distribution, distance = classifier.classify( (1,0,0) )

You can also create a test file and test it all at once::

	classifier = timbl.TimblClassifier("wsd-bank", "-a 0 -k 1" )
	classifier.load()
	classifier.addinstance("testfile", (1,0,0),'financial' ) #addinstance can be used to add instances to external files (use append() for training)
	classifier.addinstance("testfile", (0,1,0),'furniture' )
	classifier.addinstance("testfile", (0,0,1),'geograpic' )
	classifier.addinstance("testfile", (1,1,0),'geograpic' ) #this one will be wrongly classified as financial & furniture 
	classifier.test("testfile")

	print "Accuracy: ", classifier.getAccuracy()


Real multithreading support
-----------------------------

If you are writing a multithreaded Python application (i.e. using the
``threading`` module) and want to benefit from actual concurrency,
side-stepping Python's Global Interpreter Lock, add the parameter
``threading=True`` when invoking the ``TimblClassifier`` constructor.  Take
care to instantiate ``TimblClassifier`` *before* threading. You can then call
``TimblClassifier.classify()`` from within your threads.  Concurrency only
exists for this ``classify`` method.

If you do not set this option, everything will still work fine, but you won't benefit
from actual concurrency due to Python's the Global Interpret Lock.

	
timblapi: Low-level interface
-------------------------------

For documentation on the low level ``timblapi`` interface you can consult the TiMBL API guide.  Although this document actually describes the C++ interface to TiMBL, the latter is similar enough to its Python binding for this document to be a useful reference for python-timbl as well. For most part, the Python TiMBL interface follows the C++ version closely. The differences are listed below.

**Naming style**

In the C++ interface, method names are in *UpperCamelCase*; for example, ``Classify``, ``SetOptions``, etc. In contrast, the Python interface uses *lowerCamelCase*: ``classify``, ``setOptions``, etc.
Method overloading TiMBL's ``Classify`` methods use the C++ method overloading feature to provide three different kinds of outputs. Method overloading is non-existant in Python though; therefore, python-timbl has three differently named methods to mirror the functionality of the overloaded Classify method. The mapping is as follows::

	# bool TimblAPI::Classify(const std::string& Line,
	#                         std::string& result);
	#
	def TimblAPI.classify(line) -> bool, result

	#
	# bool TimblAPI::Classify(const std::string& Line,
	#                         std::string& result,
	#                         double& distance);
	#
	def TimblAPI.classify2(line) -> bool, string, distance

	#
	# bool TimblAPI::Classify(const std::string& Line,
	#                         std::string& result,
	#                         std::string& Distrib,
	#                         double& distance);
	#
	def TimblAPI.classify3(line, bool normalize=true,int requireddepth=0) -> bool, string, dictionary, distance

    #Thread-safe version of the above, releases and reacquires Python's Global Interprer Lock
	def TimblAPI.classify3safe(line, normalize, requireddepth=0) -> bool, string, dictionary, distance


Note that the ``classify3`` function returned a string representation of the
distribution in versions of python-timbl prior to 2015.08.12, now it returns an
actual dictionary. When using ``classify3safe`` (the thread-safe version) ,
ensure you first call initthreads after instantiating ``timblapi``, and
manually call the ``initthreading()`` method.


**Python-only methods**

Three TiMBL API methods print information to a standard C++ output stream object (ShowBestNeighbors, ShowOptions, ShowSettings, ShowSettings). In the Python interface, these methods will only work with Python (stream) objects that have a fileno method returning a valid file descriptor. Alternatively, three new methods are provided (bestNeighbo(u)rs, options, settings); these methods return the same information as a Python string object.



