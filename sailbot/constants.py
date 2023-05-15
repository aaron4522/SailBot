# reads values from config.ini and returns them
import configparser
import os

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
config_path = fr"{root_dir}\sailbot\config.ini"

if not os.path.isfile(config_path):
    raise Exception(F"cannot find config.ini file in {config_path}")

config = configparser.ConfigParser()
config.read(config_path)


def save():
    with open(config_path, 'w') as configfile:
        config.write(configfile) 


if __name__ == '__main__':
    print(config.sections())
    print(config['CONSTANTS']['win_title'])
