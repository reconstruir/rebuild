@echo off

call %~dp0\..\bin\rebuild.cmd pip_project install_requirements --root-dir "%~dp0\..\VE" rebuild_venv %~dp0\..\requirements.txt
call %~dp0\..\bin\rebuild.cmd pip_project install_requirements --root-dir "%~dp0\..\VE" rebuild_venv %~dp0\..\requirements-dev.txt
