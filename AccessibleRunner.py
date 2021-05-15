# TODO
# * Unable to close the window on macOS.

import os
import sys
import wx
import psutil
import shlex
from subprocess import call, Popen, PIPE, STDOUT
from threading  import Thread

ON_WINDOWS = os.name == 'nt'

class AccessibleRunner(wx.Frame):
  def __init__(self, parent, title):
    super(AccessibleRunner, self).__init__(parent, title = title)
    self.process = None
    
    self.Bind(wx.EVT_CLOSE, self.onWindowClose)
    self.Bind(wx.EVT_CHAR_HOOK, self.charHook)
    
    self.addWidgets()
    self.Centre()
    self.Show()
    self.Fit()
    
  def onWindowClose(self, event):
    if self.process:
      self.killProcessTree()
    self.Destroy()
    
  def charHook(self, event):
    key = event.GetKeyCode()
    controlDown = event.ControlDown() # On Windows and Linux this will be the Control key, on macOS this will be the Cmd key
    shiftDown = event.ShiftDown()
    
    if (key == 67) and controlDown and shiftDown: # Control + Shift + C
      self.copyOutput()
    elif (key == 68) and controlDown and shiftDown: # Control + Shift + D
      self.clearOutput()
    else:
      event.Skip()

  def addWidgets(self):
    self.panel = wx.Panel(self)    
    vbox = wx.BoxSizer(wx.VERTICAL)
    hbox1 = wx.BoxSizer(wx.HORIZONTAL)
    
    # Command textbox
    self.commandLabel = wx.StaticText(self.panel, -1, 'Command') 
    hbox1.Add(self.commandLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.commandTextbox = wx.TextCtrl(self.panel)
    hbox1.Add(self.commandTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    
    # Arguments textbox
    self.argsLabel = wx.StaticText(self.panel, -1, 'Arguments') 
    hbox2.Add(self.argsLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.argsTextbox = wx.TextCtrl(self.panel)
    hbox2.Add(self.argsTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    hbox3 = wx.BoxSizer(wx.HORIZONTAL)
    
    # Working directory textbox
    self.dirLabel = wx.StaticText(self.panel, -1, 'Working directory') 
    hbox3.Add(self.dirLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.dirTextbox = wx.TextCtrl(self.panel)
    hbox3.Add(self.dirTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    hbox4 = wx.BoxSizer(wx.HORIZONTAL)
    
    # Use shell checkbox
    self.useShellCheckbox = wx.CheckBox(self.panel, label = 'Execute using shell',pos = (10, 10))
    self.useShellCheckbox.SetValue(True)
    hbox4.Add(self.useShellCheckbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

    hbox5 = wx.BoxSizer(wx.HORIZONTAL)

    # Run button
    self.runButton = wx.Button(self.panel, label = 'Run')
    self.runButton.Bind(wx.EVT_BUTTON, self.onRunButtonClick)
    hbox5.Add(self.runButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Kill button
    self.killButton = wx.Button(self.panel, label = 'Kill process')
    self.killButton.Disable()
    self.killButton.Bind(wx.EVT_BUTTON, self.onKillButtonClick)
    hbox5.Add(self.killButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    hbox6 = wx.BoxSizer(wx.HORIZONTAL)
    
    # Output textbox
    self.outputLabel = wx.StaticText(self.panel, -1, "Output") 
    hbox6.Add(self.outputLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.outputTextbox = wx.TextCtrl(self.panel, size = (400, 150), style = wx.TE_MULTILINE | wx.TE_READONLY)
    hbox6.Add(self.outputTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    hbox7 = wx.BoxSizer(wx.HORIZONTAL)
    
    # Clear button
    self.clearButton = wx.Button(self.panel, label = 'Clear output')
    self.clearButton.Bind(wx.EVT_BUTTON, self.onClearButtonClick)
    hbox7.Add(self.clearButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Copy button
    self.copyButton = wx.Button(self.panel, label = 'Copy output')
    self.copyButton.Bind(wx.EVT_BUTTON, self.onCopyButtonClick)
    hbox7.Add(self.copyButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    vbox.Add(hbox1)
    vbox.Add(hbox2)
    vbox.Add(hbox3)
    vbox.Add(hbox4)
    vbox.Add(hbox5)
    vbox.Add(hbox6)
    vbox.Add(hbox7)

    self.panel.SetSizer(vbox)
    
  def onRunButtonClick(self, event):
    if self.process is not None:
      return
    self.runButton.Disable()
    self.killButton.Enable()
    
    command = self.commandTextbox.GetValue()
    args = self.argsTextbox.GetValue()
    #commandAndArgs = [command] + shlex.split(args) # This didn't work in macOS
    commandAndArgs = command + ' ' + args
    useShell = self.useShellCheckbox.GetValue()
    dir = self.dirTextbox.GetValue()
    if dir == '':
      dir = None
    
    # On Windows, set the proper code page for console
    # See https://stackoverflow.com/questions/67524114/python-how-to-decode-file-names-retrieved-from-dir-command-using-subprocess
    if ON_WINDOWS:
      call(['chcp', '65001'], shell = True)
      
      # Try running the command with the arguments
    try:
      self.process = Popen(commandAndArgs, shell = useShell, stdout = PIPE, stderr = STDOUT, cwd = dir)
    except (NotADirectoryError, FileNotFoundError):
      self.setOutput('Error: The working directory does not exist.\n', True)
    else:
      # Start fetching the process output in a new thread
      thread = Thread(target=self.fetchOutput, args = (self.process.stdout, None))
      thread.daemon = True # Thread dies with the program
      thread.start()
    
  def onKillButtonClick(self, event):
    if not self.process:
      return
    self.killProcessTree()
    
    self.runButton.Enable()
    self.killButton.Disable()
    
  def onClearButtonClick(self, event):
    self.clearOutput()
    
  def onCopyButtonClick(self, event):
    self.copyOutput()
      
  def clearOutput(self):
    self.setOutput('')
        
  def setOutput(self, text, append = False):
    prevText = self.outputTextbox.GetValue() if append else ''
    self.outputTextbox.SetValue(prevText + text)
    
  def copyOutput(self):
    if not wx.TheClipboard.IsOpened():
      wx.TheClipboard.Open()
      data = wx.TextDataObject()
      data.SetText(self.outputTextbox.GetValue())
      wx.TheClipboard.SetData(data)
      wx.TheClipboard.Close()
    
  def killProcessTree(self):
    parent = psutil.Process(self.process.pid)
    children = parent.children(recursive = True)
    for child in children:
        child.kill()
    psutil.wait_procs(children, timeout = 5)
    try:
      parent.kill()
      parent.wait(5)
    except:
      pass
    self.process = None
      
  def fetchOutput(self, out, arg):
    for line in iter(out.readline, b''):
      self.setOutput(line.decode(), True)
    out.close()
    self.process = None
    
    self.runButton.Enable()
    self.killButton.Disable()
    
def main():
  app = wx.App()
  AccessibleRunner(None, title='AccessibleRunner')
  app.MainLoop()

main()
