@echo off
set PYTHONPATH=%~dp0\..\lib;%PYTHONPATH%
python %~dp0\best.py %*
