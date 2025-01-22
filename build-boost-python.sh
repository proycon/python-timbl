#!/bin/sh


# build boost-python from source on AlmaLinux 8 in manylinux_2_28 container (do not use in other contexts)

set -e

#var gets set bu cibuildwheel, assign to PYTHON_HOME for boost
export PYTHON_HOME=$Python_ROOT_DIR

cd /tmp/
wget -q https://github.com/boostorg/boost/releases/download/boost-1.87.0/boost-1.87.0-cmake.tar.gz
tar -xzf boost-1.87.0-cmake.tar.gz
cd boost-1.87.0
./bootstrap.sh
./b2 --clean
./b2 install --with-python --prefix=/usr
cd $PREVPWD
