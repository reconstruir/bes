@echo off
set _this_dir=%~dp0
set PYTHONPATH=%_this_dir%\..\lib;%PYTHONPATH%
python %_this_dir%\best.py %*


