#!/bin/bash

egg=foo-1.0.0-py2.7.egg

rm -f $egg

set - e

./make_egg.sh

PYTHONPATH=$PYTHONPATH:$egg pyinstaller --log INFO --clean -F ./bin/foo_prog.py
