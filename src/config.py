import json

# Class for loading and saving application configuration.
class Config:
  CONFIG_PATH = 'config.json'
  
  # Initializes the object by loading the configuration from the config file.
  def __init__(self):
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
