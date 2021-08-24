cd src
C:\Users\asamec\AppData\Local\Programs\Python\Python39-32\Scripts\pyinstaller.exe -w --additional-hooks-dir . --distpath ../build --workpath ../temp --specpath ../temp/AccessibleRunner AccessibleRunner.py

xcopy sounds ..\build\AccessibleRunner\sounds\
xcopy md ..\build\AccessibleRunner\md\
xcopy config.default.json ..\build\AccessibleRunner

echo Deleting the 'temp' directory...
title Delete the 'temp' directory?
rmdir /s ..\temp

cd ..
title Build completed
pause
