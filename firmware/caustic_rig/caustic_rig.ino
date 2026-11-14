// Caustic Bench Rig firmware
// Board: ESP32 DevKit V1 (Arduino board "DOIT ESP32 DEVKIT V1"), ESP32 Arduino core 3.x
//
// One DRV8833 drives both loads:
//   Channel A (AIN1/AIN2 -> AOUT1/AOUT2): speaker (4 ohm 3 W), wired directly. SPK_LIMIT caps its current.
//   Channel B (BIN1 -> BOUT1/BOUT2):      LED star, through one 3 ohm resistor. BIN2 is wired to GND.
//
// Control it from a web page or the Serial Monitor.
//   Web: join the Wi-Fi network "Caustic-Rig" (password "causticrig") and open http://192.168.4.1
//        If you save your home Wi-Fi on the page, it is also at http://caustic.local on your network.
//   Serial (115200 baud, "New Line"): led <0-100>, amp <0-100>, freq <hz>,
//        sweep <from> <to> <sec>, stop, off, status

#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include "page.h"

const char *AP_SSID = "Caustic-Rig";
const char *AP_PASS = "causticrig";  // at least 8 characters
const char *HOSTNAME = "caustic";    // http://caustic.local

const int PIN_SPK_A = 25;  // DRV8833 AIN1 (IN1)
const int PIN_SPK_B = 26;  // DRV8833 AIN2 (IN2)
const int PIN_LED   = 27;  // DRV8833 BIN1 (IN3)

const int PWM_FREQ = 20000;
const int PWM_BITS = 10;
const int PWM_MAX  = (1 << PWM_BITS) - 1;

const int LED_START = 10;      // percent at power-up; the LED heats up fast
const float FREQ_START = 10.0; // Hz
const float FREQ_MIN = 0.5, FREQ_MAX = 40.0;

// The speaker has no series resistor, so 100% on the slider is limited to 40% PWM duty:
// about 0.46 A peak and under 0.5 W into the 4 ohm 3 W speaker.
const float SPK_LIMIT = 0.40;

int ledPercent = LED_START;
int ampPercent = 0;  // speaker starts off
float freqHz = FREQ_START;

bool sweeping = false;
float sweepFrom, sweepTo;
unsigned long sweepStartMs, sweepMs;

float phase = 0;  // radians, accumulated so frequency changes never jump
unsigned long lastUs;

WebServer server(80);
Preferences prefs;
String homeSsid;

// ---------- controls shared by serial and web ----------

void setLed(int p) {
  ledPercent = constrain(p, 0, 100);
  ledcWrite(PIN_LED, ledPercent * PWM_MAX / 100);
}

void setAmp(int p) { ampPercent = constrain(p, 0, 100); }

void setFreq(float f) {
  sweeping = false;
  freqHz = constrain(f, FREQ_MIN, FREQ_MAX);
}

void startSweep(float a, float b, float sec) {
  sweepFrom = constrain(a, FREQ_MIN, FREQ_MAX);
  sweepTo = constrain(b, FREQ_MIN, FREQ_MAX);
  sweepMs = (unsigned long)(sec * 1000);
  sweepStartMs = millis();
  sweeping = true;
}

void stopSpeaker() { ampPercent = 0; sweeping = false; }

void allOff() { stopSpeaker(); setLed(0); }

String statusJson() {
  String ip = WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString() : "";
  char buf[200];
  snprintf(buf, sizeof(buf),
           "{\"led\":%d,\"amp\":%d,\"freq\":%.2f,\"sweeping\":%s,\"home_ssid\":\"%s\",\"home_ip\":\"%s\"}",
           ledPercent, ampPercent, freqHz, sweeping ? "true" : "false", homeSsid.c_str(), ip.c_str());
  return String(buf);
}

void printStatus() {
  Serial.printf("led %d%%  amp %d%%  freq %.2f Hz%s\n", ledPercent, ampPercent, freqHz,
                sweeping ? "  (sweeping)" : "");
}

// ---------- serial ----------

