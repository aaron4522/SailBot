#include <SPI.h>
#include <pb_encode.h>
#include <pb_decode.h>
#include <LiquidCrystal.h>
#include <PS2X_lib.h>

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

BaseToBoat messageOut = BaseToBoat_init_zero;
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
  return radio.transmit(stream.bytes_written);
}

/* Sets sail position in degrees. Transmits immediately */
void sailPos(int value){
  sail.position = value;
  messageOut.command.sail = sail;
  messageOut.which_command = BaseToBoat_sail_tag;

  //memset(outBuffer, 0, sizeof(outBuffer));
  pb_encode(&stream, BaseToBoat_fields, &messageOut);
  transmitBuffer();
}

/* Set rudder position in degrees. Transmits immediately */
void rudderPos(int value){
  rudder.position = value;
  messageOut.command.rudder = rudder;
  messageOut.which_command = BaseToBoat_rudder_tag;
  
  //memset(&stream, 0, sizeof(outBuffer));
  pb_encode(&stream, BaseToBoat_fields, &messageOut);
  transmitBuffer();
}

/* Set sail and rudder positions in degrees. Transmits immediately */
void sailRudderPos(int sail, int rudder) {
  skipper.sailPosition = sail;
  skipper.rudderPosition = rudder;

  messageOut.command.skipper = skipper;
  messageOut.which_command = BaseToBoat_skipper_tag;

  //memset(&stream, 0, sizeof(outBuffer));
  pb_encode(&stream, BaseToBoat_fields, &messageOut);
  transmitBuffer();
}

int led_state = 0;

void loop() {
  disp.setState(DisplayState::DISCONNECTED);
  disp.refresh();

  size_t bytesReceived = 0;
  while(Serial.available()){
    digitalWrite(LED_BUILTIN, led_state);
    //size_t num = Serial.readBytes(&radio.outBuffer[bytesReceived], (OUT_BUFFER_SIZE - bytesReceived));
    radio.outBuffer[bytesReceived] = Serial.read();
    //bytesReceived += num;
    bytesReceived++;
    if(bytesReceived >= OUT_BUFFER_SIZE)
      break;
    led_state = (led_state+1)%2;
  }
  if(bytesReceived > 0)
    radio.transmit(bytesReceived);

  /* code for reading PS2 contoller here */

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
