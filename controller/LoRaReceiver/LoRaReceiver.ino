#include <SPI.h>
#include <RH_RF95.h>
#include <pb_encode.h>
#include <pb_decode.h>

#include "messages.pb.h"
#include "transceiver.h"

static Transceiver radio;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }
  
  radio.init();
}

void loop() {
  size_t bytesReceived = 0;
  if((bytesReceived = radio.tryReceive()) > 0){
    digitalWrite(LED_BUILTIN, HIGH);
    //Serial.write(&radio.inBuffer[0], bytesReceived);
    Serial.print((char*)radio.inBuffer);
    digitalWrite(LED_BUILTIN, LOW);
  }

}
