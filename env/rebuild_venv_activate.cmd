@echo off

call %~dp0\rebuild_venv_setup.cmd
call %~dp0\..\VE\rebuild_venv\Scripts\activate.rebuild
set PYTHONPATH=%~dp0\..\lib;%PYTHONPATH%
set PATH=%~dp0\..\bin;%PATH%
