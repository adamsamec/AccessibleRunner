# AccessibleRunner
AccessibleRunner is a simple cross-platform utility for running console commands with screen reader accessible command output. This utility has been created with the aim to allow easy text selection, copying and clearing for the textual output of the user provided command.

## Keyboard shortcuts
AccessibleRunner supports the following keyboard shortcuts. On macOS, Use the Cmd key in place of the Control key.

* Control + Shift + D: Clears the output.
* Control + Shift + C: Copies the output to clipboard.
* Control + Q: Quits the application.

## Download
While the app is created in Python, the following standalone binaries with no dependancies are also provided for download.

* [Download AccessibleRunner for Windows](https://github.com/adamsamec/AccessibleRunner/blob/master/dist/win-x64/AccessibleRunner.exe?raw=true).

## Dependancies
The Python version of AccessibleRunner requires the [wxPython](https://www.wxpython.org) and [psutil](https://pypi.org/project/psutil/) Python modules, which can be installed using [PIP](https://pypi.org/project/pip/) like this:

    pip install wxPython
    pip install psutil
