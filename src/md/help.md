## Introduction
AccessibleRunner is a Windows utility for running console commands with screen reader accessible command output. This utility has been created with the aim to allow easy text selection, searching, copying and clearing for the textual output of the user provided command.

## Features
* Command and working directory history. Up to ten history items can be chosen by pressing the Down arrow key when the command or working directory combobox is focused.
* Find text in command output. Press Control + F to show the search dialog, access the search history by pressing the Down arrow key when the find text combobox is focused, hit Enter to find the next occurrence. Successive occurrences can be found using the F3 key, press Shift + F3 for searching backward. The search may or not may be case sensitive. 
* In settings, AccessibleRunner can be configured so that notification sound will be played whenever a given regular expression matches a text in the output line of the currently running command. This way, if AccessibleRunner is in background, one can be notified when a given string, such as "ERROR", occurs in new output, or when a successful compilation occurs by detecting another given string.
* In settings, output line substitution feature can be enabled which allows replacement of every output line matched by the provided regular expression with the provided replacement string. This way you can, for instance, get rid of timestamps at the begining of certain log output lines. In the replacement string, you can use \1, \2, etc. as the back-reference to the groups captured in the regular expression. By pressing the Down arrow key when on the regular expression or replacement combobox, you can access the history of up to 10 previously entered items.
* If screen reader is running, the command output is sent to the screen reader, with the possibility to output even when AccessibleRunner is in background - this can also be configured in Settings. The output is both via speech and braille.

## Keyboard shortcuts
AccessibleRunner supports the following global keyboard shortcuts.

* Control + Enter: Runs the command and focuses the output textbox.
* Control + K: Kills the running process.
* Control + L: Focuses the command textbox.
* Control + O: Focuses the output textbox.
* Control + F: Shows the find text dialog.
* F3: Find the next text occurance.
* Shift + F3: Find the previous text occurance.
* Control + D: Clears the output textbox.
* Control + Shift + C: Copies the whole output textbox content to clipboard.
* Control + Q: Quits the application.
