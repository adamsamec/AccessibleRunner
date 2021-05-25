cd src
C:\Users\asamec\AppData\Local\Programs\Python\Python39-32\Scripts\pyinstaller.exe -w --distpath ../build --workpath ../temp --specpath ../temp/AccessibleRunner AccessibleRunner.py

xcopy sounds ..\build\AccessibleRunner\sounds\
xcopy config.orig.json ..\build\AccessibleRunner

echo Deleting the 'temp' directory...
title Delete the 'temp' directory?
rmdir /s ..\temp

title Build completed
pause
