#include <SPI.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include <LiquidCrystal.h>

#include "messages.pb.h"
#include "display.h"
#include "transceiver.h"


enum Commands {
  SAIL_POSITION,
  RUDDER_POSITION,
  BOTH_POSITION,
  AUTONOMY_MODE,
};

// Singleton instance of the radio driver
//static RH_RF95 rf95(RFM95_CS, RFM95_INT);
static Transceiver radio;

static Display disp;

SkipperCommand skipper = SkipperCommand_init_zero;
SailCommand sail = SailCommand_init_zero;
RudderCommand rudder = RudderCommand_init_zero;
Mode autonomyMode = Mode_init_zero;


pb_ostream_t stream;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }

  disp.init();
  disp.showMessage("Initializing...");
  
  radio.init();
  
  stream = pb_ostream_from_buffer(radio.outBuffer, sizeof(radio.outBuffer));
}

bool transmitBuffer(){
  //rf95.send(outBuffer, stream.bytes_written);
}

/* Sets sail position in degrees. Transmits immediately */
void sailPos(int value){
  sail.position = value;

  //memset(outBuffer, 0, sizeof(outBuffer));
  pb_encode(&stream, SailCommand_fields, &sail);
  transmitBuffer();
}

/* Set rudder position in degrees. Transmits immediately */
void rudderPos(int value){
  rudder.position = value;
  
  //memset(&stream, 0, sizeof(outBuffer));
  pb_encode(&stream, RudderCommand_fields, &rudder);
  transmitBuffer();
}

/* Set sail and rudder positions in degrees. Transmits immediately */
void sailRudderPos(int sail, int rudder) {
  skipper.sailPosition = sail;
  skipper.rudderPosition = rudder;

  //memset(&stream, 0, sizeof(outBuffer));
  pb_encode(&stream, SkipperCommand_fields, &skipper);
  transmitBuffer();
}

int led_state = 0;

void loop() {
  if(Serial.available()){
    // command from PC precedes controller input
    // relay data to transmitter
  }
  else{
    // controller input
    
  }

  /*if(rf95.available()){
    led_state = (led_state+1)%2;
    digitalWrite(LED_BUILTIN, led_state);
    // relay received data
    // decode locally for LCD
  }
  else {
    led_state = 0;
    digitalWrite(LED_BUILTIN, led_state);
  }*/

}
