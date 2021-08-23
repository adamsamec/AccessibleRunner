import os
import sys
import wx
from cefpython3 import cefpython as cef
import re
import markdown2

import util

# Main frame class.
class MainFrame(wx.Frame):

  WINDOW_TITLE_SEPARATOR = ' | '
  WINDOW_TITLE = 'AccessibleRunner'

  # Initializes the object by linking it with the given AccessibilityRunner and Config objects, binding the event handlers, and creating the GUI.
  def __init__(self, runner, config, title, parent = None):
    super(MainFrame, self).__init__(parent, title = title)
    self.runner = runner
    self.config = config
    
    self.Bind(wx.EVT_CLOSE, self.onWindowClose)
    self.Bind(wx.EVT_ACTIVATE, self.onWindowActivate)
    self.Bind(wx.EVT_CHAR_HOOK  , self.charHook)
    
    self.addWidgets()
    self.Centre()
    self.Show()
    self.Fit()
    
  # Adds all the initial widgets to this frame.
  def addWidgets(self):
    self.panel = wx.Panel(self)    
    vbox = wx.BoxSizer(wx.VERTICAL)
    history = self.config.history
    settings = self.config.settings
    
    # Command combobox
    commandHbox = wx.BoxSizer(wx.HORIZONTAL)
    commandLabel = wx.StaticText(self.panel, -1, 'Command') 
    commandHbox.Add(commandLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.commandCombobox = wx.ComboBox(self.panel, choices = history['commands'])
    commandHbox.Add(self.commandCombobox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Working directory combobox
    directoryHbox = wx.BoxSizer(wx.HORIZONTAL)
    directoryLabel = wx.StaticText(self.panel, -1, 'Working directory')
    directoryHbox.Add(directoryLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.directoryCombobox = wx.ComboBox(self.panel, choices = history['directories'])
    directoryHbox.Add(self.directoryCombobox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Working directory choose button
    self.chooseDirectoryButton = wx.Button(self.panel, label = 'Choose directory')
    self.chooseDirectoryButton.Bind(wx.EVT_BUTTON, self.onChooseDirectoryButtonClick)
    directoryHbox.Add(self.chooseDirectoryButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Use shell checkbox
    useShellHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.useShellCheckbox = wx.CheckBox(self.panel, label = 'Execute using shell', pos = (10, 10))
    self.useShellCheckbox.SetValue(settings['useShell'])
    useShellHbox.Add(self.useShellCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    runAndKillHbox = wx.BoxSizer(wx.HORIZONTAL)

    # Run button
    self.runButton = wx.Button(self.panel, label = 'Run')
    self.runButton.Bind(wx.EVT_BUTTON, self.onRunButtonClick)
    runAndKillHbox.Add(self.runButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Kill button
    self.killButton = wx.Button(self.panel, label = 'Kill process')
    self.killButton.Disable()
    self.killButton.Bind(wx.EVT_BUTTON, self.onKillButtonClick)
    runAndKillHbox.Add(self.killButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Output textbox
    outputHbox = wx.BoxSizer(wx.HORIZONTAL)
    outputLabel = wx.StaticText(self.panel, -1, 'Output')
    outputHbox.Add(outputLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.outputTextbox = wx.TextCtrl(self.panel, size = (600, 150), style = wx.TE_MULTILINE | wx.TE_READONLY)
    outputHbox.Add(self.outputTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    bottomButtonsHbox = wx.BoxSizer(wx.HORIZONTAL)
    
    # Clear button
    self.clearButton = wx.Button(self.panel, label = 'Clear output')
    self.clearButton.Bind(wx.EVT_BUTTON, self.onClearButtonClick)
    bottomButtonsHbox.Add(self.clearButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Copy button
    self.copyButton = wx.Button(self.panel, label = 'Copy output')
    self.copyButton.Bind(wx.EVT_BUTTON, self.onCopyButtonClick)
    bottomButtonsHbox.Add(self.copyButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
        # Settings button
    self.settingsButton = wx.Button(self.panel, label = 'Settings')
    self.settingsButton.Bind(wx.EVT_BUTTON, self.onSettingsButtonClick)
    bottomButtonsHbox.Add(self.settingsButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    vbox.Add(commandHbox)
    vbox.Add(directoryHbox)
        # Help button
    self.helpButton = wx.Button(self.panel, label = 'Help')
    self.helpButton.Bind(wx.EVT_BUTTON, self.onHelpButtonClick)
    bottomButtonsHbox.Add(self.helpButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    vbox.Add(useShellHbox)
    vbox.Add(runAndKillHbox)
    vbox.Add(outputHbox)
    vbox.Add(bottomButtonsHbox)

    self.panel.SetSizer(vbox)
    
  # Sets the GUI state as running.
  def setAsRunning(self):
    self.SetTitle('{}{}{}'.format(self.commandCombobox.GetValue().strip(), MainFrame.WINDOW_TITLE_SEPARATOR, MainFrame.WINDOW_TITLE))
    self.runButton.Disable()
    self.killButton.Enable()

  # Sets the GUI state as not running.
  def setAsNotRunning(self):
    self.SetTitle(MainFrame.WINDOW_TITLE)
    self.killButton.Disable()
    self.runButton.Enable()

  # Cleans everything and closes the main window.
  def cleanAndClose(self):
    settings = {
      'useShell': self.useShellCheckbox.GetValue(),
    }
    self.runner.mergeSettings(settings)
    self.runner.clean()
    self.Destroy()
    
  # Runs the process using the values of the relevant textboxes.
  def runProcess(self):
    command = self.commandCombobox.GetValue()
    directory = self.directoryCombobox.GetValue()
    useShell = self.useShellCheckbox.GetValue()
    self.runner.runProcess(command, directory, useShell)
    
  # Sets the given choices to the given combobox.
  def setChoices(self, combobox, choices):
    value = combobox.GetValue()
    combobox.Clear()
    combobox.SetValue(value)
    for choice in choices:
      combobox.Append(choice)
      
  # Sets the given choices to the command combobox.
  def setCommandChoices(self, choices):
    self.setChoices(self.commandCombobox, choices)

  # Sets the given choices to the directory combobox.
  def setDirectoryChoices(self, choices):
    self.setChoices(self.directoryCombobox, choices)

  # Sets or appends the given text to the command output textbox.
  def setOutput(self, text, append = False):
    if append:
      self.outputTextbox.SetValue(self.outputTextbox.GetValue() + text)
    else:
      self.outputTextbox.SetValue(text)

  # Gets the text of the command output textbox.
  def getOutput(self):
    return self.outputTextbox.GetValue()
    
  # Moves the cursor of the output textbox to the given position and outputs the line at that position in the given text via screen reader.
  def moveCursorAndOutputLine(self, text, position):
    self.outputTextbox.SetInsertionPoint(position)
    line = util.getLine(text, position)
    self.runner.srOutput(line)
      
  # Finds the next occurance of the  text stored in the temporary settings in the output textbox, moves the insertion point to that occurance and outputs the found word via screen reader.
  def findText(self, backward = False):
    settings = self.config.settings
    findText = settings['findText']
    if len(findText) == 0:
      return
    
    # Replace the \n line endings in the output text with the \r\n (Windows) ones
    origCaseOutputText = self.outputTextbox.GetValue().replace('\n', '\r\n')
    
    # Determine whether find should be case sensitive
    if settings['ignoreCase']:
      findText = findText.lower()
      outputText = origCaseOutputText.lower()
    else:
      outputText = origCaseOutputText
    
    cursorPosition = self.outputTextbox.GetInsertionPoint()
    if not backward:
      # Find forward, i.e., find the first text occurrance in the output text substring starting at the cursor position + 1 until the end
      findStartPosition = cursorPosition + 1
      foundPosition = outputText.find(findText, findStartPosition)
      if foundPosition >= 0:
        self.moveCursorAndOutputLine(origCaseOutputText, foundPosition)
      else:
        self.runner.playNotFound()
        
        # Wrap the find to the top, i.e., find the first text occurance again, but now starting at the begining of the output text and ending at the foundPosition
        foundPosition = outputText.find(findText, 0, foundPosition)
        if foundPosition >= 0:
          self.runner.srOutput('Wrapping to top', True)
          self.moveCursorAndOutputLine(origCaseOutputText, foundPosition)
        else:
          self.runner.srOutput('Search string not found')
    else:
      # Find backward, i.e., find the last text occurrance in the output text substring starting at the begining until the cursor position - 1
      findEndPosition = cursorPosition - 1
      foundPosition = outputText.rfind(findText, 0, findEndPosition)
      if foundPosition >= 0:
        self.moveCursorAndOutputLine(origCaseOutputText, foundPosition)
      else:
        self.runner.playNotFound()
        
        # Wrap the find to the bottom, i.e., find the last text occurrance again, but now starting at the previously found position and ending at the end of the output text
        foundPosition = outputText.rfind(findText, 0)
        if foundPosition >= 0:
          self.runner.srOutput('Wrapping to bottom', True)
          self.moveCursorAndOutputLine(origCaseOutputText, foundPosition)
        else:
          self.runner.srOutput('Search string not found', True)
    
  # Handles  the window close event.
  def onWindowClose(self, event):
    self.cleanAndClose()
    
  # Handles  the window activate event.
  def onWindowActivate(self, event):
    self.runner.setActive(event.GetActive())
    event.Skip()

  # Handles  the key press events for the whole frame.
  def charHook(self, event):
    key = event.GetKeyCode()
    modifiers = event.GetModifiers()
    
    # Check if no modifiers, only Control, or only Control + Shift are pressed
    # On macOS the control key is actually the Cmd key
    noModifiers = not event.HasAnyModifiers()
    onlyControlDown = modifiers == wx.MOD_CONTROL
    onlyShiftDown = modifiers == (wx.MOD_SHIFT)
    onlyControlAndShiftDown = modifiers == (wx.MOD_CONTROL | wx.MOD_SHIFT)
    
    # Control + Enter
    if (key == wx.WXK_RETURN) and onlyControlDown:
      self.outputTextbox.SetFocus()
      self.runProcess()
      
    # Control + K
    elif (key == ord('K')) and onlyControlDown:
      self.runner.killProcessTree()

    # Control + L
    elif (key == ord('L')) and onlyControlDown:
      self.commandCombobox.SetFocus()

    # Control + O
    elif (key == ord('O')) and onlyControlDown:
      self.outputTextbox.SetFocus()

    # Control + F
    elif (key == ord('F')) and onlyControlDown:
      self.showFindDialog()
      
    # F3
    elif (key == wx.WXK_F3) and noModifiers:
      self.findText()
      
    # Shift + F3
    elif (key == wx.WXK_F3) and onlyShiftDown:
      self.findText(True)

    # Control + Q
    elif (key == ord('Q')) and onlyControlDown:
      self.cleanAndClose()
      
    # Control + Shift + C
    elif (key == ord('C')) and onlyControlAndShiftDown:
      self.runner.copyOutput()
      
    # Control + D
    elif (key == ord('D')) and onlyControlDown:
      self.runner.clearOutput()
    
    else:
      event.Skip()
    
  # Handles the choose directory button click.
  def onChooseDirectoryButtonClick(self, event):
    # Determine the default path from the working directory combobox
    path = self.directoryCombobox.GetValue()
    path = path if os.path.isdir(path) else ''
    
    # Create and show the directory chooser dialog
    dialog = wx.DirDialog(self, message = 'Choose a working directory', defaultPath = path)
    if dialog.ShowModal() == wx.ID_OK:
      path = dialog.GetPath()
      self.directoryCombobox.SetValue(path)
      self.directoryCombobox.SetFocus()
    dialog.Destroy()
    
  # Handles the run button click.
  def onRunButtonClick(self, event):
    self.runProcess()
    
  # Handles the kill process button click.
  def onKillButtonClick(self, event):
    self.runner.killProcessTree()
    
  # Handles the clear button click.
  def onClearButtonClick(self, event):
    self.runner.clearOutput()
    
  # Handles the copy button click.
  def onCopyButtonClick(self, event):
    self.runner.copyOutput()
    
  # Handles the settings button click.
  def onSettingsButtonClick(self, event):
    SettingsDialog(self.runner, self.config, title = 'Settings{}{}'.format(MainFrame.WINDOW_TITLE_SEPARATOR, MainFrame.WINDOW_TITLE), parent = self)

  # Handles the settings button click.
  def onHelpButtonClick(self, event):
    helpDialog = HelpHTMLDialog(title = 'Help{}{}'.format(MainFrame.WINDOW_TITLE_SEPARATOR, MainFrame.WINDOW_TITLE), parent = self)

  # Shows the find text dialog
  def showFindDialog(self):
    FindDialog(self.runner, self.config, title = 'Find text', parent = self)

# Settings dialog class.
class SettingsDialog(wx.Dialog):

  # Initializes the object by linking it with the given AccessibilityRunner and Config objects, binding the event handlers, and creating the GUI.
  def __init__(self, runner, config, title, parent = None):
    super(SettingsDialog, self).__init__(parent = parent, title = title)
    self.runner = runner
    self.config = config
    
    self.Bind(wx.EVT_CHAR_HOOK  , self.charHook)
    
    self.addWidgets()
    self.Centre()
    self.ShowModal()
    self.Fit()

  # Adds all the initial widgets to this dialog.
  def addWidgets(self):
    self.panel = wx.Panel(self)    
    vbox = wx.BoxSizer(wx.VERTICAL)
    settings = self.config.settings
    history = self.config.history
    
    # Screen reader output in background checkbox
    bgOutputHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.bgOutputCheckbox = wx.CheckBox(self.panel, label = 'Screen reader output in background', pos = (10, 10))
    self.bgOutputCheckbox.Bind(wx.EVT_CHECKBOX, self.onBgOutputCheckboxClick)
    self.bgOutputCheckbox.SetValue(settings['srBgOutput'])
    bgOutputHbox.Add(self.bgOutputCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Play success sound checkbox
    playSuccessCheckboxHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.playSuccessCheckbox = wx.CheckBox(self.panel, label = 'Play success sound when regular expression matches', pos = (10, 10))
    self.playSuccessCheckbox.SetValue(settings['playSuccessSound'])
    self.playSuccessCheckbox.Bind(wx.EVT_CHECKBOX, self.onPlaySuccessCheckboxClick)
    playSuccessCheckboxHbox.Add(self.playSuccessCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Success regex textbox
    successRegexHbox = wx.BoxSizer(wx.HORIZONTAL)
    successRegexLabel = wx.StaticText(self.panel, -1, 'Success regular expression') 
    successRegexHbox.Add(successRegexLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.successRegexTextbox = wx.TextCtrl(self.panel, value = settings['successRegex'])
    if not settings['playSuccessSound']:
      self.successRegexTextbox.Disable()
    successRegexHbox.Add(self.successRegexTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Play error sound checkbox
    playErrorCheckboxHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.playErrorCheckbox = wx.CheckBox(self.panel, label = 'Play error sound when regular expression matches', pos = (10, 10))
    self.playErrorCheckbox.SetValue(settings['playErrorSound'])
    self.playErrorCheckbox.Bind(wx.EVT_CHECKBOX, self.onPlayErrorCheckboxClick)
    playErrorCheckboxHbox.Add(self.playErrorCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Error regex textbox
    errorRegexHbox = wx.BoxSizer(wx.HORIZONTAL)
    errorRegexLabel = wx.StaticText(self.panel, -1, 'Error regular expression') 
    errorRegexHbox.Add(errorRegexLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.errorRegexTextbox = wx.TextCtrl(self.panel, value = settings['errorRegex'])
    if not settings['playErrorSound']:
      self.errorRegexTextbox.Disable()
    errorRegexHbox.Add(self.errorRegexTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Enable line substitution checkbox
    lineSubstitutionCheckboxHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.lineSubstitutionCheckbox = wx.CheckBox(self.panel, label = 'Enable line substitution', pos = (10, 10))
    self.lineSubstitutionCheckbox.SetValue(settings['lineSubstitution'])
    self.lineSubstitutionCheckbox.Bind(wx.EVT_CHECKBOX, self.onLineSubstitutionCheckboxClick)
    lineSubstitutionCheckboxHbox.Add(self.lineSubstitutionCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Line substitution regular expression combobox
    substitutionRegexHbox = wx.BoxSizer(wx.HORIZONTAL)
    substitutionRegexLabel = wx.StaticText(self.panel, -1, 'Line substitution regular expression') 
    substitutionRegexHbox.Add(substitutionRegexLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.substitutionRegexCombobox = wx.ComboBox(self.panel, value = settings['substitutionRegex'], choices = history['substitutionRegexes'])
    if not settings['lineSubstitution']:
      self.substitutionRegexCombobox.Disable()
    substitutionRegexHbox.Add(self.substitutionRegexCombobox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Line substitution replacement combobox
    substitutionReplacementHbox = wx.BoxSizer(wx.HORIZONTAL)
    substitutionReplacementLabel = wx.StaticText(self.panel, -1, 'Line substitution replacement (use \\1, \\2 etc. for back-references)') 
    substitutionReplacementHbox.Add(substitutionReplacementLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.substitutionReplacementCombobox = wx.ComboBox(self.panel, value = settings['substitutionReplacement'], choices = history['substitutionReplacements'])
    if not settings['lineSubstitution']:
      self.substitutionReplacementCombobox.Disable()
    substitutionReplacementHbox.Add(self.substitutionReplacementCombobox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    cancelAndCloseHbox = wx.BoxSizer(wx.HORIZONTAL)
    
    # Cancel button
    self.cancelButton = wx.Button(self.panel, label = 'Cancel')
    self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButtonClick)
    cancelAndCloseHbox.Add(self.cancelButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Save and close button
    self.closeButton = wx.Button(self.panel, label = 'Save and close')
    self.closeButton.SetDefault()
    self.closeButton.Bind(wx.EVT_BUTTON, self.onCloseButtonClick)
    cancelAndCloseHbox.Add(self.closeButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    vbox.Add(bgOutputHbox)
    vbox.Add(playSuccessCheckboxHbox)
    vbox.Add(successRegexHbox)
    vbox.Add(playErrorCheckboxHbox)
    vbox.Add(errorRegexHbox)
    vbox.Add(lineSubstitutionCheckboxHbox)
    vbox.Add(substitutionRegexHbox)
    vbox.Add(substitutionReplacementHbox)
    vbox.Add(cancelAndCloseHbox)
    self.panel.SetSizer(vbox)
    
  # Closes the dialog without any changes.
  def close(self):
    self.Destroy()
    
  # Handles  the key press events for the whole dialog.
  def charHook(self, event):
    key = event.GetKeyCode()
    modifiers = event.GetModifiers()
    
    # Check if no modifiers are pressed
    noModifiers = not event.HasAnyModifiers()
    
    # Escape
    if key == wx.WXK_ESCAPE:
      self.close()
    else:
      event.Skip()

  # Handles the screen reader output in background checkbox click.
  def onBgOutputCheckboxClick(self, event):
    settings = {
      'srBgOutput': self.bgOutputCheckbox.GetValue(),
    }
    self.runner.mergeSettings(settings)

  # Handles the play success sound checkbox click.
  def onPlaySuccessCheckboxClick(self, event):
    if self.playSuccessCheckbox.GetValue():
      self.successRegexTextbox.Enable()
    else:
      self.successRegexTextbox.Disable()

  # Handles the play error sound checkbox click.
  def onPlayErrorCheckboxClick(self, event):
    if self.playErrorCheckbox.GetValue():
      self.errorRegexTextbox.Enable()
    else:
      self.errorRegexTextbox.Disable()

  # Handles the enable line substitution checkbox click.
  def onLineSubstitutionCheckboxClick(self, event):
    if self.lineSubstitutionCheckbox.GetValue():
      self.substitutionRegexCombobox.Enable()
      self.substitutionReplacementCombobox.Enable()
    else:
      self.substitutionRegexCombobox.Disable()
      self.substitutionReplacementCombobox.Disable()

  # Handles the cancel button click.
  def onCancelButtonClick(self, event):
    self.close()

  # Handles the save and close button click.
  def onCloseButtonClick(self, event):
    settings = {
      'playSuccessSound': self.playSuccessCheckbox.GetValue(),
      'successRegex': self.successRegexTextbox.GetValue(),
      'playErrorSound': self.playErrorCheckbox.GetValue(),
      'errorRegex': self.errorRegexTextbox.GetValue(),
      'lineSubstitution': self.lineSubstitutionCheckbox.GetValue(),
      'substitutionRegex': self.substitutionRegexCombobox.GetValue(),
      'substitutionReplacement': self.substitutionReplacementCombobox.GetValue(),
    }
    self.runner.mergeSettings(settings)
    self.runner.addToSubstitutionRegexesHistory(settings['substitutionRegex'])
    self.runner.addToSubstitutionReplacementsHistory(settings['substitutionReplacement'])
    self.Destroy()

# Find text dialog class.
class FindDialog(wx.Dialog):

  # Initializes the object by linking it with the given AccessibilityRunner and Config objects, binding the event handlers, and creating the GUI.
  def __init__(self, runner, config, title, parent = None):
    super(FindDialog, self).__init__(parent = parent, title = title)
    self.parent = parent
    self.runner = runner
    self.config = config
    
    self.Bind(wx.EVT_CHAR_HOOK  , self.charHook)
    
    self.addWidgets()
    self.Centre()
    self.ShowModal()
    self.Fit()

  # Adds all the initial widgets to this dialog.
  def addWidgets(self):
    self.panel = wx.Panel(self)    
    vbox = wx.BoxSizer(wx.VERTICAL)
    history = self.config.history
    settings = self.config.settings
    
    # Find text combobox
    findComboboxHbox = wx.BoxSizer(wx.HORIZONTAL)
    findLabel = wx.StaticText(self.panel, -1, 'Find what') 
    findComboboxHbox.Add(findLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.findCombobox = wx.ComboBox(self.panel, choices = history['findTexts'], value = settings['findText'])
    findComboboxHbox.Add(self.findCombobox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Find backward checkbox
    backwardHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.backwardCheckbox = wx.CheckBox(self.panel, label = 'Backward direction', pos = (10, 10))
    self.backwardCheckbox.SetValue(settings['findBackward'])
    self.backwardCheckbox.Bind(wx.EVT_CHECKBOX, self.onBackwardCheckboxClick)
    backwardHbox.Add(self.backwardCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Ignore case checkbox
    ignoreCaseHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.ignoreCaseCheckbox = wx.CheckBox(self.panel, label = 'Ignore case', pos = (10, 10))
    self.ignoreCaseCheckbox.SetValue(settings['ignoreCase'])
    self.ignoreCaseCheckbox.Bind(wx.EVT_CHECKBOX, self.onIgnoreCaseCheckboxClick)
    ignoreCaseHbox.Add(self.ignoreCaseCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Find next button
    findButtonHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.findButton = wx.Button(self.panel, label = 'Find next')
    self.findButton.SetDefault()
    self.findButton.Bind(wx.EVT_BUTTON, self.onFindButtonClick)
    findButtonHbox.Add(self.findButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    vbox.Add(findComboboxHbox)
    vbox.Add(backwardHbox)
    vbox.Add(ignoreCaseHbox)
    vbox.Add(findButtonHbox)

    self.panel.SetSizer(vbox)
    
  # Closes the dialog without any changes.
  def close(self):
    self.Destroy()
    
  # Temporary saves the find dialog combobox text and backward checkbox state, finds the next occurance of the text in the output textbox and moves the insertion point to that occurance. Finally closes the dialog.
  def findTextAndClose(self):
    settings = {
      'findText': self.findCombobox.GetValue(),
      'findBackward': self.backwardCheckbox.GetValue(),
    }
    self.runner.mergeSettings(settings)
    
    self.runner.addToFindTextsHistory(settings['findText'])
    self.parent.findText(settings['findBackward'])
    self.close()
    
  # Handles  the key press events for the whole dialog.
  def charHook(self, event):
    key = event.GetKeyCode()
    modifiers = event.GetModifiers()
    
    # Check if no modifiers are pressed
    noModifiers = not event.HasAnyModifiers()
    
    # Escape
    if key == wx.WXK_ESCAPE:
      self.close()
      
    # Enter
    elif key == wx.WXK_RETURN:
      self.findTextAndClose()
    else:
      event.Skip()

  # Handles the find backward checkbox click.
  def onBackwardCheckboxClick(self, event):
    settings = {
      'findBackward': self.backwardCheckbox.GetValue(),
    }
    self.runner.mergeSettings(settings)

  # Handles the ignore case checkbox click.
  def onIgnoreCaseCheckboxClick(self, event):
    settings = {
      'ignoreCase': self.ignoreCaseCheckbox.GetValue(),
    }
    self.runner.mergeSettings(settings)

  # Handles the find text button click.
  def onFindButtonClick(self, event):
    self.findTextAndClose()

# Help HTML dialog class.
class HelpHTMLDialog(wx.Dialog):

  # Paths to Markdown pages directory and files
  MARKDOWN_PATH = 'md/'
  HELP_PAGE_PATH = MARKDOWN_PATH + 'help.md'

  # Initializes the object by creating the CEF  web browser and binding the event handlers.
  def __init__(self, title, parent = None):
    super(HelpHTMLDialog, self).__init__(parent = parent, title = title)
    
    self.SetSize((1000, 800))
    self.addBrowser()
    
    self.Centre()
    self.ShowModal()
    
  # Adds the CEF web browser to this dialog and binds the dialog close event.
  def addBrowser(self):
    self.panel = wx.Panel(self)
    self.Bind(wx.EVT_CLOSE, self.onClose)
    
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    windowInfo = cef.WindowInfo()
    (width, height) = self.panel.GetClientSize().Get()
    windowInfo.SetAsChild(self.panel.GetHandle(), [0, 0, 1000, 800])
    self.browser = cef.CreateBrowserSync(windowInfo, url = 'about:blank')
    html = self.loadHTML()
    self.browser.LoadUrl('data:text/html,' + html)
    
    self.timerId = 1
    self.timer = wx.Timer(self, self.timerId)
    self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
    self.timer.Start(10)
    
  # Closes all CEF processes on dialog close.
  def onClose(self, event):
    self.timer.Stop()
    self.browser = None
    event.Skip()
    
  # Runs the  CEF  message loop iteration.
  def onTimer(self, event):
    cef.MessageLoopWork()

  # Loads the page in Markdown, converts it into HTML and returns it.
  def loadHTML(self):
    path = HelpHTMLDialog.HELP_PAGE_PATH
    content = ''
    with open(path, encoding='utf-8') as file:
      # Load file line by line
      while True:
        line = file.readline()
        content += line
        if not line:
          break
    
    # Convert the page from Markkdown to HTML
    md = markdown2.Markdown()
    html = md.convert(content)
    
    # Wrap the page content with the basic HTML structure and add the scrip which focuses the first element
    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
</head>
<body>
''' + html + '''
</body>
</html>
'''
    return html
