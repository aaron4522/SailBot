# SailBot
Main codebase for SailBot 2019-21

## What each of the scripts do and important notes

### GPS (also contains compass)
1. contains functiond for converting between distance units
2. contains gps class, which has attributes latitude and longitude
3. contains compass class

### OdriveTest
1. contains odrive object and initialization values
2. setting odrive.pos will change motor position

### transciver
1. contains arduino class which:
2. sends messages to other transciver
3. reads messages sent from other transciver

### windvane
1. contains windvane class with property angle

### drivers
1. Has sail and rudder objects which have properties angle, used for setting angle of sail and rudders
2. Has code for stepper motors and servos

### boatMain
1. will eventually call all the automation code

### constants
1. holds all of the constants used by other scripts
2. note: the constants are store in config.ini file, constants.py just loads and returns 

#### other scripts not mentioned are not used
