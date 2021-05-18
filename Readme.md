# AccessibleRunner
AccessibleRunner is a simple utility for running console commands with screen reader accessible command output. This utility has been created with the aim to allow easy text selection, copying and clearing for the textual output of the user provided command.

## Keyboard shortcuts
AccessibleRunner supports the following keyboard shortcuts. On macOS, Use the Cmd key in place of the Control key.

* Control + Shift + D: Clears the output.
* Control + Shift + C: Copies the output to clipboard.
* Control + Q: Quits the application.

## Download
### Portable version for Windows
AccessibleRunner for Windows is available as a portable version. After downloading the ZIP file by clicking the link below, extract the archive and run the application using the AccessibleRunner.exe file. [Download AccessibleRunner for Windows (32 bit)](https://github.com/adamsamec/AccessibleRunner/blob/master/dist/Win-32bit/AccessibleRunner%20(Win-32bit).zip?raw=true).

### Source file
AccessibleRunner is developed in Python. [Download  the source file here](https://raw.githubusercontent.com/adamsamec/AccessibleRunner/master/src/AccessibleRunner.py?raw=true).

## Dependancies
The Python version of AccessibleRunner requires the [wxPython](https://www.wxpython.org) and [psutil](https://pypi.org/project/psutil/) Python modules, which can be installed using [PIP](https://pypi.org/project/pip/) like this:

    pip install wxPython
    pip install psutil
