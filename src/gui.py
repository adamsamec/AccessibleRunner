import wx

# GUI class.
class GUI(wx.Frame):

  # Initializes the object by linking it with the given AccessibilityRunner object, binds the event handlers, and creates the whole GUI.
  def __init__(self, parent, runner, title):
    super(GUI, self).__init__(parent, title = title)
    self.runner = runner
    
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
    
    # Command textbox
    commandHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.commandLabel = wx.StaticText(self.panel, -1, 'Command') 
    commandHbox.Add(self.commandLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.commandTextbox = wx.TextCtrl(self.panel)
    #self.commandTextbox.Bind(wx.EVT_CHAR_HOOK, self.charHookAtCommand)
    commandHbox.Add(self.commandTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Working directory textbox
    dirHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.dirLabel = wx.StaticText(self.panel, -1, 'Working directory')
    dirHbox.Add(self.dirLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.dirTextbox = wx.TextCtrl(self.panel)
    dirHbox.Add(self.dirTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Use shell checkbox
    useShellHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.useShellCheckbox = wx.CheckBox(self.panel, label = 'Execute using shell',pos = (10, 10))
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
    self.outputLabel = wx.StaticText(self.panel, -1, 'Output')
    outputHbox.Add(self.outputLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.outputTextbox = wx.TextCtrl(self.panel, size = (600, 150), style = wx.TE_MULTILINE | wx.TE_READONLY)
    outputHbox.Add(self.outputTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    clearAndCopyHbox = wx.BoxSizer(wx.HORIZONTAL)
    
    # Clear button
    self.clearButton = wx.Button(self.panel, label = 'Clear output')
    self.clearButton.Bind(wx.EVT_BUTTON, self.onClearButtonClick)
    clearAndCopyHbox.Add(self.clearButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Copy button
    self.copyButton = wx.Button(self.panel, label = 'Copy output')
    self.copyButton.Bind(wx.EVT_BUTTON, self.onCopyButtonClick)
    clearAndCopyHbox.Add(self.copyButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    vbox.Add(commandHbox)
    vbox.Add(dirHbox)
    vbox.Add(useShellHbox)
    vbox.Add(runAndKillHbox)
    vbox.Add(outputHbox)
    vbox.Add(clearAndCopyHbox)

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
    command = self.commandTextbox.GetValue()
    directory = self.dirTextbox.GetValue()
    if directory == '':
      directory = None
    useShell = self.useShellCheckbox.GetValue()
    self.runner.runProcess(command, directory, useShell)

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
      self.commandTextbox.SetFocus()
      self.runner.killProcessTree()

    # Control + L
    elif (key == ord('L')) and onlyControlDown:
      self.commandTextbox.SetFocus()


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
  