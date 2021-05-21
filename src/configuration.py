import json

class Configuration:
  CONFIG_PATH = 'config.json'
  
  def __init__(self):
    # Load the configuration file line by line
    path = Configuration.CONFIG_PATH
    file = open(path, encoding='utf-8')
    content = ''
    while True:
      line = file.readline()
      content += line
      if not line:
        break
    file.close()

    # Parse the configuration file and save it as a dictionary
    self.config = json.loads(content)

