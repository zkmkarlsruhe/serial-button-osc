// press a key when a digital switch changes value
// wiring: 3.3V -> switch -> 10k Ohm -> GND
//                       \-> D2
// ZKM | Hertz-Lab 2023
// Dan Wilcox <dan.wilcox@zkm.de>

#include <Keyboard.h>

const int SWITCH_PIN = 2;
const char SWITCH_CHAR = KEY_ESC;

// previous button value
int pvalue = -1;

void setup() {
  pinMode(SWITCH_PIN, INPUT);
  Keyboard.begin();
}

void loop() {
  int value = digitalRead(SWITCH_PIN);
  if(value != pvalue) {
    if(value == 1) {
      Keyboard.press(SWITCH_CHAR);
    }
    else {
      Keyboard.release(SWITCH_CHAR);
    }
    pvalue = value;
  }
  delay(20);
}
