@echo off
set PYTHONPATH=%~dp0\..\lib;%PYTHONPATH%
"c:\Program Files\Python39\python.exe" %~dp0\bes_test.py --dont-hack-env %*

