
@ECHO Pointing to this job's Package directory:
set HOUDINI_PACKAGE_DIR=%cd%\..\packages;%HOUDINI_PACKAGE_DIR%
@ECHO(
@ECHO(
@ECHO Starting Houdini:
start "" /b "C:\Program Files\Side Effects Software\Houdini 20.5.584\bin\houdini.exe"

