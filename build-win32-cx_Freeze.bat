cd src
C:\Users\asamec\AppData\Local\Programs\Python\Python39-32\python.exe setup-cx_Freeze.py build
xcopy sounds ..\build\AccessibleRunner-cx_Freeze\sounds\
xcopy config.default.json ..\build\AccessibleRunner-cx_Freeze
title build completed
pause
