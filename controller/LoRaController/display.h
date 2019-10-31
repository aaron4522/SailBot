
#ifndef DISPLAY_H
#define DISPLAY_H

#include <LiquidCrystal.h>

#define DISP_RS 18
#define DISP_EN 19
#define DISP_D4 20
#define DISP_D5 21
#define DISP_D6 22
#define DISP_D7 23
#define DISP_BL 5

#define DISP_LENGTH 16
#define DISP_HEIGHT 2

#define DISP_BUFFER_SIZE  ((DISP_LENGTH*DISP_HEIGHT)+1)

enum DisplayState {
  SHOW_MESSAGE,
  DISCONNECTED,
  VIEW_STATUS,
};

class Display {
  public:
  Display();
  ~Display() {};

  bool init();

  void setBacklight(int level);
  void setState(DisplayState state);
  void refresh();
  void showMessage(String message);
    
  private:
  LiquidCrystal _lcd;
  char _buffer[DISP_BUFFER_SIZE];
  DisplayState _state;

  void _clearBuffer();
  
};

#endif

