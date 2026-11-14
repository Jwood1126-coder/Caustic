// Caustic Bench Rig firmware
// Board: ESP32 DevKit V1 (Arduino board "DOIT ESP32 DEVKIT V1"), ESP32 Arduino core 3.x
//
// One DRV8833 drives both loads:
//   Channel A (AIN1/AIN2 -> AOUT1/AOUT2): speaker, through three 3 ohm resistors in series
//   Channel B (BIN1 -> BOUT1/BOUT2):      LED star, through one 3 ohm resistor. BIN2 is wired to GND.
//
// Both channels use 20 kHz PWM so nothing whines. The speaker gets a sine wave
// (PWM duty follows a sine), not a square wave, so the cone moves smoothly and quietly.
//
// Serial Monitor at 115200 baud, line ending "New Line". Commands:
//   led <0-100>               LED brightness, percent
//   amp <0-100>               speaker drive, percent
//   freq <hz>                 wave frequency, 0.5 to 40 Hz
//   sweep <from> <to> <sec>   glide the frequency from one value to another
//   stop                      speaker off (LED stays as set)
//   off                       speaker and LED off
//   status                    print the current settings

const int PIN_SPK_A = 25;  // DRV8833 AIN1 (IN1)
const int PIN_SPK_B = 26;  // DRV8833 AIN2 (IN2)
const int PIN_LED   = 27;  // DRV8833 BIN1 (IN3)

const int PWM_FREQ = 20000;
const int PWM_BITS = 10;
const int PWM_MAX  = (1 << PWM_BITS) - 1;

const int LED_START = 10;      // percent at power-up; the LED heats up fast
const float FREQ_START = 10.0; // Hz
const float FREQ_MIN = 0.5, FREQ_MAX = 40.0;

int ledPercent = LED_START;
int ampPercent = 0;  // speaker starts off
float freqHz = FREQ_START;

// sweep state
bool sweeping = false;
float sweepFrom, sweepTo;
unsigned long sweepStartMs, sweepMs;

float phase = 0;  // radians, accumulated so frequency changes never jump
unsigned long lastUs;

void applyLed() {
  ledcWrite(PIN_LED, ledPercent * PWM_MAX / 100);
}

void printStatus() {
  Serial.printf("led %d%%  amp %d%%  freq %.2f Hz%s\n", ledPercent, ampPercent, freqHz,
                sweeping ? "  (sweeping)" : "");
}

void handleLine(String s) {
  s.trim();
  s.toLowerCase();
  if (!s.length()) return;
  int sp = s.indexOf(' ');
  String cmd = sp < 0 ? s : s.substring(0, sp);
  String arg = sp < 0 ? "" : s.substring(sp + 1);

  if (cmd == "led") {
    ledPercent = constrain(arg.toInt(), 0, 100);
    applyLed();
  } else if (cmd == "amp") {
    ampPercent = constrain(arg.toInt(), 0, 100);
  } else if (cmd == "freq") {
    sweeping = false;
    freqHz = constrain(arg.toFloat(), FREQ_MIN, FREQ_MAX);
  } else if (cmd == "sweep") {
    float a, b, sec;
    if (sscanf(arg.c_str(), "%f %f %f", &a, &b, &sec) == 3 && sec > 0) {
      sweepFrom = constrain(a, FREQ_MIN, FREQ_MAX);
      sweepTo = constrain(b, FREQ_MIN, FREQ_MAX);
      sweepMs = (unsigned long)(sec * 1000);
      sweepStartMs = millis();
      sweeping = true;
    } else {
      Serial.println("usage: sweep <from Hz> <to Hz> <seconds>");
      return;
    }
  } else if (cmd == "stop") {
    ampPercent = 0;
    sweeping = false;
  } else if (cmd == "off") {
    ampPercent = 0;
    sweeping = false;
    ledPercent = 0;
    applyLed();
  } else if (cmd != "status") {
    Serial.println("commands: led, amp, freq, sweep, stop, off, status");
    return;
  }
  printStatus();
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);
  ledcAttach(PIN_SPK_A, PWM_FREQ, PWM_BITS);
  ledcAttach(PIN_SPK_B, PWM_FREQ, PWM_BITS);
  ledcAttach(PIN_LED, PWM_FREQ, PWM_BITS);
  ledcWrite(PIN_SPK_A, 0);
  ledcWrite(PIN_SPK_B, 0);
  applyLed();
  lastUs = micros();
  Serial.println("Caustic rig ready. Type: led 20, amp 30, freq 10, sweep 5 25 20, stop, off, status");
  printStatus();
}

void loop() {
  if (Serial.available()) handleLine(Serial.readStringUntil('\n'));

  if (sweeping) {
    unsigned long t = millis() - sweepStartMs;
    if (t >= sweepMs) {
      freqHz = sweepTo;
      sweeping = false;
      printStatus();
    } else {
      freqHz = sweepFrom + (sweepTo - sweepFrom) * (float)t / sweepMs;
    }
  }

  // Update the speaker waveform about every 0.5 ms.
  unsigned long now = micros();
  if (now - lastUs < 500) return;
  float dt = (now - lastUs) * 1e-6f;
  lastUs = now;

  phase += TWO_PI * freqHz * dt;
  if (phase > TWO_PI) phase -= TWO_PI;

  int duty = (int)(sinf(phase) * ampPercent * PWM_MAX / 100);
  // Positive half drives AIN1, negative half drives AIN2. The other input stays low.
  ledcWrite(PIN_SPK_A, duty > 0 ? duty : 0);
  ledcWrite(PIN_SPK_B, duty < 0 ? -duty : 0);
}
