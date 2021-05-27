import os
import json
from shutil import copyfile

# Class for loading and saving application configuration.
class Config:

  # Configuration file version.
  VERSION = '1.0'
  
  # Paths to the original and actually used config files.
  ORIG_CONFIG_PATH = 'config.orig.json'
  CONFIG_PATH = os.environ['APPDATA'] + '\\AccessibleRunner\\config.json'
  
  # Initializes the object by loading the configuration from the config file. The used config file is copied from the original to a writable standard application directory if not already exists there, or if is corrupted or older version.
  def __init__(self):
    isConfigValid = False
    if os.path.exists(Config.CONFIG_PATH):
      # The config file already exists, verify if it is a valid JSON file and has the correct version
      path = Config.CONFIG_PATH
      try:
        file = open(path, encoding='utf-8')
        content = ''
        
        # Load the file line by line
        while True:
          line = file.readline()
          content += line
          if not line:
            break
      
        # Parse the configuration file and verify its version
        config = json.loads(content)
        if config['version'] == Config.VERSION:
          isConfigValid = True
      except:
        pass

    if not isConfigValid:
      # The config file does not already exist or is not valid, so copy the original config file to a  writable standard application  directory 
      dir = os.path.dirname(Config.CONFIG_PATH)
      if not os.path.isdir(dir):
        os.makedirs(dir)
      copyfile(os.path.abspath(Config.ORIG_CONFIG_PATH), Config.CONFIG_PATH)
    
      # Open and load the copied configuration file line by line
      path = Config.CONFIG_PATH
      with open(path, encoding='utf-8') as file:
        content = ''
        while True:
          line = file.readline()
          content += line
          if not line:
            break

      # Parse the configuration file
      config = json.loads(content)
      
    # Save the parsed config as a dictionary
    self.history = config['history']
    self.settings = config['settings']
    
  # Saves the current configuration to the config file.
  def saveToFile(self):
    path = Config.CONFIG_PATH
    with open(path, 'w', encoding='utf-8') as file:
      config = {
        'version': Config.VERSION,
        'history': self.history,
        'settings': self.settings,
      }
      json.dump(config, file, indent = 2)
