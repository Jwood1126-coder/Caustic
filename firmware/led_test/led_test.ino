// Caustic Bench Rig - LED bench test
// ESP32 DevKit V1 -> DRV8833 channel B -> 3 ohm resistor -> LED star
// Open Serial Monitor at 115200 baud, type 0-100 and press Enter to set brightness in percent.

const int LED_PIN = 27;        // to DRV8833 BIN1 (IN3). BIN2 (IN4) is wired to GND.
const int PWM_FREQ = 20000;    // 20 kHz, above hearing
const int PWM_BITS = 10;       // duty 0..1023
const int START_PERCENT = 10;  // start dim: the LED heats up fast

int percent = START_PERCENT;

void setPercent(int p) {
  percent = constrain(p, 0, 100);
  ledcWrite(LED_PIN, (percent * ((1 << PWM_BITS) - 1)) / 100);
  Serial.printf("LED %d%%\n", percent);
}

void setup() {
  Serial.begin(115200);
  ledcAttach(LED_PIN, PWM_FREQ, PWM_BITS);
  setPercent(START_PERCENT);
  Serial.println("Type 0-100 and press Enter to set LED brightness.");
}

void loop() {
  if (Serial.available()) {
    String s = Serial.readStringUntil('\n');
    s.trim();
    if (s.length()) setPercent(s.toInt());
  }
}
