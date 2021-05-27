# TODO
# * Test if wrapping and not found should interrupt the speach.

import os
import sys
import wx
import re
import psutil
import accessible_output2.outputs.auto
from subprocess import call, Popen, PIPE, STDOUT
from threading import Thread
from playsound import playsound

from config import Config
from gui import MainFrame

ON_WINDOWS = os.name == 'nt'

# Main application class.
class AccessibleRunner:

  # Maximum number of items in commands history.
  COMMAND_HISTORY_LIMIT = 10

  # Maximum number of items in working directories history.
  DIR_HISTORY_LIMIT = 10
  
  # Maximum number of items in find texts history
  FIND_TEXTS_HISTORY_LIMIT = 10
  
  # Paths to sounds directory and files
  SOUNDS_PATH = 'sounds/'
  SUCCESS_SOUND_PATH = SOUNDS_PATH + 'success.mp3'
  ERROR_SOUND_PATH = SOUNDS_PATH + 'error.mp3'
  NOT_FOUND_SOUND_PATH = SOUNDS_PATH + 'Windows Background.wav'

  # Initializes the object.
  def __init__(self, config):
    self.config = config
    self.active = True
    self.process = None
    self.sr = accessible_output2.outputs.auto.Auto()
    
  # Sets the UI object for this runner.
  def setUI(self, ui):
    self.ui = ui
    
  # Sets the active state of the application to the given value.
  def setActive(self, active):
    self.active = active
    
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
      thread = Thread(target = self.fetchOutput, args = (self.process.stdout, None))
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
    
  # Adds the given find text to the  history.
  def addToFindHistory(self, findText):
    findTexts = self.config.history['findTexts']
    
    # If the find text already exists in the history, remove it
    try:  
      index = findTexts.index(findText)
      findTexts.pop(index)
    except:
      pass
      
    # Add the find text to the begining of the history
    findTexts.insert(0, findText)
    
    # Remove the find texts which exceed the history limit
    findTexts = findTexts[:AccessibleRunner.FIND_TEXTS_HISTORY_LIMIT]

  # Merges the given settings with the config settings dictionary.
  def mergeSettings(self, settings):
    self.config.settings.update(settings)
    
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
    
  # Plays the sound at the given path asynchronously.
  def play(self, path):
    thread = Thread(target = playsound, args = (path, None))
    thread.daemon = True # Thread dies with the program
    thread.start()
  
  # Plays the success sound.
  def playSuccess(self):
    self.play(AccessibleRunner.SUCCESS_SOUND_PATH)
    
  # Plays the error sound.
  def playError(self):
    self.play(AccessibleRunner.ERROR_SOUND_PATH)

  # Plays the not found sound.
  def playNotFound(self):
    self.play(AccessibleRunner.NOT_FOUND_SOUND_PATH)
    
  # Outputs the given text via screen reader, optionally interrupting the current output.
  def srOutput(self, text, interrupt = False):
    # Output only if screen reader is running
    if not self.sr.is_system_output():
      self.sr.output(text, interrupt = interrupt)
      
  # Waits for the process output and continuously writes it to the command output. Depending on the current settings, plays success and error sounds if regular expression matches output line.
  def fetchOutput(self, out, arg):
    settings = self.config.settings
    
    for line in iter(out.readline, b''):
      lineString = line.decode()
      
      # Output the line via screen reader if the main frame is active or if background output is turned on
      if self.active or self.config.settings['srBgOutput']:
        self.srOutput(lineString)
      
      # Play sound if success regex matches
      if settings['playSuccessSound']:
        match = re.search(settings['successRegex'], lineString)
        if match is not None:
          self.playSuccess()
        
      # Play sound if error regex matches
      if settings['playErrorSound']:
        match = re.search(settings['errorRegex'], lineString)
        if match is not None:
          self.playError()
        
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
  mainFrame = MainFrame(runner, config, title = MainFrame.WINDOW_TITLE)
  runner.setUI(mainFrame)
  app.MainLoop()

main()
