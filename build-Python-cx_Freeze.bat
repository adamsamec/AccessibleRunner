cd src
python setup-cx_Freeze.py build

xcopy sounds ..\build\cx_Freeze\AccessibleRunner\sounds\
xcopy md ..\build\cx_Freeze\AccessibleRunner\md\
xcopy config.default.json ..\build\cx_Freeze\AccessibleRunner

cd ..
title build completed
pause
