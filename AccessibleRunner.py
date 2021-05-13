# TODO
# * Create keyboard shortcuts.

import sys
import wx
import os
import signal
import psutil
from subprocess import Popen, PIPE, STDOUT
from threading  import Thread

class AccessibleRunner(wx.Frame):
  def __init__(self, parent, title):
    super(AccessibleRunner, self).__init__(parent, title = title)
    self.process = None
    
    self.Bind(wx.EVT_CLOSE, self.onWindowClose)
    
    self.addWidgets()
    self.Centre()
    self.Show()
    self.Fit()
    
  def onWindowClose(self, event):
    if self.process:
      self.killProcessTree()
    self.Destroy()

  def addWidgets(self):
    self.panel = wx.Panel(self)    
    vbox = wx.BoxSizer(wx.VERTICAL)
    
    # Command textbox
    hbox1 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.commandLabel = wx.StaticText(self.panel, -1, 'Command') 
    hbox1.Add(self.commandLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.commandTextbox = wx.TextCtrl(self.panel)
    hbox1.Add(self.commandTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Arguments textbox
    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.argsLabel = wx.StaticText(self.panel, -1, 'Arguments') 
    hbox2.Add(self.argsLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.argsTextbox = wx.TextCtrl(self.panel)
    hbox2.Add(self.argsTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Working directory textbox
    hbox3 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.dirLabel = wx.StaticText(self.panel, -1, 'Working directory') 
    hbox3.Add(self.dirLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.dirTextbox = wx.TextCtrl(self.panel)
    hbox3.Add(self.dirTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Run button
    hbox4 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.runButton = wx.Button(self.panel, label = 'Run')
    self.runButton.Bind(wx.EVT_BUTTON, self.onRunButtonClick)
    hbox4.Add(self.runButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.killButton = wx.Button(self.panel, label = 'Kill process')
    self.killButton.Disable()
    self.killButton.Bind(wx.EVT_BUTTON, self.onKillButtonClick)
    hbox4.Add(self.killButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)    
    
    # Output textbox
    hbox5 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.outputLabel = wx.StaticText(self.panel, -1, "Output") 
    hbox5.Add(self.outputLabel, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    self.outputTextbox = wx.TextCtrl(self.panel, size = (400, 150), style = wx.TE_MULTILINE | wx.TE_READONLY)
    hbox5.Add(self.outputTextbox, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Clear button
    hbox6 = wx.BoxSizer(wx.HORIZONTAL)
    
    self.clearButton = wx.Button(self.panel, label = 'Clear output')
    self.clearButton.Bind(wx.EVT_BUTTON, self.onClearButtonClick)
    hbox6.Add(self.clearButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    # Copy button
    self.copyButton = wx.Button(self.panel, label = 'Copy output')
    self.copyButton.Bind(wx.EVT_BUTTON, self.onCopyButtonClick)
    hbox6.Add(self.copyButton, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
    
    vbox.Add(hbox1)
    vbox.Add(hbox2)
    vbox.Add(hbox3)
    vbox.Add(hbox4)
    vbox.Add(hbox5)
    vbox.Add(hbox6)
      
    self.panel.SetSizer(vbox)
    
  def onRunButtonClick(self, event):
    if self.process is None:
      self.runButton.Disable()
      self.killButton.Enable()
      
      command = self.commandTextbox.GetValue()
      args = self.argsTextbox.GetValue()
      dir = self.dirTextbox.GetValue()
      if dir == '':
        dir = None
      
      try:
        self.process = Popen([command, args], shell = True, stdout = PIPE, stderr = STDOUT, cwd = dir)
      except NotADirectoryError:
        self.setOutput('Error: The directory does not exist.\n', True)
      else:        
        thread = Thread(target=self.fetchOutput, args = (self.process.stdout, None))
        thread.daemon = True # Thread dies with the program
        thread.start()
    
  def onKillButtonClick(self, event):
    if self.process:
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
    #os.kill(self.process.pid, signal.CTRL_C_EVENT) # This cannot be used, as it terminates the whole app
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
      self.setOutput(line.decode('windows-1250'), True)
    out.close()
    self.process = None
    
    self.runButton.Enable()
    self.killButton.Disable()
    
def main():
  app = wx.App()
  AccessibleRunner(None, title='AccessibleRunner')
  app.MainLoop()

main()
