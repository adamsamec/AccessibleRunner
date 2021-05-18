# TODO
# * Play a notification sound whenever the new output matches a given regular expression. This way the user could be notified about error or successful compilation.
# * Add a command and working directory history which will be loaded from external file and could be selected ideally using combobox.
# * Add menubar for macOS. After that, let Cmd + W close only the Window and Cmd + Q close the app.

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
    self.closeWindow()
    
  def charHook(self, event):
    key = event.GetKeyCode()
    controlDown = event.ControlDown() # On Windows and Linux this will be the Control key, on macOS this will be the Cmd key
    shiftDown = event.ShiftDown()
    
    if (key == ord('Q')) and controlDown: # Control/Cmd + Q
      self.closeWindow()
    if (key == ord('C')) and controlDown and shiftDown: # Control/Cmd + Shift + C
      self.copyOutput()
    elif (key == ord('D')) and controlDown and shiftDown: # Control/Cmd + Shift + D
      self.clearOutput()
    else:
      event.Skip()

  def addWidgets(self):
    self.panel = wx.Panel(self)    
    vbox = wx.BoxSizer(wx.VERTICAL)
    
    # Command textbox
    commandHbox = wx.BoxSizer(wx.HORIZONTAL)
    self.commandLabel = wx.StaticText(self.panel, -1, 'Command') 
    commandHbox.Add(self.commandLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.commandTextbox = wx.TextCtrl(self.panel)
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
    self.outputLabel = wx.StaticText(self.panel, -1, "Output")
    outputHbox.Add(self.outputLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    self.outputTextbox = wx.TextCtrl(self.panel, size = (400, 150), style = wx.TE_MULTILINE | wx.TE_READONLY)
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
    
  def onRunButtonClick(self, event):
    if self.process is not None:
      return
    self.runButton.Disable()
    self.killButton.Enable()
    
    command = self.commandTextbox.GetValue()
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
      self.process = Popen(command, shell = useShell, stdout = PIPE, stderr = STDOUT, stdin = PIPE, cwd = dir)
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
    
  def closeWindow(self):
    if self.process:
      self.killProcessTree()
    self.Destroy()

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
