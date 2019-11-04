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
  _changed = true;
}

void Display::refresh(){
  if(!_changed)
    return;
  
  switch(_state){
    case DisplayState::SHOW_MESSAGE:
      _showMessage();
      break;
    case DisplayState::DISCONNECTED:
      _showDisconnected();
      break;
    case DisplayState::VIEW_STATUS:
      _showStatus();
      break;
  }
  _lcd.clear();
  _lcd.print(&_buffer[0]);
  _changed = false;
}

void Display::showMessage(String message){
  _lcd.clear();
  _lcd.print(message);
}

void Display::_showMessage(){
  
}

void Display::_showDisconnected(){
  _clearBuffer();
  strcpy(&_buffer[0], "Disconnected");
}

void Display::_showStatus(){
  
}

void Display::_clearBuffer(){
  memset(&_buffer[0], 0, DISP_BUFFER_SIZE);
}

/* eof */

