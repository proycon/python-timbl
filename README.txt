======================
 README: python-timbl
======================

:Author: Sander Canisius    (adapted and maintained by Maarten van Gompel <proycon@anaproy.nl>)
:Contact: S.V.M.Canisius@uvt.nl,  proycon@anaproy.nl
:Web site: http://github.com/proycon/python-timbl/
:Original web site: http://ilk.uvt.nl/~sander/software/python-timbl.html


python-timbl is a Python extension module wrapping the full TiMBL C++
programming interface. With this module, all functionality exposed
through the C++ interface is also available to Python scripts. Being
able to access the API from Python greatly facilitates prototyping
TiMBL-based applications.


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

python-timbl depends on two external packages, which must have been
built and/or installed on your system in order to successfully build
python-timbl. The first is TiMBL itself; download its tarball from
TiMBL's homepage and follow the installation instructions. In the
remainder of this section, it is assumed that ``$TIMBL_ROOT`` points
to the directory in which TiMBL was built. This directory contains
(among others) ``libTimbl.a`` and ``TimblAPI.h``.

The second prerequisite is Boost.Python, a library that facilitates
writing Python extension modules in C++. Many Linux distributions come
with prebuilt packages of Boost.Python. If so, install this package;
if not, refer to the `Boost installation instructions`_ to build and
install Boost.Python manually. In the remainder of this section, let
``$BOOST_HEADERS`` refer to the directory that contains the Boost
header files, and ``$BOOST_LIBS`` to the directory that contains the
Boost library files. If you installed Boost.Python with your
distribution's package manager, these directories are probably
``/usr/include`` and ``/usr/lib`` respectively.

.. _Boost installation instructions: http://www.boost.org/more/getting_started.html

If both prerequisites have been installed on your system, python-timbl
can be built and installed with the following command.

::

        python setup.py \
               build_ext --boost-include-dir=$BOOST_HEADERS \
                         --boost-library-dir=$BOOST_LIBS \
                         --timbl-include-dir=$TIMBL_ROOT \
                         --timbl-library-dir=$TIMBL_ROOT \
               install --prefix=/dir/to/install/in

The ``--prefix`` option to the install command denotes the directory
in which the module is to be installed. If you have the appropriate
system permissions, you can leave out this option. The module will
then be installed in the Python system tree. Otherwise, make sure that
the installation directory is in the module search path of your Python
system.
