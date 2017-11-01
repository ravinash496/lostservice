@echo off
rem ***********************************************************************
rem This batch script installs local dependencies, as well as those defined
rem in requirements.txt on Windows.
rem ***********************************************************************
pip install %~dp0dependencies\GDAL-2.1.3-cp36-cp36m-win_amd64.whl
pip install %~dp0dependencies\python_Levenshtein-0.12.0-cp36-cp36m-win_amd64.whl
pip install %~dp0dependencies\lxml-3.7.3-cp36-cp36m-win_amd64.whl
pip install %~dp0dependencies\Shapely-1.5.17-cp36-cp36m-win_amd64.whl
pip install -r %~dp0requirements.txt