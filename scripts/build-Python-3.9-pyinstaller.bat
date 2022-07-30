C:\Users\asamec\AppData\Local\Programs\Python\Python39-32\Scripts\pyinstaller.exe -w --additional-hooks-dir . --distpath ../build/pyinstaller --workpath ../temp --specpath ../temp/AccessibleRunner ../src/AccessibleRunner.py

xcopy ..\src\sounds ..\build\cx_Freeze\AccessibleRunner\sounds\
xcopy ..\src\md ..\build\cx_Freeze\AccessibleRunner\md\
xcopy ..\src\config.default.json ..\build\cx_Freeze\AccessibleRunner

echo Deleting the 'temp' directory...
title Delete the 'temp' directory?
rmdir /s ..\temp

title Build completed
pause
