
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
    
def save():
    with open('config.ini', 'w') as configfile:
        config.write(configfile) 


