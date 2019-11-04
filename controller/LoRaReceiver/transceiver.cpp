#include <Arduino.h>
#include "transceiver.h"

bool Transceiver::init(){
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  delay(100);

  //Serial.println("Feather LoRa TX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!_rf95.init()) {
    //Serial.println("LoRa radio init failed");
    //Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    //while (1);
    return true;
  }
  //Serial.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!_rf95.setFrequency(RF95_FREQ)) {
    //Serial.println("setFrequency failed");
    //while (1);
    return true;
  }
  //Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);
  
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  _rf95.setTxPower(23, false);

  memset(outBuffer, 0, OUT_BUFFER_SIZE);
  memset(inBuffer, 0, IN_BUFFER_SIZE);

  digitalWrite(LED_BUILTIN, LOW);
}

bool Transceiver::transmit(size_t amount){
  if(amount > OUT_BUFFER_SIZE)
    return true;

  digitalWrite(LED_BUILTIN, HIGH);
  _rf95.send(&outBuffer[0], amount);
  digitalWrite(LED_BUILTIN, LOW);

  return false;
}

size_t Transceiver::tryReceive(){
  if(!_rf95.waitAvailableTimeout(3000))
    return 0;

  digitalWrite(LED_BUILTIN, HIGH);

  uint8_t bytesTransferred = IN_BUFFER_SIZE;
  if(!_rf95.recv(&inBuffer[0], &bytesTransferred))
    return 0;

  Serial.println(bytesTransferred);

  digitalWrite(LED_BUILTIN, LOW);

  return bytesTransferred;
}

/* eof */
