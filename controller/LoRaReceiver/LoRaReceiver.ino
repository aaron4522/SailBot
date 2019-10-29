#include <SPI.h>
#include <RH_RF95.h>
#include <pb_encode.h>
#include <pb_decode.h>

#include "messages.pb.h"

// for feather32u4 
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 7

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

enum Commands {
  SAIL_POSITION,
  RUDDER_POSITION,
  BOTH_POSITION,
  AUTONOMY_MODE,
};

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

SkipperCommand skipper = SkipperCommand_init_zero;
SailCommand sail = SailCommand_init_zero;
RudderCommand rudder = RudderCommand_init_zero;
Mode autonomyMode = Mode_init_zero;

#define OUT_BUFFER_LENGTH 256
uint8_t outBuffer[OUT_BUFFER_LENGTH];
pb_ostream_t stream;

void setup() {
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }

  delay(100);

  Serial.println("Feather LoRa TX Test!");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    while (1);
  }
  Serial.println("LoRa radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);
  
  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);

  memset(outBuffer, 0, sizeof(outBuffer));
  stream = pb_ostream_from_buffer(outBuffer, sizeof(outBuffer));
}

void loop() {
  if(rf95.available()){
    
  }

}
