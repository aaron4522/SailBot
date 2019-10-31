#include <Arduino.h>

#include "display.h"

Display::Display() : _lcd(DISP_RS, DISP_EN, DISP_D4, DISP_D5, DISP_D6, DISP_D7){
  _state = DISCONNECTED;
  _clearBuffer();
}

bool Display::init(){

  //pinMode(DISP_BL, OUTPUT);
  _lcd.begin(DISP_LENGTH, DISP_HEIGHT);

  //digitalWrite(DISP_BL, LOW);
  _lcd.home();
  _lcd.display();
  return false;
}

void Display::setBacklight(int level){
  //TODO will be set to a pwm level eventually

  //digitalWrite(DISP_BL, level);
}

void Display::setState(DisplayState state){
  _state = state;
}

void Display::refresh(){
  _lcd.print(&_buffer[0]);
}

void Display::showMessage(String message){
  _lcd.clear();
  _lcd.print(message);
}

void Display::_clearBuffer(){
  memset(&_buffer[0], 0, DISP_BUFFER_SIZE);
}

/* eof */

