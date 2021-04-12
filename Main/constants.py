
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
    
def save():
    with open('../config.ini', 'w') as configfile:
        config.write(configfile) 

if __name__ == '__main__':
<<<<<<< HEAD
    #print(config['CONSTANTS']['motorKV'])
    print(config.sections())
    save()
    print(config.sections())
=======
    print(config.sections())
    print(config['CONSTANTS']['win_title'])
>>>>>>> 3db36562af7c80ae34beffeaa526e522005367b5
