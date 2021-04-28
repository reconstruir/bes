@echo off
set PYTHONPATH=%~dp0\..\lib;%PYTHONPATH%
python %~dp0\bes_test.py --dont-hack-env %*

