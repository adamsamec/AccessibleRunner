# AccessibleRunner
AccessibleRunner is a simple Windows utility for running console commands with screen reader accessible command output. This utility has been created with the aim to allow easy text selection, copying and clearing for the textual output of the user provided command.

## Features
* Command and working directory history. History items can be choosed by pressing the Down arrow key when the command or working directory combobox is focused.
* In settings, AccessibleRunner can be configured so that notification sound will be played whenever the given regular expression mmatches a new output string. This way, if AccessibleRunner is not in foreground, one can get notified when a given string, such as "ERROR", occurs in new output, or when a successful compilation occurs by detecting another string.

## Keyboard shortcuts
AccessibleRunner supports the following keyboard shortcuts.

* Control + Enter: Runs the command and focuses the output textbox.
* Control + K: Kills the running process.
* Control + L: Focuses the command textbox.
* Control + D: Clears the output textbox.
* Control + Shift + C: Copies the output to clipboard.
* Control + Q: Quits the application.

## Download
### Portable version for Windows
AccessibleRunner for Windows is available as a portable version. After downloading the ZIP file by clicking the link below, extract the archive and run the application using the AccessibleRunner.exe file. [Download AccessibleRunner for Windows (32 bit)](https://github.com/adamsamec/AccessibleRunner/blob/master/dist/AccessibleRunner%20(Win-32bit).zip?raw=true).

### Source files
AccessibleRunner is developed in Python. [Download the source files ZIP archive here](https://github.com/adamsamec/AccessibleRunner/blob/master/dist/AccessibleRunner%20(source).zip?raw=true). After downloading the ZIP file, extract it and run AccessibleRunner by executing the following command in the extracted directory:

    python AccessibleRunner.py

## Dependancies
The Python version of AccessibleRunner requires the [wxPython](https://www.wxpython.org), [psutil](https://pypi.org/project/psutil/) and [playsound](https://pypi.org/project/playsound/) Python modules, which can be installed using [PIP](https://pypi.org/project/pip/) like this:

    pip install wxPython
    pip install psutil
    pip install playsound
