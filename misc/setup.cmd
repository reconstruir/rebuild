@echo off

call %~dp0\..\..\bes\misc\setup.cmd

set PYTHONPATH=%~dp0\..\lib;%PYTHONPATH%
set PATH=%~dp0\..\bin;%PATH%
