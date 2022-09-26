#include <Wire.h>

# define I2C_SLAVE_ADDRESS 0x10 // 12 pour l'esclave 2 et ainsi de suite

void setup()
{
  Wire.begin(I2C_SLAVE_ADDRESS);             
  Wire.onRequest(requestEvents);
  Wire.onReceive(receiveEvents);
}

void loop(){}

int n = 5;

void requestEvents()
{
  Wire.write("heelo from Ardu");
}

void receiveEvents(int numBytes)
{  
if ( Wire.available() ){
}
  
}
