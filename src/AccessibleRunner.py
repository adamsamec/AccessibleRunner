# TODO
# * Is it possible to send narration message to screen reader?
# * Add Find text in output textbox feature.

import os
import sys
import wx
import re
import psutil
from subprocess import call, Popen, PIPE, STDOUT
from threading import Thread
from playsound import playsound

from config import Config
from gui import MainFrame

ON_WINDOWS = os.name == 'nt'

# Main application class.
class AccessibleRunner:

  # Maximum number of items in command history.
  COMMAND_HISTORY_LIMIT = 10

  # Maximum number of items in working directory history.
  DIR_HISTORY_LIMIT = 10
  
  # Paths to sounds directory and files
  SOUNDS_PATH = 'sounds/'
  SUCCESS_SOUND_PATH = SOUNDS_PATH + 'success.mp3'
  ERROR_SOUND_PATH = SOUNDS_PATH + 'error.mp3'

  # Initializes the object.
  def __init__(self, config):
    self.config = config
    self.process = None
    
  # Sets the UI object for this runner.
  def setUI(self, ui):
    self.ui = ui
    
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
      self.ui.setOutput('Error: The working directory \'{}\' does not exist.\n'.format(dir), True)
      self.ui.setAsNotRunning()
    else:
    
      # Start fetching the process output in a new thread
      thread = Thread(target=self.fetchOutput, args = (self.process.stdout, None))
      thread.daemon = True # Thread dies with the program
      thread.start()
    self.ui.setAsRunning()
    
  # Cleans everything on exit, including saving the changes to the config file.
  def clean(self):
    self.killProcessTree()
    self.config.saveToFile()

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
    self.ui.setCommandChoices(commands)

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
    self.ui.setDirChoices(dirs)
    
  # Sets the given settings to the config object.
  def setSettings(self, settings):
    self.config.settings = settings
    
  # Clears the command output.
  def clearOutput(self):
    self.ui.setOutput('')
        
  # Copies the command output string to the system clipboard.
  def copyOutput(self):
    if not wx.TheClipboard.IsOpened():
      wx.TheClipboard.Open()
      data = wx.TextDataObject()
      data.SetText(self.ui.getOutput())
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
    self.ui.setAsNotRunning()
      
  # Waits for the process output and continuously writes it to the command output. Depending on the current settings, plays success and error sounds if regular expression matches output line.
  def fetchOutput(self, out, arg):
    settings = self.config.settings
    
    for line in iter(out.readline, b''):
      lineString = line.decode()
      
      # Play sound if success regex matches
      if settings['playSuccessSound']:
        match = re.search(settings['successRegex'], lineString)
        if match is not None:
          playsound(AccessibleRunner.SUCCESS_SOUND_PATH)
        
      # Play sound if error regex matches
      if settings['playErrorSound']:
        match = re.search(settings['errorRegex'], lineString)
        if match is not None:
          playsound(AccessibleRunner.ERROR_SOUND_PATH)
        
      # Append the line to the UI output
      self.ui.setOutput(lineString, True)

    out.close()
    self.process = None
    self.ui.setAsNotRunning()
    
# Main function.
def main():
  app = wx.App()
  config = Config()
  runner = AccessibleRunner(config)
  mainFrame = MainFrame(runner, config, title='AccessibleRunner')
  runner.setUI(mainFrame)
  app.MainLoop()

main()
