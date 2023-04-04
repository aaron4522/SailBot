# SailBot
Main codebase for SailBot 2019-21

## Guide
Onenote notebook containing boat startup steps, documentation and passwords can be found [here](https://pitt-my.sharepoint.com/:o:/r/personal/tad85_pitt_edu/Documents/Sailbot%20Stuff?d=w0d1afb3f4ab44df2b02186d8015ae380&csf=1&web=1&e=uvn9TV)

## Installation
In the terminal, navigate to the directory where you want to install the repository and enter
```
git clone https://github.com/SailBotPitt/SailBot.git
```

Install required dependencies by entering
```
pip install -r requirements.txt
```
*this requires python 3.10 to be installed*

## Scripts
### Logic
- **boatMain** - dain loop controlling every aspect of the boat
- **events** - directs boat behavior depending on which [competition challenges](https://www.sailbot.org/wp-content/uploads/2022/05/SailBot-2022-Events.pdf) the boat is participating in

### Sensors/Controls
Scripts which interface with the mechanical parts of the boat and provide abstracted functions used by 
- **GPS** - boat position
- **compass** - boat heading
- **windvane** - wind direction
- **camera** - RGB optical camera
- **drivers** - controls motors for rudder and sail
- **transceiver** - wireless communication to shore

### Utils
Miscellaneous functions used by the boat
- **constants** - config containing all static parameters used by the boat
- **boatMath** - common functions for converting between coordinates and angles
- **objectDetection** - AI buoy detection from an image
- **Odrive** - used to calibrate motor speed and limits

### Debug
Scripts used to test boat behavior
- **boatSim** - simulates how the boat moves in a virtual environment
