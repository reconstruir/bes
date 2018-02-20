#!/bin/bash

PYTHONPATH=lib python -v ./bin/foo_prog.py
rv=$?
exit $rv
