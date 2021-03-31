
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
    
def save():
    with open('../config.ini', 'w') as configfile:
        config.write(configfile) 

if __name__ == '__main__':
<<<<<<< HEAD
    print(config.sections())
    print(config['CONSTANTS']['win_title'])
=======
    #print(config['CONSTANTS']['motorKV'])
    print(config.sections())
    save()
    print(config.sections())
>>>>>>> 9861c9c9c0c1d23f7eb224b6c89ac19d1a7068fd
