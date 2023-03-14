# reads values from config.ini and returns them
import configparser

try:
    import boatMath # see if we are in sailbot folder or parent folder
    prefix = ''
except:
    prefix = 'sailbot/'
config = configparser.ConfigParser()
config.read(F'{prefix}config.ini')
    
def save():
    with open('../config.ini', 'w') as configfile:
        config.write(configfile) 

if __name__ == '__main__':

    print(config.sections())
    print(config['CONSTANTS']['win_title'])
