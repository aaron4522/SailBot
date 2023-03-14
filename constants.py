# reads values from config.ini and returns them
import configparser
import os

if os.path.isfile('config.ini'):
    prefix = ''
elif os.path.isfile('config.ini'):
    prefix = 'sailbot/'
else:
    raise Exception("cannot find config.ini file")

config = configparser.ConfigParser()
config.read(F'{prefix}config.ini')
    
def save():
    with open('../config.ini', 'w') as configfile:
        config.write(configfile) 

if __name__ == '__main__':

    print(config.sections())
    print(config['CONSTANTS']['win_title'])
