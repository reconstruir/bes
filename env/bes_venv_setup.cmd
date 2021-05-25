@echo off

call %~dp0\..\bin\best.cmd pip_project install_requirements --root-dir "%~dp0\..\VE" bes_deps %~dp0\..\requirements.txt
call %~dp0\..\bin\best.cmd pip_project install_requirements --root-dir "%~dp0\..\VE" bes_deps %~dp0\..\requirements-dev.txt
