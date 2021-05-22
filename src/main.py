# TODO
# * Is it possible to send narration message to screen reader?
# * Play a notification sound whenever the new output matches a given regular expression. This way the user could be notified about error or successful compilation.
# * Add menubar for macOS. After that, let Cmd + W close only the Window and Cmd + Q close the app.

import os
import sys
import wx
import psutil
from subprocess import call, Popen, PIPE, STDOUT
from threading import Thread

from config import Config
from gui import GUI

ON_WINDOWS = os.name == 'nt'

# Main application class.
class AccessibleRunner:

  # Maximum number of items in command history.
  COMMAND_HISTORY_LIMIT = 10

  # Maximum number of items in working directory history.
  DIR_HISTORY_LIMIT = 10

  # Initializes the object.
  def __init__(self, config):
    self.config = config
    self.process = None
    
  # Sets the GUI object for this runner.
  def setGUI(self, gui):
    self.gui = gui
    
  # Runs the given command in a new process starting in  the  given working directory . The "useShell" parameter indicates if the command should be executed through the shell.
  def runProcess(self, command, dir, useShell):
    if self.process is not None:
      return
    
    # Sanitize the user input and ad to history if okay
    if command.strip() != '':
      self.addToCommandHistory(command)
    if dir.strip() == '':
      dir = None
    if dir is not None:
      self.addToDirHistory(dir)
    
    # On Windows, set the proper code page for console
    # See https://stackoverflow.com/questions/67524114/python-how-to-decode-file-names-retrieved-from-dir-command-using-subprocess
    if ON_WINDOWS:
      call(['chcp', '65001'], shell = True)
      
      # Try running the command
    try:
      self.process = Popen(command, cwd = dir, shell = useShell, stdout = PIPE, stderr = STDOUT, stdin = PIPE)
    except (NotADirectoryError, FileNotFoundError):         
      self.gui.setOutput('Error: The working directory \'{}\' does not exist.\n'.format(dir), True)
      self.gui.setAsNotRunning()
    else:
    
      # Start fetching the process output in a new thread
      thread = Thread(target=self.fetchOutput, args = (self.process.stdout, None))
      thread.daemon = True # Thread dies with the program
      thread.start()
    self.gui.setAsRunning()
    
  # Cleans everything on exit, including saving the changes to the config file.
  def clean(self):
    self.killProcessTree()
    self.config.save()

  # Adds the given command to the  history.
  def addToCommandHistory(self, command):
    commands = self.config.history['commands']
    
    # If the command already exists in the history, remove it
    try:  
      index = commands.index(command)
      commands.pop(index)
    except:
      pass
      
    # Add the command to the begining of the history
    commands.insert(0, command)
    
    # Remove the commands which exceed the history limit
    commands = commands[:AccessibleRunner.COMMAND_HISTORY_LIMIT]
    
    # Set the new command choices
    self.gui.setCommandChoices(commands)

  # Adds the given directory to the  history.
  def addToDirHistory(self, dir):
    dirs = self.config.history['dirs']
    
    # If the directory already exists in the history, remove it
    try:  
      normDirs = [os.path.normpath(item) for item in dirs]
      index = normDirs.index(os.path.normpath(dir))
      dirs.pop(index)
    except:
      pass
      
    # Add the normalized directory to the begining of the history
    dirs.insert(0, os.path.normpath(dir))
    
    # Remove the directories which exceed the history limit
    dirs = dirs[:AccessibleRunner.DIR_HISTORY_LIMIT]
    
    # Set the new directory choices
    self.gui.setDirChoices(dirs)
    
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
  config = Config()
  runner = AccessibleRunner(config)
  gui = GUI(None, runner, config, title='AccessibleRunner')
  runner.setGUI(gui)
  app.MainLoop()

main()
