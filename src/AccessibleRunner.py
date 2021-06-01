# TODO
# * Resize the command output textbox together with the window.

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

  # Maximum number of items in the commands history.
  COMMANDS_HISTORY_LIMIT = 10

  # Maximum number of items in the working directories history.
  DIRECTORIES_HISTORY_LIMIT = 10
  
  # Maximum number of items in the find texts history
  FIND_TEXTS_HISTORY_LIMIT = 10
  
  # Maximum number of items in the line substitution regular expression history
  SUBSTITUTION_REGEXES_HISTORY_LIMIT = 10
  
  # Maximum number of items in the line substitution replacement history
  SUBSTITUTION_REPLACEMENTS_HISTORY_LIMIT = 10
  
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
  def runProcess(self, command, directory, useShell):
    if self.process is not None:
      return
    
    # Add the command and directory to the history and ensure that blank or whitespace working directory value means the current working directory should be used
    self.addToCommandsHistory(command)
    if directory.strip() == '':
      directory = None
    self.addToDirectoriesHistory(directory)
    
    # On Windows, set the proper code page for console
    # See https://stackoverflow.com/questions/67524114/python-how-to-decode-file-names-retrieved-from-dir-command-using-subprocess
    if ON_WINDOWS:
      call(['chcp', '65001'], shell = True)
      
      # Try running the command
    try:
      self.process = Popen(command, cwd = directory, shell = useShell, stdout = PIPE, stderr = STDOUT, stdin = PIPE)
    except (NotADirectoryError, FileNotFoundError):
      errorMessage = 'Error: The working directory \'{}\' does not exist.\n'.format(directory)
      self.ui.setOutput(errorMessage, True)
      self.srOutput(errorMessage)
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

  # Adds the given item to the  given history record with the given limit and returns the new items list.
  def addToHistory(self, item, record, limit):
    if (item.strip() == '') or item is None:
      return
    items = self.config.history[record]
    
    # If the item already exists in the history, remove it
    try:  
      index = items.index(item)
      items.pop(index)
    except:
      pass
      
    # Add the item to the begining of the history
    items.insert(0, item)
    
    # Remove the items which exceed the history limit
    items = items[:limit]
    
    return items
    
  # Adds the given command to the  history.
  def addToCommandsHistory(self, command):
    commands = self.addToHistory(command, 'commands', AccessibleRunner.COMMANDS_HISTORY_LIMIT)
    
    # Set the new command choices
    self.ui.setCommandChoices(commands)

  # Adds the given directory to the  history.
  def addToDirectoriesHistory(self, directory):
    if directory is None:
      return
    directories = self.addToHistory(os.path.normpath(directory), 'directories', AccessibleRunner.DIRECTORIES_HISTORY_LIMIT)
    
    # Set the new directory choices
    self.ui.setDirectoryChoices(directories)
    
  # Adds the given find text to the  history.
  def addToFindTextsHistory(self, findText):
    self.addToHistory(findText, 'findTexts', AccessibleRunner.FIND_TEXTS_HISTORY_LIMIT)

  # Adds the given line substitution regular expression to the  history.
  def addToSubstitutionRegexesHistory(self, regex):
    self.addToHistory(regex, 'substitutionRegexes', AccessibleRunner.SUBSTITUTION_REGEXES_HISTORY_LIMIT)
    
  # Merges the given settings with the config settings dictionary.
  def mergeSettings(self, settings):
    self.config.settings.update(settings)
    
  # Adds the given line substitution replacement to the  history.
  def addToSubstitutionReplacementsHistory(self, replacement):
    self.addToHistory(replacement, 'substitutionReplacements', AccessibleRunner.SUBSTITUTION_REPLACEMENTS_HISTORY_LIMIT)

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
      
      # Apply the regex based line substitution if enabled
      if settings['lineSubstitution']:
        lineString = re.sub(settings['substitutionRegex'], settings['substitutionReplacement'], lineString)
      
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
