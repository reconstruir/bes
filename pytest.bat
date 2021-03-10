@echo off
cls
set PYTHONPATH=C:\Users\ramiro\proj\bes\lib
python -m pytest --continue-on-collection-errors %*

