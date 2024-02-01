#include <IcsSoftSerialClass.h>

const byte S_RX_PIN = 8;
const byte S_TX_PIN = 9;
const byte EN_PIN = 2;
const long BAUDRATE = 115200;
const int TIMEOUT = 200;
const int MAX_SERVOS = 8; // Set the maximum number of servos here

IcsSoftSerialClass krs(S_RX_PIN, S_TX_PIN, EN_PIN, BAUDRATE, TIMEOUT);
int servoAngles[MAX_SERVOS];

void setup() {
  krs.begin();
  Serial.begin(9600);
  Serial.setTimeout(1);
  for (int i = 0; i < MAX_SERVOS; i++) {
    servoAngles[i] = 7500; // Default position for all servos
  }
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n'); // Read the entire line
    int start = 0;
    int end = data.indexOf(',');

    for (int i = 0; i < MAX_SERVOS; i++) {
      if (end == -1) {
        end = data.length();
      }

      String angleString = data.substring(start, end);
      servoAngles[i] = angleString.toInt();
      krs.setPos(i, servoAngles[i]); // Set position for each servo
      krs.setSpd(i, 40);

      start = end + 1;
      end = data.indexOf(',', start);
    }
  }
 delay(500);// Adjust delay as needed
}