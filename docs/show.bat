@echo off
rem ***********************************************************************
rem This batch script launches the generated documentation in your browser.
rem ***********************************************************************
REM START /wait %~dp0make.bat html
ECHO %~dp0build/html/index.html
START "" %~dp0build/html/index.html