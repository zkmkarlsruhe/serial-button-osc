// two buttons and two chars
// wiring: 5V -> button1 -> 10k Ohm -> GND
//                      \-> D2
//         5V -> button2 -> 10k Ohm -> GND
//                      \-> D3
// ZKM | Hertz-Lab 2025
// Dan Wilcox <dan.wilcox@zkm.de>

const int BUTTON_PIN1 = 2;
const char BUTTON_CHAR1 = '1';
const int BUTTON_PIN2 = 3;
const char BUTTON_CHAR2 = '2';

// previous button value
int pvalue1 = -1;
int pvalue2 = -1;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN1, INPUT);
  pinMode(BUTTON_PIN2, INPUT);
  Serial.print(BUTTON_CHAR1);
  Serial.print(BUTTON_CHAR2);
}

void loop() {
  int value1 = digitalRead(BUTTON_PIN1);
  if(value1 != pvalue1) {
    if(value1 == 1) {
      Serial.print(BUTTON_CHAR1);
    }
    pvalue1 = value1;
  }
  int value2 = digitalRead(BUTTON_PIN2);
  if(value2 != pvalue2) {
    if(value2 == 1) {
      Serial.print(BUTTON_CHAR2);
    }
    pvalue2 = value2;
  }
  delay(20);
}
