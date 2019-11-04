
#ifndef DISPLAY_H
#define DISPLAY_H

#include <LiquidCrystal.h>

#define DISP_RS 12
#define DISP_EN 11
#define DISP_D4 10
#define DISP_D5 9
#define DISP_D6 6
#define DISP_D7 5
#define DISP_BL 3

#define DISP_LENGTH 16
#define DISP_HEIGHT 2

#define DISP_BUFFER_SIZE  ((DISP_LENGTH*DISP_HEIGHT)+1)

enum DisplayState {
  SHOW_MESSAGE = 0,
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
  bool _changed;

  void _showMessage();
  void _showDisconnected();
  void _showStatus();

  void _clearBuffer();
  
};

#endif

