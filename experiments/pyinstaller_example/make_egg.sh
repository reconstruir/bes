#!/bin/bash

here=$(pwd)
tmp=/tmp/megg$$
rm -rf $tmp
set -e 
mkdir -p $tmp
cp -a bin lib $tmp
cd $tmp/lib
python setup.py bdist_egg
cp dist/foo-1.0.0-py2.7.egg $here
rm -rf $tmp
exit 0
