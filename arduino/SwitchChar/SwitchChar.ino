// send on or off char when a digital switch changes value
// wiring: 3.3V -> switch -> 10k Ohm -> GND
//                       \-> D2
// ZKM | Hertz-Lab 2023
// Dan Wilcox <dan.wilcox@zkm.de>

const int SWITCH_PIN = 2;
const char SWITCH_CHAR_OFF = '0';
const char SWITCH_CHAR_ON = '1';

// previous button value
int pvalue = -1;

void setup() {
  Serial.begin(115200);
  pinMode(SWITCH_PIN, INPUT);
}

void loop() {
  int value = digitalRead(SWITCH_PIN);
  if(value != pvalue) {
    if(value == 1) {
      Serial.print(SWITCH_CHAR_ON);
    }
    else {
      Serial.print(SWITCH_CHAR_OFF);
    }
    pvalue = value;
  }
  delay(20);
}
