@echo off

call %~dp0\..\bin\best.cmd pip_project install_requirements --root-dir "%~dp0\..\VE\bes" %~dp0\..\bes_requirements.txt %~dp0\..\bes_requirements_dev.txt

set PATH=%~dp0\..\bin;%PATH%
