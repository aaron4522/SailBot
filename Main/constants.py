
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
    
def save():
    with open('../config.ini', 'w') as configfile:
        config.write(configfile) 

if __name__ == '__main__':
    print(config.sections())
    print(config['CONSTANTS']['win_title'])
