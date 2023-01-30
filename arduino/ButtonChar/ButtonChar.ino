// send a single char on a digital button press
// note: matches original button from ZKM Video Studio
// wiring: 3.3V -> button -> 10k Ohm -> GND
//                       \-> D2
// ZKM | Hertz-Lab 2023
// Dan Wilcox <dan.wilcox@zkm.de>

const int BUTTON_PIN = 2;
const char BUTTON_CHAR = '3';

// previous button value
int pvalue = -1;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT);
}

void loop() {
  int value = digitalRead(BUTTON_PIN);
  if(value != pvalue) {
    if(value == 1) {
      Serial.print(BUTTON_CHAR);
    }
    pvalue = value;
  }
  delay(20);
}
