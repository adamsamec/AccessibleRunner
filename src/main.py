# TODO
# * Is it possible to send narration message to screen reader?
# * Add Enter key shortcut for running the command. After running, move the focus to the output textbox.
# * Ad shortcut for focusing the command textbox.
# * Play a notification sound whenever the new output matches a given regular expression. This way the user could be notified about error or successful compilation.
# * Add a command and working directory history which will be loaded from external file and could be selected ideally using combobox.
# * Add menubar for macOS. After that, let Cmd + W close only the Window and Cmd + Q close the app.

import os
import sys
import wx
import psutil
from subprocess import call, Popen, PIPE, STDOUT
from threading  import Thread

from configuration import Configuration
from gui import GUI

ON_WINDOWS = os.name == 'nt'

# Main application class.
class AccessibleRunner:

  # Initializes the object.
  def __init__(self):
    self.process = None
    
  # Sets the GUI object for this runner.
  def setGUI(self, gui):
    self.gui = gui
    
  # Runs the given command in a new process starting in  the  given working directory . The "useShell" parameter indicates if the command should be executed through the shell.
  def runProcess(self, command, directory, useShell):
    if self.process is not None:
      return
    
    # On Windows, set the proper code page for console
    # See https://stackoverflow.com/questions/67524114/python-how-to-decode-file-names-retrieved-from-dir-command-using-subprocess
    if ON_WINDOWS:
      call(['chcp', '65001'], shell = True)
      
      # Try running the command
    try:
      self.process = Popen(command, cwd = directory, shell = useShell, stdout = PIPE, stderr = STDOUT, stdin = PIPE)
    except (NotADirectoryError, FileNotFoundError):         
      self.gui.setOutput('Error: The working directory does not exist.\n', True)
      self.gui.setAsNotRunning()
    else:
    
      # Start fetching the process output in a new thread
      thread = Thread(target=self.fetchOutput, args = (self.process.stdout, None))
      thread.daemon = True # Thread dies with the program
      thread.start()
    self.gui.setAsRunning()
    
  # Cleans everything on exit.
  def clean(self):
    self.killProcessTree()

  # Clears the command output textbox.
  def clearOutput(self):
    self.gui.setOutput('')
        
  # Copies the command output textbox string to the system clipboard.
  def copyOutput(self):
    if not wx.TheClipboard.IsOpened():
      wx.TheClipboard.Open()
      data = wx.TextDataObject()
      data.SetText(self.gui.getOutput())
      wx.TheClipboard.SetData(data)
      wx.TheClipboard.Close()
    
      # Kills the currently running process and all its child processes.
  def killProcessTree(self):
    if not self.process:
      return
      
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
    self.gui.setAsNotRunning()
      
  # Waits for the process output and continuously writes it to the command output textbox.
  def fetchOutput(self, out, arg):
    for line in iter(out.readline, b''):
      self.gui.setOutput(line.decode(), True)
    out.close()
    self.process = None
    self.gui.setAsNotRunning()
    
# Main function.
def main():
  app = wx.App()
  runner = AccessibleRunner()
  g = GUI(None, runner, title='AccessibleRunner')
  runner.setGUI(g)
  app.MainLoop()

main()
