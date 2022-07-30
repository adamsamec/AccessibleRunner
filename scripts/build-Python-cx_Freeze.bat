python setup-cx_Freeze.py build

xcopy ..\src\sounds ..\build\cx_Freeze\AccessibleRunner\sounds\
xcopy ..\src\md ..\build\cx_Freeze\AccessibleRunner\md\
xcopy ..\src\config.default.json ..\build\cx_Freeze\AccessibleRunner

title Build completed
pause
