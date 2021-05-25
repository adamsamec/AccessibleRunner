import os
import json
from shutil import copyfile

# Class for loading and saving application configuration.
class Config:

  # Paths to the original and actually used config files.
  ORIG_CONFIG_PATH = 'config.orig.json'
  CONFIG_PATH = os.environ['APPDATA'] + '\\AccessibleRunner\\config.json'
  
  # Initializes the object by loading the configuration from the config file. The used config file is copied to a writable standard application directory if not already exists there.
  def __init__(self):
    # If not already exists, copy the original config file to a  writable standard application  directory 
    if not os.path.exists(Config.CONFIG_PATH):
      dir = os.path.dirname(Config.CONFIG_PATH)
      if not os.path.isdir(dir):
        os.makedirs(dir)
      copyfile(os.path.abspath(Config.ORIG_CONFIG_PATH), Config.CONFIG_PATH)
    
    # Load the configuration file line by line
    path = Config.CONFIG_PATH
    with open(path, encoding='utf-8') as file:
      content = ''
      while True:
        line = file.readline()
        content += line
        if not line:
          break

    # Parse the configuration file and save it as a dictionary
    config = json.loads(content)
    self.history = config['history']
    self.settings = config['settings']
    
  # Saves the current configuration to the config file.
  def saveToFile(self):
    path = Config.CONFIG_PATH
    with open(path, 'w', encoding='utf-8') as file:
      config = {
        'history': self.history,
        'settings': self.settings,
      }
      json.dump(config, file, indent = 2)
