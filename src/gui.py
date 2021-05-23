import os
import wx

# Main frame class.
class MainFrame(wx.Frame):

  # Initializes the object by linking it with the given AccessibilityRunner and Config objects, binds the event handlers, and creates the whole GUI.
  def __init__(self, runner, config, title, parent = None):
    super(MainFrame, self).__init__(parent, title = title)
    self.runner = runner
    self.config = config
    
    self.Bind(wx.EVT_CLOSE, self.onWindowClose)
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
    
    # Command combobox
    commandHbox = wx.BoxSizer(wx.HORIZONTAL)
    commandLabel = wx.StaticText(self.panel, -1, 'Command') 
    commandHbox.Add(commandLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.commandCombobox = wx.ComboBox(self.panel, choices = history['commands'])
    commandHbox.Add(self.commandCombobox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Working directory combobox
    dirHbox = wx.BoxSizer(wx.HORIZONTAL)
    dirLabel = wx.StaticText(self.panel, -1, 'Working directory')
    dirHbox.Add(dirLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.dirCombobox = wx.ComboBox(self.panel, choices = history['dirs'])
    dirHbox.Add(self.dirCombobox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Working directory choose button
    self.chooseDirButton = wx.Button(self.panel, label = 'Chooce directory')
    self.chooseDirButton.Bind(wx.EVT_BUTTON, self.onChooseDirButtonClick)
    dirHbox.Add(self.chooseDirButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Use shell checkbox
    useShellHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.useShellCheckbox = wx.CheckBox(self.panel, label = 'Execute using shell', pos = (10, 10))
    self.useShellCheckbox.SetValue(True)
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
    
    clearCopySettingsHbox = wx.BoxSizer(wx.HORIZONTAL)
    
    # Clear button
    self.clearButton = wx.Button(self.panel, label = 'Clear output')
    self.clearButton.Bind(wx.EVT_BUTTON, self.onClearButtonClick)
    clearCopySettingsHbox.Add(self.clearButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Copy button
    self.copyButton = wx.Button(self.panel, label = 'Copy output')
    self.copyButton.Bind(wx.EVT_BUTTON, self.onCopyButtonClick)
    clearCopySettingsHbox.Add(self.copyButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
        # Settings button
    self.settingsButton = wx.Button(self.panel, label = 'Settings')
    self.settingsButton.Bind(wx.EVT_BUTTON, self.onSettingsButtonClick)
    clearCopySettingsHbox.Add(self.settingsButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    vbox.Add(commandHbox)
    vbox.Add(dirHbox)
    vbox.Add(useShellHbox)
    vbox.Add(runAndKillHbox)
    vbox.Add(outputHbox)
    vbox.Add(clearCopySettingsHbox)

    self.panel.SetSizer(vbox)
    
  # Sets the GUI state as running.
  def setAsRunning(self):
    self.runButton.Disable()
    self.killButton.Enable()

  # Sets the GUI state as not running.
  def setAsNotRunning(self):
    self.killButton.Disable()
    self.runButton.Enable()

  # Cleans everything and closes the main window.
  def cleanAndClose(self):
    self.runner.clean()
    self.Destroy()
    
  # Runs the process using the values of the relevant textboxes.
  def runProcess(self):
    command = self.commandCombobox.GetValue()
    dir = self.dirCombobox.GetValue()
    useShell = self.useShellCheckbox.GetValue()
    self.runner.runProcess(command, dir, useShell)
    
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
  def setDirChoices(self, choices):
    self.setChoices(self.dirCombobox, choices)

  # Sets or appends the given text to the command output textbox.
  def setOutput(self, text, append = False):
    if append:
      self.outputTextbox.SetValue(self.outputTextbox.GetValue() + text)
    else:
      self.outputTextbox.SetValue(text)

  # Gets the text of the command output textbox.
  def getOutput(self):
    return self.outputTextbox.GetValue()
    
  # Handles  the window close event.
  def onWindowClose(self, event):
    self.cleanAndClose()
    
  # Handles  the key press events no matter where the focus is.
  def charHook(self, event):
    key = event.GetKeyCode()
    modifiers = event.GetModifiers()
    
    # Check if only Control or Control + Shift are pressed
    # On macOS the control key is actually the Cmd key
    onlyControlDown = modifiers == wx.MOD_CONTROL
    onlyControlAndShiftDown = modifiers == (wx.MOD_CONTROL | wx.MOD_SHIFT)
    
    # Control + Enter
    if (key == wx.WXK_RETURN) and onlyControlDown:
      self.outputTextbox.SetFocus()
      self.runProcess()
      
    # Control + K
    elif (key == ord('K')) and onlyControlDown:
      self.commandCombobox.SetFocus()
      self.runner.killProcessTree()

    # Control + L
    elif (key == ord('L')) and onlyControlDown:
      self.commandCombobox.SetFocus()


    # Control/Cmd + Q
    elif (key == ord('Q')) and onlyControlDown:
      self.cleanAndClose()
      
    # Control/Cmd + Shift + C
    elif (key == ord('C')) and onlyControlAndShiftDown:
      self.runner.copyOutput()
      
    # Control/Cmd + D
    elif (key == ord('D')) and onlyControlDown:
      self.runner.clearOutput()
    
    else:
      event.Skip()
    
  # Handles  the key down event if the focus is on the command textbox.
  def charHookAtCommand(self, event):
    key = event.GetKeyCode()
    hasAnyModifiers = event.HasAnyModifiers()
    print(    'test')
    print(hasAnyModifiers)
    print(key)
    
  # Handles the choose directory button click.
  def onChooseDirButtonClick(self, event):
    # Determine the default path from the working directory combobox
    path = self.dirCombobox.GetValue()
    path = path if os.path.isdir(path) else ''
    
    # Create and show the directory chooser dialog
    dialog = wx.DirDialog(self, message = 'Choose a working directory', defaultPath = path)
    if dialog.ShowModal() == wx.ID_OK:
      path = dialog.GetPath()
      self.dirCombobox.SetValue(path)
    dialog.Destroy()
    
  # Handles the run button click.
  def onRunButtonClick(self, event):
    self.runProcess()
    
  # Handles the kill process button click.
  def onKillButtonClick(self, event):
    self.runner.killProcessTree()
    
  # Handles the settings button click.
  def onSettingsButtonClick(self, event):
    self.settingsDialog = SettingsDialog(self.runner, self.config, title = 'Settings | AccessibleRunner', parent = self)

  # Handles the clear button click.
  def onClearButtonClick(self, event):
    self.runner.clearOutput()
    
  # Handles the copy button click.
  def onCopyButtonClick(self, event):
    self.runner.copyOutput()

# Settings dialog class.
class SettingsDialog(wx.Dialog):

  # Initializes the object by linking it with the given AccessibilityRunner and Config objects, binds the event handlers, and creates the whole GUI.
  def __init__(self, runner, config, title, parent = None):
    super(SettingsDialog, self).__init__(parent = parent, title = title)
    self.runner = runner
    self.config = config
    
    self.addWidgets()
    self.Centre()
    self.ShowModal()
    self.Fit()

  # Adds all the initial widgets to this frame.
  def addWidgets(self):
    self.panel = wx.Panel(self)    
    vbox = wx.BoxSizer(wx.VERTICAL)
    settings = self.config.settings
    
    # Play success sound checkbox
    playSuccessHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.playSuccessCheckbox = wx.CheckBox(self.panel, label = 'Play success sound when regular expression matches', pos = (10, 10))
    self.playSuccessCheckbox.SetValue(settings['playSuccessSound'])
    playSuccessHbox.Add(self.playSuccessCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Success regex textbox
    successRegexHbox = wx.BoxSizer(wx.HORIZONTAL)
    successRegexLabel = wx.StaticText(self.panel, -1, 'Success regular expression') 
    successRegexHbox.Add(successRegexLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.successRegexTextbox = wx.TextCtrl(self.panel, value = settings['successRegex'])
    successRegexHbox.Add(self.successRegexTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Play error sound checkbox
    playErrorHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.playErrorCheckbox = wx.CheckBox(self.panel, label = 'Play error sound when regular expression matches', pos = (10, 10))
    self.playErrorCheckbox.SetValue(settings['playErrorSound'])
    playErrorHbox.Add(self.playErrorCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Error regex textbox
    errorRegexHbox = wx.BoxSizer(wx.HORIZONTAL)
    errorRegexLabel = wx.StaticText(self.panel, -1, 'Error regular expression') 
    errorRegexHbox.Add(errorRegexLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.errorRegexTextbox = wx.TextCtrl(self.panel, value = settings['errorRegex'])
    errorRegexHbox.Add(self.errorRegexTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    cancelAndCloseHbox = wx.BoxSizer(wx.HORIZONTAL)
    
    # Cancel button
    self.cancelButton = wx.Button(self.panel, label = 'Cancel')
    self.cancelButton.Bind(wx.EVT_BUTTON, self.onCancelButtonClick)
    cancelAndCloseHbox.Add(self.cancelButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    # Save and close button
    self.closeButton = wx.Button(self.panel, label = 'Save and close')
    self.closeButton.Bind(wx.EVT_BUTTON, self.onCloseButtonClick)
    cancelAndCloseHbox.Add(self.closeButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    vbox.Add(playSuccessHbox)
    vbox.Add(successRegexHbox)
    vbox.Add(playErrorHbox)
    vbox.Add(errorRegexHbox)
    vbox.Add(cancelAndCloseHbox)
    self.panel.SetSizer(vbox)
    
  # Handles the cancel button click.
  def onCancelButtonClick(self, event):
    self.Destroy()

  # Handles the save and close button click.
  def onCloseButtonClick(self, event):
    settings = {
      'playSuccessSound': self.playSuccessCheckbox.GetValue(),
      'successRegex': self.successRegexTextbox.GetValue(),
      'playErrorSound': self.playErrorCheckbox.GetValue(),
      'errorRegex': self.errorRegexTextbox.GetValue(),
    }
    self.runner.setSettings(settings)
    self.Destroy()
