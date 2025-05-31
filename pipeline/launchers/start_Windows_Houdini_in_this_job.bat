
@ECHO Loading config.env variables
FOR /F "eol=# tokens=*" %%i IN (..\config.env) DO SET %%i
@ECHO(
@ECHO(
@ECHO Pointing to this job's Package directory:
set HOUDINI_PACKAGE_DIR=%cd%\..\houdini_project_library\packages;%HOUDINI_PACKAGE_DIR%
@ECHO(
@ECHO(
@ECHO Starting Houdini:
start "" /b %HOUDINI_EXE%

