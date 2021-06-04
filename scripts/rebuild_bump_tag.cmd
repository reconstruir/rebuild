@echo off

call %~dp0\..\bin\rebuild.cmd git bump_tag --prefix "release/" -v
exit /b %ERRORLEVEL%