void handleLine(String s) {
  s.trim();
  s.toLowerCase();
  if (!s.length()) return;
  int sp = s.indexOf(' ');
  String cmd = sp < 0 ? s : s.substring(0, sp);
  String arg = sp < 0 ? "" : s.substring(sp + 1);

  if (cmd == "led") setLed(arg.toInt());
  else if (cmd == "amp") setAmp(arg.toInt());
  else if (cmd == "freq") setFreq(arg.toFloat());
  else if (cmd == "sweep") {
    float a, b, sec;
    if (sscanf(arg.c_str(), "%f %f %f", &a, &b, &sec) == 3 && sec > 0) startSweep(a, b, sec);
    else { Serial.println("usage: sweep <from Hz> <to Hz> <seconds>"); return; }
  }
  else if (cmd == "stop") stopSpeaker();
  else if (cmd == "off") allOff();
  else if (cmd != "status") { Serial.println("commands: led, amp, freq, sweep, stop, off, status"); return; }
  printStatus();
}

// ---------- web ----------

void sendStatus() { server.send(200, "application/json", statusJson()); }

void setupWeb() {
  server.on("/", HTTP_GET, []() { server.send_P(200, "text/html", PAGE_HTML); });

  server.on("/api/status", HTTP_GET, sendStatus);

  server.on("/api/set", HTTP_POST, []() {
    if (server.hasArg("led")) setLed(server.arg("led").toInt());
    if (server.hasArg("amp")) setAmp(server.arg("amp").toInt());
    if (server.hasArg("freq")) setFreq(server.arg("freq").toFloat());
    sendStatus();
  });

  server.on("/api/sweep", HTTP_POST, []() {
    float sec = server.arg("sec").toFloat();
    if (sec <= 0) { server.send(400, "text/plain", "seconds must be above 0"); return; }
    startSweep(server.arg("from").toFloat(), server.arg("to").toFloat(), sec);
    sendStatus();
  });

  server.on("/api/stop", HTTP_POST, []() { stopSpeaker(); sendStatus(); });
  server.on("/api/off", HTTP_POST, []() { allOff(); sendStatus(); });

  server.on("/api/wifi", HTTP_POST, []() {
    prefs.putString("ssid", server.arg("ssid"));
    prefs.putString("pass", server.arg("pass"));
    server.send(200, "text/plain", "saved, restarting");
    delay(500);
    ESP.restart();
  });

  server.on("/api/wifi/forget", HTTP_POST, []() {
    prefs.remove("ssid");
    prefs.remove("pass");
    server.send(200, "text/plain", "forgotten, restarting");
    delay(500);
    ESP.restart();
  });

  server.onNotFound([]() { server.send(404, "text/plain", "not found"); });
  server.begin();
}

void setupWifi() {
  prefs.begin("caustic", false);
  homeSsid = prefs.getString("ssid", "");
  String homePass = prefs.getString("pass", "");

  WiFi.mode(WIFI_AP_STA);
  WiFi.setHostname(HOSTNAME);
  if (homeSsid.length()) {
    WiFi.begin(homeSsid.c_str(), homePass.c_str());
    Serial.printf("Joining home Wi-Fi \"%s\"", homeSsid.c_str());
    for (int i = 0; i < 20 && WiFi.status() != WL_CONNECTED; i++) { delay(500); Serial.print("."); }
    Serial.println();
    if (WiFi.status() == WL_CONNECTED)
      Serial.printf("Home Wi-Fi: http://%s.local or http://%s\n", HOSTNAME, WiFi.localIP().toString().c_str());
    else
      Serial.println("Could not join home Wi-Fi. The Caustic-Rig network still works.");
  }
  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.printf("Rig Wi-Fi: join \"%s\" (password %s), open http://%s\n", AP_SSID, AP_PASS,
                WiFi.softAPIP().toString().c_str());
  MDNS.begin(HOSTNAME);
  MDNS.addService("http", "tcp", 80);
}

// ---------- main ----------

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);
  ledcAttach(PIN_SPK_A, PWM_FREQ, PWM_BITS);
  ledcAttach(PIN_SPK_B, PWM_FREQ, PWM_BITS);
  ledcAttach(PIN_LED, PWM_FREQ, PWM_BITS);
  ledcWrite(PIN_SPK_A, 0);
  ledcWrite(PIN_SPK_B, 0);
  setLed(LED_START);

  setupWifi();
  setupWeb();

  lastUs = micros();
  Serial.println("Caustic rig ready. Type: led 20, amp 30, freq 10, sweep 5 25 20, stop, off, status");
  printStatus();
}

void loop() {
  server.handleClient();
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

  int duty = (int)(sinf(phase) * ampPercent * SPK_LIMIT * PWM_MAX / 100);
  // Positive half drives AIN1, negative half drives AIN2. The other input stays low.
  ledcWrite(PIN_SPK_A, duty > 0 ? duty : 0);
  ledcWrite(PIN_SPK_B, duty < 0 ? -duty : 0);
}
